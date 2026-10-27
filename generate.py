"""
CLI generation script for MelodyLoop.
Generates new music using a trained LSTM checkpoint and exports both MIDI and WAV.
"""

import argparse
from pathlib import Path
import sys
import torch

from config import Config
from melodyloop.audio import synthesize_notes_to_wav
from melodyloop.generation import generate_melody, export_notes_to_midi
from melodyloop.model import MelodyLSTM


def main():
    parser = argparse.ArgumentParser(description="MelodyLoop Music Generation")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to model checkpoint .pt")
    parser.add_argument("--length", type=int, default=100, help="Number of notes to generate")
    parser.add_argument("--temperature", type=float, default=0.9, help="Sampling temperature")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for generation")
    parser.add_argument("--output-midi", type=str, default=None, help="Path for generated MIDI")
    parser.add_argument("--output-wav", type=str, default=None, help="Path for generated WAV preview")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda or cpu)")

    args = parser.parse_args()
    cfg = Config()

    ckpt_path = Path(args.checkpoint) if args.checkpoint else cfg.best_model_path
    if not ckpt_path.exists():
        ckpt_path = cfg.latest_model_path

    if not ckpt_path.exists():
        print(f"Error: No model checkpoint found at {ckpt_path}!")
        print("Please train a model first using: python train.py")
        sys.exit(1)

    device_name = args.device or cfg.device
    device = torch.device(device_name)

    print(f"Loading checkpoint from: {ckpt_path}")
    checkpoint = torch.load(str(ckpt_path), map_location=device)

    # Reconstruct config if present
    saved_cfg = checkpoint.get("config", {})
    if "hidden_dim" in saved_cfg:
        cfg.hidden_dim = saved_cfg["hidden_dim"]

    model = MelodyLSTM(cfg).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    epoch = checkpoint.get("epoch", "unknown")
    val_loss = checkpoint.get("val_loss", "unknown")
    print(f"Model loaded: Epoch {epoch}, Val Loss: {val_loss}")
    print(f"Generating {args.length} notes (temperature={args.temperature}, seed={args.seed})...")

    notes = generate_melody(
        model=model,
        cfg=cfg,
        num_notes=args.length,
        temperature=args.temperature,
        seed=args.seed,
        device=device_name,
    )

    out_midi = (
        Path(args.output_midi)
        if args.output_midi
        else (cfg.generated_dir / f"melody_seed{args.seed}_temp{args.temperature}.mid")
    )
    export_notes_to_midi(notes, out_midi, bpm=cfg.tempo_bpm)
    print(f"Saved MIDI file -> {out_midi}")

    out_wav = (
        Path(args.output_wav)
        if args.output_wav
        else (cfg.generated_dir / f"melody_seed{args.seed}_temp{args.temperature}.wav")
    )
    synthesize_notes_to_wav(notes, out_wav)
    print(f"Saved WAV preview -> {out_wav}")

    pitches = [n["pitch"] for n in notes]
    total_dur = notes[-1]["start"] + notes[-1]["duration"] if notes else 0.0
    print("-" * 50)
    print("Generation Summary:")
    print(f"  Total Notes: {len(notes)}")
    print(f"  Pitch Range: {min(pitches)} - {max(pitches)}")
    print(f"  Total Duration: {total_dur:.2f} seconds")
    print("-" * 50)


if __name__ == "__main__":
    main()
