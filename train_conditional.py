"""
Training script for MelodyLoop 2.0: Condition-Aware LSTM.
Trains from scratch on filtered MidiCaps solo piano sequences with condition embedding.
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from config import Config
from melodyloop.conditional_data import (
    build_or_load_conditional_dataset,
    ConditionalMelodyDataset,
    MOOD_VOCAB,
    TEMPO_VOCAB,
    REGISTER_VOCAB,
    DYNAMICS_VOCAB,
)
from melodyloop.conditional_model import ConditionalMelodyLSTM


def setup_logging(log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("train_conditional")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Formatter
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File Handler
    fh = logging.FileHandler(str(log_file), mode="w", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


def train_one_epoch(
    model: ConditionalMelodyLSTM,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    logger: logging.Logger,
    epoch: int,
    total_epochs: int,
) -> dict:
    model.train()
    total_loss = 0.0
    sum_lp = 0.0
    sum_ld = 0.0
    sum_ls = 0.0
    sum_lv = 0.0
    count = 0

    t0 = time.time()
    for batch_idx, batch in enumerate(loader):
        x = batch["x"].to(device, non_blocking=True)
        cond = batch["cond"].to(device, non_blocking=True)
        yp = batch["pitch"].to(device, non_blocking=True)
        yd = batch["duration"].to(device, non_blocking=True)
        ys = batch["step"].to(device, non_blocking=True)
        yv = batch["velocity"].to(device, non_blocking=True)

        optimizer.zero_grad()
        lp, ld, ls, lv, _ = model(x, cond)

        loss, metrics = model.compute_loss(lp, ld, ls, lv, yp, yd, ys, yv)
        loss.backward()

        # Gradient clipping for LSTM stability
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
        optimizer.step()

        b_size = x.size(0)
        total_loss += metrics["loss_total"] * b_size
        sum_lp += metrics["loss_pitch"] * b_size
        sum_ld += metrics["loss_dur"] * b_size
        sum_ls += metrics["loss_step"] * b_size
        sum_lv += metrics["loss_vel"] * b_size
        count += b_size

        if (batch_idx + 1) % 150 == 0 or (batch_idx + 1) == len(loader):
            elapsed = time.time() - t0
            throughput = count / max(elapsed, 1e-4)
            logger.info(
                f"Epoch [{epoch}/{total_epochs}] Step [{batch_idx+1}/{len(loader)}] - "
                f"Loss: {total_loss/count:.4f} (p:{sum_lp/count:.3f}, d:{sum_ld/count:.3f}, "
                f"s:{sum_ls/count:.3f}, v:{sum_lv/count:.3f}) - {throughput:.1f} seqs/s"
            )

    return {
        "train_loss": total_loss / max(count, 1),
        "train_loss_pitch": sum_lp / max(count, 1),
        "train_loss_dur": sum_ld / max(count, 1),
        "train_loss_step": sum_ls / max(count, 1),
        "train_loss_vel": sum_lv / max(count, 1),
    }


def evaluate(
    model: ConditionalMelodyLSTM,
    loader: DataLoader,
    device: torch.device,
) -> dict:
    model.eval()
    total_loss = 0.0
    sum_lp = 0.0
    sum_ld = 0.0
    sum_ls = 0.0
    sum_lv = 0.0
    count = 0

    with torch.no_grad():
        for batch in loader:
            x = batch["x"].to(device, non_blocking=True)
            cond = batch["cond"].to(device, non_blocking=True)
            yp = batch["pitch"].to(device, non_blocking=True)
            yd = batch["duration"].to(device, non_blocking=True)
            ys = batch["step"].to(device, non_blocking=True)
            yv = batch["velocity"].to(device, non_blocking=True)

            lp, ld, ls, lv, _ = model(x, cond)
            _, metrics = model.compute_loss(lp, ld, ls, lv, yp, yd, ys, yv)

            b_size = x.size(0)
            total_loss += metrics["loss_total"] * b_size
            sum_lp += metrics["loss_pitch"] * b_size
            sum_ld += metrics["loss_dur"] * b_size
            sum_ls += metrics["loss_step"] * b_size
            sum_lv += metrics["loss_vel"] * b_size
            count += b_size

    return {
        "val_loss": total_loss / max(count, 1),
        "val_loss_pitch": sum_lp / max(count, 1),
        "val_loss_dur": sum_ld / max(count, 1),
        "val_loss_step": sum_ls / max(count, 1),
        "val_loss_vel": sum_lv / max(count, 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Train Conditional MelodyLoop LSTM")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--max_train_seqs", type=int, default=50000, help="Sequence budget for training")
    parser.add_argument("--max_val_seqs", type=int, default=5000, help="Sequence budget for validation")
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cuda", "cpu"])
    parser.add_argument("--smoke_test", action="store_true", help="Run 1 epoch smoke test")
    parser.add_argument("--force_rebuild_cache", action="store_true", help="Rebuild dataset cache")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    cfg = Config()
    cfg.seed = args.seed
    torch.manual_seed(cfg.seed)
    np.random.seed(cfg.seed)

    # Output paths
    checkpoints_dir = cfg.checkpoints_dir / "conditional"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    best_ckpt_path = checkpoints_dir / "best_conditional_model.pt"
    latest_ckpt_path = checkpoints_dir / "latest_conditional_model.pt"
    log_file = cfg.logs_dir / "conditional_training.log"
    history_file = cfg.logs_dir / "conditional_training_history.json"

    logger = setup_logging(log_file)
    logger.info("=" * 65)
    logger.info("MelodyLoop 2.0: Condition-Aware LSTM Training")
    logger.info("=" * 65)

    # Hardware detection
    if args.device == "auto":
        dev_str = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        dev_str = args.device
    device = torch.device(dev_str)
    logger.info(f"Using device: {device}")
    if dev_str == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}, VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

    # Load / Build dataset
    max_train = 500 if args.smoke_test else args.max_train_seqs
    max_val = 100 if args.smoke_test else args.max_val_seqs
    epochs = 1 if args.smoke_test else args.epochs

    train_ds, val_ds, meta = build_or_load_conditional_dataset(
        cfg=cfg,
        max_train_sequences=max_train,
        max_val_sequences=max_val,
        force_rebuild=args.force_rebuild_cache,
    )
    logger.info(f"Active training sequences: {len(train_ds):,}")
    logger.info(f"Active validation sequences: {len(val_ds):,}")

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=True,
        num_workers=0,  # Windows-friendly zero worker process overhead
        pin_memory=(dev_str == "cuda"),
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=(dev_str == "cuda"),
    )

    # Initialize model
    model = ConditionalMelodyLSTM(
        cfg=cfg,
        velocity_bins=16,
        mood_vocab_size=len(MOOD_VOCAB),
        tempo_vocab_size=len(TEMPO_VOCAB),
        register_vocab_size=len(REGISTER_VOCAB),
        dynamics_vocab_size=len(DYNAMICS_VOCAB),
    ).to(device)

    total_params = model.get_parameter_count()
    logger.info(f"Initialized ConditionalMelodyLSTM with {total_params:,} trainable parameters.")
    logger.info(f"Event embedding: 144, Condition embedding: 40, LSTM input dim: {model.input_dim}, Hidden dim: {cfg.hidden_dim}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=2, min_lr=1e-5
    )

    best_val_loss = float("inf")
    history = []
    start_time = time.time()

    try:
        for epoch in range(1, epochs + 1):
            ep_start = time.time()
            train_metrics = train_one_epoch(
                model=model,
                loader=train_loader,
                optimizer=optimizer,
                device=device,
                logger=logger,
                epoch=epoch,
                total_epochs=epochs,
            )

            val_metrics = evaluate(model=model, loader=val_loader, device=device)
            ep_time = time.time() - ep_start
            current_lr = optimizer.param_groups[0]["lr"]

            logger.info(
                f"[Epoch {epoch:02d}/{epochs:02d}] finished in {ep_time:.1f}s | "
                f"Train Loss: {train_metrics['train_loss']:.4f} | "
                f"Val Loss: {val_metrics['val_loss']:.4f} (p:{val_metrics['val_loss_pitch']:.3f}, "
                f"d:{val_metrics['val_loss_dur']:.3f}, s:{val_metrics['val_loss_step']:.3f}, "
                f"v:{val_metrics['val_loss_vel']:.3f}) | LR: {current_lr:.6f}"
            )

            scheduler.step(val_metrics["val_loss"])

            # Save latest checkpoint
            checkpoint_data = {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "train_loss": train_metrics["train_loss"],
                "val_loss": val_metrics["val_loss"],
                "metrics": {**train_metrics, **val_metrics},
                "cfg": cfg,
                "dataset_meta": meta,
                "model_config": {
                    "velocity_bins": 16,
                    "mood_vocab": MOOD_VOCAB,
                    "tempo_vocab": TEMPO_VOCAB,
                    "register_vocab": REGISTER_VOCAB,
                    "dynamics_vocab": DYNAMICS_VOCAB,
                    "hidden_dim": cfg.hidden_dim,
                    "num_layers": cfg.num_layers,
                    "params": total_params,
                },
            }
            torch.save(checkpoint_data, str(latest_ckpt_path))

            # Check for best checkpoint
            if val_metrics["val_loss"] < best_val_loss:
                improvement = best_val_loss - val_metrics["val_loss"]
                best_val_loss = val_metrics["val_loss"]
                torch.save(checkpoint_data, str(best_ckpt_path))
                logger.info(f"--> Saved new BEST checkpoint to {best_ckpt_path} (improved by {improvement:.4f})")

            epoch_record = {
                "epoch": epoch,
                "time_sec": ep_time,
                "lr": current_lr,
                **train_metrics,
                **val_metrics,
            }
            history.append(epoch_record)
            with open(history_file, "w", encoding="utf-8") as hf:
                json.dump(history, hf, indent=2)

    except KeyboardInterrupt:
        logger.warning("Training interrupted by user. Saved latest checkpoint and history.")

    total_training_time = time.time() - start_time
    logger.info("=" * 65)
    logger.info(f"Training session ended in {total_training_time/60:.2f} minutes.")
    logger.info(f"Best Validation Loss: {best_val_loss:.4f}")
    logger.info(f"Best Checkpoint: {best_ckpt_path}")
    logger.info("=" * 65)


if __name__ == "__main__":
    main()
