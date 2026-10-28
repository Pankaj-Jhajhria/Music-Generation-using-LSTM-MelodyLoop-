"""
MelodyLoop Training Script.
Trains the LSTM on quantized next-note prediction from MAESTRO MIDI performances.
Supports resuming, checkpointing, CLI overrides, and background execution.
"""

import argparse
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Any, Tuple

import torch
from torch.utils.data import DataLoader

from config import Config
from melodyloop.data import load_maestro_split
from melodyloop.model import MelodyLSTM


def setup_logger(log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("MelodyLoop")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    fh = logging.FileHandler(str(log_file), mode="a", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


def save_checkpoint(
    path: Path,
    model: MelodyLSTM,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    train_loss: float,
    val_loss: float,
    metrics: Dict[str, float],
    cfg: Config,
):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Convert config dataclass to dict safely
    cfg_dict = {
        k: getattr(cfg, k)
        for k in dir(cfg)
        if not k.startswith("_") and not callable(getattr(cfg, k))
    }
    # Convert Path objects to strings for serialization
    for k, v in cfg_dict.items():
        if isinstance(v, Path):
            cfg_dict[k] = str(v)

    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "train_loss": train_loss,
            "val_loss": val_loss,
            "metrics": metrics,
            "config": cfg_dict,
            "timestamp": time.time(),
        },
        str(path),
    )


def train_one_epoch(
    model: MelodyLSTM,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    logger: logging.Logger,
    epoch: int,
    log_interval: int = 50,
) -> float:
    model.train()
    total_loss = 0.0
    num_batches = len(loader)

    for batch_idx, batch in enumerate(loader):
        x = batch["x"].to(device, non_blocking=True)
        t_p = batch["pitch"].to(device, non_blocking=True)
        t_d = batch["duration"].to(device, non_blocking=True)
        t_s = batch["step"].to(device, non_blocking=True)

        optimizer.zero_grad()
        logits_p, logits_d, logits_s, _ = model(x)
        loss, _ = model.compute_loss(logits_p, logits_d, logits_s, t_p, t_d, t_s)

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item()

        if (batch_idx + 1) % log_interval == 0 or (batch_idx + 1) == num_batches:
            avg_so_far = total_loss / (batch_idx + 1)
            logger.info(
                f"Epoch {epoch:02d} [{batch_idx + 1:04d}/{num_batches:04d}] "
                f"Batch Loss: {loss.item():.4f} | Running Avg: {avg_so_far:.4f}"
            )
            sys.stdout.flush()

    return total_loss / max(num_batches, 1)


@torch.no_grad()
def evaluate(
    model: MelodyLSTM,
    loader: DataLoader,
    device: torch.device,
) -> Tuple[float, Dict[str, float]]:
    model.eval()
    total_loss = 0.0
    sum_p = 0.0
    sum_d = 0.0
    sum_s = 0.0
    num_batches = len(loader)

    if num_batches == 0:
        return 0.0, {}

    for batch in loader:
        x = batch["x"].to(device, non_blocking=True)
        t_p = batch["pitch"].to(device, non_blocking=True)
        t_d = batch["duration"].to(device, non_blocking=True)
        t_s = batch["step"].to(device, non_blocking=True)

        logits_p, logits_d, logits_s, _ = model(x)
        loss, metrics = model.compute_loss(logits_p, logits_d, logits_s, t_p, t_d, t_s)

        total_loss += loss.item()
        sum_p += metrics["loss_pitch"]
        sum_d += metrics["loss_dur"]
        sum_s += metrics["loss_step"]

    avg_loss = total_loss / num_batches
    metrics = {
        "val_loss": avg_loss,
        "val_loss_pitch": sum_p / num_batches,
        "val_loss_dur": sum_d / num_batches,
        "val_loss_step": sum_s / num_batches,
    }
    return avg_loss, metrics


def main():
    parser = argparse.ArgumentParser(description="MelodyLoop LSTM Trainer")
    parser.add_argument("--epochs", type=int, default=None, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=None, help="Batch size")
    parser.add_argument("--lr", type=float, default=None, help="Learning rate")
    parser.add_argument("--hidden-dim", type=int, default=None, help="LSTM hidden dimension")
    parser.add_argument("--max-files", type=int, default=None, help="Max train files to read")
    parser.add_argument("--max-sequences", type=int, default=None, help="Max training sequences")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda or cpu)")
    parser.add_argument("--resume", action="store_true", help="Resume from latest checkpoint")
    parser.add_argument("--smoke-test", action="store_true", help="Fast 1-epoch smoke test")
    parser.add_argument("--patience", type=int, default=6, help="Early stopping patience (epochs without val improvement)")
    parser.add_argument("--log-file", type=str, default=None, help="Path to log file")
    parser.add_argument("--best-checkpoint", type=str, default=None, help="Path to save best checkpoint")
    parser.add_argument("--latest-checkpoint", type=str, default=None, help="Path to save latest checkpoint")
    parser.add_argument("--no-alias", action="store_true", help="Do not mirror to best_model.pt")

    args = parser.parse_args()

    cfg = Config()
    if args.smoke_test:
        cfg.epochs = 1
        cfg.max_train_files = 2
        cfg.max_val_files = 1
        cfg.max_train_sequences = 128
        cfg.max_val_sequences = 32
        cfg.batch_size = 16

    if args.epochs is not None:
        cfg.epochs = args.epochs
    if args.batch_size is not None:
        cfg.batch_size = args.batch_size
    if args.lr is not None:
        cfg.learning_rate = args.lr
    if args.hidden_dim is not None:
        cfg.hidden_dim = args.hidden_dim
    if args.max_files is not None:
        cfg.max_train_files = args.max_files
    if args.max_sequences is not None:
        cfg.max_train_sequences = args.max_sequences
    if args.device is not None:
        cfg.device = args.device

    best_ckpt_path = Path(args.best_checkpoint) if args.best_checkpoint else (cfg.artifacts_dir / "checkpoints" / "best_model_expanded.pt")
    latest_ckpt_path = Path(args.latest_checkpoint) if args.latest_checkpoint else (cfg.artifacts_dir / "checkpoints" / "latest_model_expanded.pt")

    log_path = Path(args.log_file) if args.log_file else (cfg.logs_dir / "training_expanded.log")
    logger = setup_logger(log_path)

    torch.manual_seed(cfg.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(cfg.seed)

    device = torch.device(cfg.device)
    logger.info("=" * 60)
    logger.info("MelodyLoop -- LSTM Music Generation Trainer")
    logger.info("=" * 60)
    logger.info(f"Target Device: {cfg.device.upper()}")
    if cfg.device == "cuda" and torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"Allocated VRAM: {torch.cuda.memory_allocated() / (1024**2):.1f} MB")
    logger.info(f"Training Config: epochs={cfg.epochs}, batch_size={cfg.batch_size}, lr={cfg.learning_rate}")
    logger.info(f"Model Architecture: hidden_dim={cfg.hidden_dim}, seq_len={cfg.seq_length}")
    logger.info(f"Data Limits: max_train_files={cfg.max_train_files}, max_sequences={cfg.max_train_sequences}")

    # Load splits
    logger.info("Loading MAESTRO training split...")
    t0 = time.time()
    train_dataset, train_stats = load_maestro_split(
        "train", cfg, max_files=cfg.max_train_files, max_sequences=cfg.max_train_sequences
    )
    logger.info(
        f"Train data loaded in {time.time() - t0:.2f}s: {train_stats['files_processed']} files, "
        f"{train_stats['total_notes']} notes, {len(train_dataset)} sequences."
    )

    logger.info("Loading MAESTRO validation split...")
    val_dataset, val_stats = load_maestro_split(
        "validation", cfg, max_files=cfg.max_val_files, max_sequences=cfg.max_val_sequences
    )
    logger.info(
        f"Val data loaded: {val_stats['files_processed']} files, "
        f"{val_stats['total_notes']} notes, {len(val_dataset)} sequences."
    )

    if len(train_dataset) == 0:
        logger.error("No training sequences extracted! Please check dataset path.")
        sys.exit(1)

    pin = (cfg.device == "cuda")
    train_loader = DataLoader(
        train_dataset,
        batch_size=cfg.batch_size,
        shuffle=True,
        pin_memory=pin,
        drop_last=(len(train_dataset) > cfg.batch_size),
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=cfg.batch_size,
        shuffle=False,
        pin_memory=pin,
    )

    model = MelodyLSTM(cfg).to(device)
    logger.info(f"Model instantiated with {model.count_parameters():,} trainable parameters.")

    optimizer = torch.optim.Adam(
        model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay
    )

    start_epoch = 1
    best_val_loss = float("inf")
    patience_counter = 0

    # Resume support
    resume_target = latest_ckpt_path if latest_ckpt_path.exists() else (cfg.latest_model_path if cfg.latest_model_path.exists() else None)
    if args.resume and resume_target is not None:
        logger.info(f"Found checkpoint at {resume_target}. Resuming...")
        ckpt = torch.load(str(resume_target), map_location=device)
        model.load_state_dict(ckpt["model_state_dict"])
        optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        start_epoch = ckpt["epoch"] + 1
        best_val_loss = ckpt.get("val_loss", float("inf"))
        logger.info(f"Resumed from epoch {ckpt['epoch']} (previous val_loss: {best_val_loss:.4f})")

    # Graceful exit handling
    interrupted = False

    def handle_interrupt(signum, frame):
        nonlocal interrupted
        logger.warning("\nInterrupt received! Saving checkpoint before exit...")
        interrupted = True

    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)

    logger.info("-" * 60)
    logger.info(f"Starting training run (epochs {start_epoch} to {cfg.epochs})...")
    logger.info("-" * 60)

    for epoch in range(start_epoch, cfg.epochs + 1):
        if interrupted:
            break

        ep_start = time.time()
        train_loss = train_one_epoch(
            model, train_loader, optimizer, device, logger, epoch
        )
        val_loss, val_metrics = evaluate(model, val_loader, device)
        elapsed = time.time() - ep_start

        logger.info(
            f"=== Epoch {epoch:02d}/{cfg.epochs:02d} Summary [{elapsed:.1f}s] ==="
        )
        logger.info(
            f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} "
            f"(P: {val_metrics.get('val_loss_pitch', 0):.3f}, "
            f"D: {val_metrics.get('val_loss_dur', 0):.3f}, "
            f"S: {val_metrics.get('val_loss_step', 0):.3f})"
        )

        # Always save latest
        save_checkpoint(
            latest_ckpt_path,
            model,
            optimizer,
            epoch,
            train_loss,
            val_loss,
            val_metrics,
            cfg,
        )
        if not args.no_alias and latest_ckpt_path != cfg.latest_model_path:
            save_checkpoint(
                cfg.latest_model_path,
                model,
                optimizer,
                epoch,
                train_loss,
                val_loss,
                val_metrics,
                cfg,
            )
        logger.info(f"Saved checkpoint -> {latest_ckpt_path.name}")

        # Check best
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            save_checkpoint(
                best_ckpt_path,
                model,
                optimizer,
                epoch,
                train_loss,
                val_loss,
                val_metrics,
                cfg,
            )
            if not args.no_alias and best_ckpt_path != cfg.best_model_path:
                save_checkpoint(
                    cfg.best_model_path,
                    model,
                    optimizer,
                    epoch,
                    train_loss,
                    val_loss,
                    val_metrics,
                    cfg,
                )
            logger.info(f"* New best model achieved (val_loss: {best_val_loss:.4f}) -> {best_ckpt_path.name}")
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                logger.info(
                    f"\n! Early stopping triggered: Validation loss has not improved for {args.patience} consecutive epochs."
                )
                break

        logger.info("-" * 60)
        sys.stdout.flush()

    logger.info("Training loop completed successfully.")
    logger.info(f"Best Validation Loss: {best_val_loss:.4f}")
    logger.info(f"Final checkpoint location: {best_ckpt_path}")


if __name__ == "__main__":
    main()
