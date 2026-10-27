"""
Data preprocessing and dataset handling for MelodyLoop.
Handles MIDI parsing, tokenization, quantization, and sequence generation.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

import mido
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from config import Config

logger = logging.getLogger(__name__)


@dataclass
class RawNote:
    pitch: int
    start: float
    duration: float
    step: float


def quantize_value(val: float, min_val: float, max_val: float, num_bins: int) -> int:
    """Quantize continuous value into [0, num_bins - 1]."""
    clipped = min(max(val, min_val), max_val)
    normalized = (clipped - min_val) / max(max_val - min_val, 1e-6)
    idx = int(normalized * (num_bins - 1) + 0.5)
    return min(max(idx, 0), num_bins - 1)


def dequantize_value(bin_idx: int, min_val: float, max_val: float, num_bins: int) -> float:
    """Convert discrete bin back to continuous value."""
    bin_idx = min(max(int(bin_idx), 0), num_bins - 1)
    return min_val + (bin_idx / max(num_bins - 1, 1)) * (max_val - min_val)


def quantize_duration(dur: float, cfg: Config) -> int:
    return quantize_value(dur, cfg.min_duration, cfg.max_duration, cfg.duration_bins)


def dequantize_duration(bin_idx: int, cfg: Config) -> float:
    return dequantize_value(bin_idx, cfg.min_duration, cfg.max_duration, cfg.duration_bins)


def quantize_step(step: float, cfg: Config) -> int:
    return quantize_value(step, cfg.min_step, cfg.max_step, cfg.step_bins)


def dequantize_step(bin_idx: int, cfg: Config) -> float:
    return dequantize_value(bin_idx, cfg.min_step, cfg.max_step, cfg.step_bins)


def parse_midi_file(filepath: Path | str, cfg: Config) -> List[Tuple[int, int, int]]:
    """
    Parse a MIDI file safely, extracting chronological note events.
    Each event is a tuple: (pitch_idx, duration_idx, step_idx).
    Returns an empty list if file is invalid or empty.
    """
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"File not found: {path}")
        return []

    try:
        mid = mido.MidiFile(str(path), clip=True)
    except Exception as e:
        logger.warning(f"Error reading MIDI file {path.name}: {e}")
        return []

    current_time = 0.0
    active_notes: Dict[int, List[float]] = {}
    raw_notes: List[Dict[str, Any]] = []

    try:
        for msg in mid:
            current_time += getattr(msg, "time", 0.0)
            if msg.type == "note_on" and msg.velocity > 0:
                active_notes.setdefault(msg.note, []).append(current_time)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active_notes and active_notes[msg.note]:
                    start_time = active_notes[msg.note].pop(0)
                    dur = max(cfg.min_duration, current_time - start_time)
                    raw_notes.append({
                        "pitch": min(max(int(msg.note), 0), cfg.pitch_vocab_size - 1),
                        "start": start_time,
                        "duration": dur,
                    })
    except Exception as e:
        logger.warning(f"Corrupted messages in {path.name}: {e}")

    # Close any unclosed notes safely
    for pitch, starts in active_notes.items():
        for st in starts:
            dur = max(cfg.min_duration, current_time - st)
            raw_notes.append({
                "pitch": min(max(int(pitch), 0), cfg.pitch_vocab_size - 1),
                "start": st,
                "duration": dur,
            })

    if not raw_notes:
        return []

    # Sort chronologically by start time, then pitch
    raw_notes.sort(key=lambda n: (n["start"], n["pitch"]))

    # Compute step time to next note and quantize
    events: List[Tuple[int, int, int]] = []
    num_notes = len(raw_notes)
    for i in range(num_notes):
        n = raw_notes[i]
        if i + 1 < num_notes:
            step = max(0.0, raw_notes[i + 1]["start"] - n["start"])
        else:
            step = 0.25  # Final default step

        p_idx = n["pitch"]
        d_idx = quantize_duration(n["duration"], cfg)
        s_idx = quantize_step(step, cfg)
        events.append((p_idx, d_idx, s_idx))

    return events


def create_sequences_from_events(
    events: List[Tuple[int, int, int]], seq_length: int, stride: int = 1
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build input sequences X and target next-events y from note events.
    X shape: (num_seqs, seq_length, 3)
    y shape: (num_seqs, 3)
    """
    if len(events) <= seq_length:
        return (
            np.empty((0, seq_length, 3), dtype=np.int64),
            np.empty((0, 3), dtype=np.int64),
        )

    xs = []
    ys = []
    for i in range(0, len(events) - seq_length, stride):
        xs.append(events[i : i + seq_length])
        ys.append(events[i + seq_length])

    return np.array(xs, dtype=np.int64), np.array(ys, dtype=np.int64)


class MelodyDataset(Dataset):
    """PyTorch Dataset for MelodyLoop sequences."""

    def __init__(self, sequences: np.ndarray, targets: np.ndarray):
        super().__init__()
        self.x = torch.from_numpy(sequences).long()  # (N, seq_len, 3)
        self.y_pitch = torch.from_numpy(targets[:, 0]).long()
        self.y_duration = torch.from_numpy(targets[:, 1]).long()
        self.y_step = torch.from_numpy(targets[:, 2]).long()

    def __len__(self) -> int:
        return len(self.x)

    def __getitem__(self, idx: int):
        return {
            "x": self.x[idx],
            "pitch": self.y_pitch[idx],
            "duration": self.y_duration[idx],
            "step": self.y_step[idx],
        }


def load_maestro_split(
    split_name: str,
    cfg: Config,
    max_files: Optional[int] = None,
    max_sequences: Optional[int] = None,
) -> Tuple[MelodyDataset, Dict[str, Any]]:
    """
    Load and preprocess MAESTRO split according to configuration limits.
    Returns dataset and summary statistics.
    """
    csv_path = cfg.csv_path
    if not csv_path.exists():
        raise FileNotFoundError(f"MAESTRO metadata CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)
    split_df = df[df["split"] == split_name]

    if max_files is not None and max_files > 0:
        split_df = split_df.head(max_files)

    base_dir = cfg.data_dir
    all_x = []
    all_y = []
    total_notes = 0
    files_processed = 0
    files_skipped = 0

    for _, row in split_df.iterrows():
        rel_path = row["midi_filename"]
        midi_path = base_dir / rel_path
        events = parse_midi_file(midi_path, cfg)
        if not events:
            files_skipped += 1
            continue

        files_processed += 1
        total_notes += len(events)
        xs, ys = create_sequences_from_events(events, cfg.seq_length, cfg.stride)
        if len(xs) > 0:
            all_x.append(xs)
            all_y.append(ys)

        current_total = sum(len(x) for x in all_x)
        if max_sequences is not None and current_total >= max_sequences:
            break

    if all_x:
        combined_x = np.concatenate(all_x, axis=0)
        combined_y = np.concatenate(all_y, axis=0)
        if max_sequences is not None and len(combined_x) > max_sequences:
            combined_x = combined_x[:max_sequences]
            combined_y = combined_y[:max_sequences]
    else:
        combined_x = np.empty((0, cfg.seq_length, 3), dtype=np.int64)
        combined_y = np.empty((0, 3), dtype=np.int64)

    stats = {
        "split": split_name,
        "files_considered": len(split_df),
        "files_processed": files_processed,
        "files_skipped": files_skipped,
        "total_notes": total_notes,
        "total_sequences": len(combined_x),
    }

    dataset = MelodyDataset(combined_x, combined_y)
    return dataset, stats


def create_synthetic_midi(output_path: Path | str, num_notes: int = 40) -> Path:
    """Generate a tiny synthetic MIDI file for testing purposes."""
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Set tempo (120 BPM = 500,000 microseconds per beat)
    track.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))

    # C major scale repetition: C4, D4, E4, F4, G4, A4, B4, C5
    scale = [60, 62, 64, 65, 67, 69, 71, 72]
    for i in range(num_notes):
        pitch = scale[i % len(scale)]
        track.append(mido.Message("note_on", note=pitch, velocity=80, time=0))
        track.append(mido.Message("note_off", note=pitch, velocity=64, time=240))  # Eighth note

    mid.save(str(out_p))
    return out_p
