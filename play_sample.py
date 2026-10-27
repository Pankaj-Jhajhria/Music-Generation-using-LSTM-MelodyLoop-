"""
Play Random Music Sample from Dataset or Generated Model.

Allows immediate auditory comparison between real human piano performances
from the MAESTRO dataset and LSTM-generated compositions.
Uses identical synthesis and Windows native audio playback.
"""

import argparse
from pathlib import Path
import random
import sys
import time
import pandas as pd

from config import Config
from melodyloop.audio import synthesize_notes_to_wav
from melodyloop.data import parse_midi_file, dequantize_duration, dequantize_step

# Windows native sound player
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


def play_wav_file(wav_path: Path):
    """Play WAV file using Windows native audio playback."""
    if not wav_path.exists():
        print(f"Error: WAV file not found at {wav_path}")
        return

    print(f"\n▶ Playing audio: {wav_path.name}")
    print("  (Press Ctrl+C to stop playback)")
    try:
        if HAS_WINSOUND:
            # Play synchronously so user hears it in terminal
            winsound.PlaySound(str(wav_path), winsound.SND_FILENAME)
        else:
            # Fallback for non-windows environments
            import os
            os.system(f'start "" "{wav_path}"')
    except KeyboardInterrupt:
        if HAS_WINSOUND:
            winsound.PlaySound(None, winsound.SND_PURGE)
        print("\nPlayback stopped by user.")


def play_random_dataset_sample(cfg: Config, notes_count: int = 80, split: str = None, open_raw_midi: bool = False):
    """Select a random performance from MAESTRO, synthesize a clip, and play it."""
    csv_path = cfg.data_dir / cfg.csv_filename
    if not csv_path.exists():
        print(f"Error: Dataset CSV not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    if split:
        df = df[df["split"].str.lower() == split.lower()]

    if df.empty:
        print(f"Error: No pieces found for split '{split}'")
        return

    # Filter to existing MIDI files
    valid_rows = []
    for _, row in df.iterrows():
        p = cfg.data_dir / row["midi_filename"]
        if p.exists():
            valid_rows.append((row, p))

    if not valid_rows:
        print("Error: No valid MIDI files found on disk.")
        return

    # Pick a random piece
    row, midi_path = random.choice(valid_rows)

    composer = row.get("canonical_composer", "Unknown Composer")
    title = row.get("canonical_title", "Unknown Title")
    year = row.get("year", "N/A")
    split_name = row.get("split", "N/A")

    print("=" * 60)
    print("🎵 REAL DATASET SAMPLE (Human Performance — MAESTRO v3.0)")
    print("=" * 60)
    print(f"  Composer : {composer}")
    print(f"  Title    : {title}")
    print(f"  Year     : {year} | Split: {split_name}")
    print(f"  MIDI File: {midi_path.name}")
    print("-" * 60)

    if open_raw_midi:
        print(f"Opening original MIDI directly in Windows Player: {midi_path.name}")
        import os
        os.system(f'start "" "{midi_path}"')
        return

    # Parse notes from original MIDI
    print(f"Extracting first {notes_count} notes...")
    events = parse_midi_file(midi_path, cfg)
    if not events:
        print("Warning: Could not parse notes from selected file, picking another...")
        return play_random_dataset_sample(cfg, notes_count, split)

    # Convert quantized (pitch, dur_idx, step_idx) tuples to playable note dicts
    notes_clip = []
    current_time = 0.0
    for p_idx, d_idx, s_idx in events[:notes_count]:
        dur = dequantize_duration(d_idx, cfg)
        step = dequantize_step(s_idx, cfg)
        notes_clip.append({
            "pitch": p_idx,
            "start": current_time,
            "duration": dur,
            "step": step,
        })
        current_time += step

    duration = notes_clip[-1]["start"] + notes_clip[-1]["duration"] if notes_clip else 0.0
    print(f"Synthesizing {len(notes_clip)} notes ({duration:.1f}s) with MelodyLoop harmonic engine...")

    out_wav = cfg.generated_dir / "dataset_sample.wav"
    synthesize_notes_to_wav(notes_clip, out_wav)

    play_wav_file(out_wav)


def play_latest_generated_sample(cfg: Config):
    """Play the latest generated melody from the artifacts/generated directory."""
    wav_files = sorted(list(cfg.generated_dir.glob("melody_*.wav")) + list(cfg.generated_dir.glob("generated_*.wav")),
                       key=lambda p: p.stat().st_mtime, reverse=True)

    if not wav_files:
        print("No generated WAV files found! Generate one first using: python generate.py")
        return

    latest_wav = wav_files[0]
    print("=" * 60)
    print("🤖 LSTM GENERATED SAMPLE (Model-Composed)")
    print("=" * 60)
    print(f"  File: {latest_wav.name}")
    print("-" * 60)
    play_wav_file(latest_wav)


def main():
    parser = argparse.ArgumentParser(description="Play music from MAESTRO dataset or LSTM generator.")
    parser.add_argument("--mode", choices=["dataset", "generated", "compare"], default="dataset",
                        help="Play random dataset piece, generated melody, or side-by-side comparison.")
    parser.add_argument("--notes", type=int, default=80, help="Number of notes to extract/play (default: 80)")
    parser.add_argument("--split", type=str, default=None, help="Dataset split (train, validation, test)")
    parser.add_argument("--raw-midi", action="store_true", help="Open the raw MIDI directly in Windows Player")

    args = parser.parse_args()
    cfg = Config()

    if args.mode == "dataset":
        play_random_dataset_sample(cfg, notes_count=args.notes, split=args.split, open_raw_midi=args.raw_midi)
    elif args.mode == "generated":
        play_latest_generated_sample(cfg)
    elif args.mode == "compare":
        print("\n--- [PART 1/2] Real Human Performance from Dataset ---")
        play_random_dataset_sample(cfg, notes_count=args.notes, split=args.split)
        print("\nWaiting 2 seconds before playing generated melody...")
        time.sleep(2)
        print("\n--- [PART 2/2] LSTM Generated Music ---")
        play_latest_generated_sample(cfg)
        print("=" * 60)
        print("🔍 COMPARISON INSIGHT:")
        print("• Human Performance: Features rich rubato (expressive timing), wide dynamic pitch range,")
        print("  and complex chordal harmonizations spanning multiple octaves.")
        print("• LSTM Model Output: Successfully learned temporal transitions, active register locality,")
        print("  and quantized duration structures, producing coherent rhythmic phrases!")
        print("=" * 60)


if __name__ == "__main__":
    main()
