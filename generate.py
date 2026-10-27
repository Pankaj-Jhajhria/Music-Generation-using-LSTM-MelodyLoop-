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
from melodyloop.data import parse_midi_file, dequantize_duration, dequantize_step
from melodyloop.generation import generate_melody, export_notes_to_midi
from melodyloop.model import MelodyLSTM


def main():
    parser = argparse.ArgumentParser(description="MelodyLoop Music Generation")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to model checkpoint .pt")
    parser.add_argument("--length", type=int, default=80, help="Number of notes to generate")
    parser.add_argument("--temperature", type=float, default=0.6, help="Sampling temperature (default: 0.6)")
    parser.add_argument("--top-k", type=int, default=5, help="Top-K candidate filtering (default: 5)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for generation")
    parser.add_argument("--seed-midi", type=str, default=None, help="Path to MIDI file to use as prompt phrase")
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

    seed_seq = None
    if args.seed_midi:
        sm_path = Path(args.seed_midi)
        if sm_path.exists():
            print(f"Loading prompt phrase from MIDI: {sm_path.name}")
            events = parse_midi_file(sm_path, cfg)
            seed_seq = []
            curr_t = 0.0
            for p, d, s in events[:32]:
                dur = dequantize_duration(d, cfg)
                step = dequantize_step(s, cfg)
                seed_seq.append({"pitch": p, "start": curr_t, "duration": dur, "step": step})
                curr_t += step
            print(f"Extracted {len(seed_seq)} prompt notes for continuation.")

    mode_label = "Seeded continuation" if seed_seq else "Free generation"
    print(f"Generating {args.length} notes [{mode_label}] (temperature={args.temperature}, top_k={args.top_k}, seed={args.seed})...")

    notes = generate_melody(
        model=model,
        cfg=cfg,
        num_notes=args.length,
        temperature=args.temperature,
        pitch_top_k=args.top_k,
        seed=args.seed,
        seed_sequence=seed_seq,
        device=device_name,
    )

    out_midi = (
        Path(args.output_midi)
        if args.output_midi
        else (cfg.generated_dir / f"melody_seed{args.seed}_temp{args.temperature}_topk{args.top_k}.mid")
    )
    export_notes_to_midi(notes, out_midi, bpm=cfg.tempo_bpm)
    print(f"Saved MIDI file -> {out_midi}")

    out_wav = (
        Path(args.output_wav)
        if args.output_wav
        else (cfg.generated_dir / f"melody_seed{args.seed}_temp{args.temperature}_topk{args.top_k}.wav")
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
