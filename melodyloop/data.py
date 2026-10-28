"""
Data preprocessing and dataset handling for MelodyLoop.
Handles MIDI parsing, tokenization, quantization, and sequence generation.
"""

import logging
import os
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
            np.empty((0, seq_length, 3), dtype=np.uint8),
            np.empty((0, 3), dtype=np.uint8),
        )

    xs = []
    ys = []
    for i in range(0, len(events) - seq_length, stride):
        xs.append(events[i : i + seq_length])
        ys.append(events[i + seq_length])

    return np.array(xs, dtype=np.uint8), np.array(ys, dtype=np.uint8)


class MelodyDataset(Dataset):
    """
    PyTorch Dataset for MelodyLoop sequences.
    Stores arrays as compact uint8 tensors in RAM (8x memory reduction),
    returning torch.long tensors on __getitem__ for neural layer compatibility.
    """

    def __init__(self, sequences: np.ndarray | torch.Tensor, targets: np.ndarray | torch.Tensor):
        super().__init__()
        if isinstance(sequences, torch.Tensor):
            self.x = sequences.to(torch.uint8)
        else:
            self.x = torch.from_numpy(np.asarray(sequences, dtype=np.uint8))

        if isinstance(targets, torch.Tensor):
            self.y_pitch = targets[:, 0].to(torch.uint8)
            self.y_duration = targets[:, 1].to(torch.uint8)
            self.y_step = targets[:, 2].to(torch.uint8)
        else:
            targets_np = np.asarray(targets, dtype=np.uint8)
            self.y_pitch = torch.from_numpy(targets_np[:, 0])
            self.y_duration = torch.from_numpy(targets_np[:, 1])
            self.y_step = torch.from_numpy(targets_np[:, 2])

    def __len__(self) -> int:
        return len(self.x)

    def __getitem__(self, idx: int):
        return {
            "x": self.x[idx].long(),
            "pitch": self.y_pitch[idx].long(),
            "duration": self.y_duration[idx].long(),
            "step": self.y_step[idx].long(),
        }


def _worker_parse_midi(args: Tuple[str, Config]) -> Tuple[str, List[Tuple[int, int, int]]]:
    """Helper worker for multi-process parsing."""
    filepath_str, cfg = args
    ev = parse_midi_file(filepath_str, cfg)
    return filepath_str, ev


def load_maestro_split(
    split_name: str,
    cfg: Config,
    max_files: Optional[int] = None,
    max_sequences: Optional[int] = None,
    use_cache: bool = True,
) -> Tuple[MelodyDataset, Dict[str, Any]]:
    """
    Load and preprocess MAESTRO split according to configuration limits.
    Supports:
      - Processing ALL available split performances (when max_files is None or <= 0).
      - Persistent disk caching of parsed note events in artifacts/cache/ for instant loading.
      - Balanced sequence sampling across all eligible performances.
      - Compact uint8 storage to protect laptop RAM.
    """
    csv_path = cfg.csv_path
    if not csv_path.exists():
        raise FileNotFoundError(f"MAESTRO metadata CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)
    split_df = df[df["split"] == split_name]

    if max_files is not None and max_files > 0:
        split_df = split_df.head(max_files)

    num_target_files = len(split_df)
    base_dir = cfg.data_dir
    cache_path = cfg.cache_dir / f"maestro_{split_name}_events_cache.npz"

    # Step 1: Ingest or compute parsed events dictionary {rel_path: np.ndarray(N, 3)}
    events_by_file: Dict[str, np.ndarray] = {}
    cache_loaded = False

    if use_cache and cache_path.exists():
        try:
            logger.info(f"Loading cached note events from {cache_path.name}...")
            with np.load(cache_path) as cached:
                events_by_file = {k: cached[k] for k in cached.files}
            cache_loaded = True
            logger.info(f"Loaded {len(events_by_file)} performances from event cache.")
        except Exception as e:
            logger.warning(f"Could not load event cache ({e}), re-parsing...")

    # Identify files that need parsing
    target_rel_paths = list(split_df["midi_filename"])
    missing_paths = [p for p in target_rel_paths if p not in events_by_file]

    if missing_paths:
        logger.info(f"Parsing {len(missing_paths)} MIDI files for split '{split_name}'...")
        abs_paths = [str(base_dir / p) for p in missing_paths]

        # Use fast sequential or parallel parsing
        import concurrent.futures
        workers = min(6, os.cpu_count() or 4) if len(missing_paths) >= 10 else 1

        if workers > 1:
            worker_args = [(p, cfg) for p in abs_paths]
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
                for rel_p, (_, ev) in zip(missing_paths, executor.map(_worker_parse_midi, worker_args)):
                    if ev:
                        events_by_file[rel_p] = np.array(ev, dtype=np.uint8)
        else:
            for rel_p, abs_p in zip(missing_paths, abs_paths):
                ev = parse_midi_file(abs_p, cfg)
                if ev:
                    events_by_file[rel_p] = np.array(ev, dtype=np.uint8)

        # Update cache file on disk
        if use_cache and events_by_file:
            try:
                cfg.cache_dir.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(cache_path, **events_by_file)
                logger.info(f"Saved {len(events_by_file)} performances to cache -> {cache_path.name}")
            except Exception as e:
                logger.warning(f"Failed to save cache file: {e}")

    # Step 2: Build sequences from all eligible files with proportional balancing
    all_x: List[np.ndarray] = []
    all_y: List[np.ndarray] = []
    total_notes = 0
    files_processed = 0
    files_skipped = 0

    valid_files_count = sum(1 for p in target_rel_paths if p in events_by_file and len(events_by_file[p]) > cfg.seq_length)
    max_per_file = None
    if max_sequences is not None and max_sequences > 0 and valid_files_count > 0:
        # Distribute sequence budget across ALL valid target files proportionally
        max_per_file = max(16, int(np.ceil((max_sequences * 1.10) / valid_files_count)))

    for rel_path in target_rel_paths:
        events_arr = events_by_file.get(rel_path)
        if events_arr is None or len(events_arr) <= cfg.seq_length:
            files_skipped += 1
            continue

        files_processed += 1
        total_notes += len(events_arr)

        xs, ys = create_sequences_from_events(events_arr, cfg.seq_length, cfg.stride)
        if len(xs) > 0:
            if max_per_file is not None and len(xs) > max_per_file:
                # Evenly sample sequences across the full performance
                indices = np.linspace(0, len(xs) - 1, max_per_file, dtype=int)
                xs = xs[indices]
                ys = ys[indices]
            all_x.append(xs)
            all_y.append(ys)

    if all_x:
        combined_x = np.concatenate(all_x, axis=0)
        combined_y = np.concatenate(all_y, axis=0)
        if max_sequences is not None and max_sequences > 0 and len(combined_x) > max_sequences:
            combined_x = combined_x[:max_sequences]
            combined_y = combined_y[:max_sequences]
    else:
        combined_x = np.empty((0, cfg.seq_length, 3), dtype=np.uint8)
        combined_y = np.empty((0, 3), dtype=np.uint8)

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
