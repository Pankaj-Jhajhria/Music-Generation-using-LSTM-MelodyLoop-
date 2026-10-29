"""
Conditional data handling, MIDI parsing, and dataset creation for MelodyLoop 2.0.
Supports 4-feature events (pitch, duration, step, velocity) and structured musical conditioning
(mood, tempo, pitch register, dynamics).
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Union

import mido
import numpy as np
import torch
from torch.utils.data import Dataset

from config import Config

logger = logging.getLogger(__name__)

# Condition Vocabularies
MOOD_VOCAB = ["any", "calm", "happy", "sad", "energetic", "dramatic", "romantic"]
TEMPO_VOCAB = ["any", "slow", "moderate", "fast"]
REGISTER_VOCAB = ["any", "low", "middle", "high"]
DYNAMICS_VOCAB = ["any", "soft", "medium", "strong"]

MOOD_TO_IDX = {m: i for i, m in enumerate(MOOD_VOCAB)}
TEMPO_TO_IDX = {t: i for i, t in enumerate(TEMPO_VOCAB)}
REGISTER_TO_IDX = {r: i for i, r in enumerate(REGISTER_VOCAB)}
DYNAMICS_TO_IDX = {d: i for i, d in enumerate(DYNAMICS_VOCAB)}

# Semantic mapping from raw dataset tags to supported mood categories
MOOD_ALIAS_MAP = {
    "calm": {"relaxing", "meditative", "calm", "peaceful", "gentle", "serene", "ambient"},
    "happy": {"happy", "positive", "uplifting", "cheerful", "bright", "joyful", "fun"},
    "sad": {"sad", "emotional", "melancholic", "ballad", "sorrow", "melancholy", "grief"},
    "energetic": {"energetic", "action", "motivational", "upbeat", "intense", "powerful"},
    "dramatic": {"drama", "epic", "dark", "tense", "cinematic", "heavy"},
    "romantic": {"romantic", "love", "reflective", "dream", "sensual"},
}

# General MIDI piano family programs (0-7)
PIANO_PROGRAMS = set(range(8))


def quantize_velocity(vel: int | float, num_bins: int = 16) -> int:
    """Quantize MIDI velocity (1-127) into discrete bins [0, num_bins - 1]."""
    clipped = min(max(float(vel), 1.0), 127.0)
    idx = int((clipped / 128.0) * num_bins)
    return min(max(idx, 0), num_bins - 1)


def dequantize_velocity(bin_idx: int, num_bins: int = 16) -> int:
    """Convert discrete velocity bin back to MIDI velocity (1-127)."""
    bin_idx = min(max(int(bin_idx), 0), num_bins - 1)
    step = 128.0 / num_bins
    center = int(bin_idx * step + step / 2)
    return min(max(center, 1), 127)


def determine_register(pitches: Union[List[int], np.ndarray]) -> str:
    """Determine register based on median pitch: low (<=58), middle (59-71), high (>=72)."""
    if len(pitches) == 0:
        return "middle"
    med = float(np.median(pitches))
    if med <= 58.0:
        return "low"
    elif med <= 71.0:
        return "middle"
    else:
        return "high"


def determine_dynamics(velocities: Union[List[int], np.ndarray]) -> str:
    """Determine dynamics based on median velocity: soft (<=65), medium (66-95), strong (>=96)."""
    if len(velocities) == 0:
        return "medium"
    med = float(np.median(velocities))
    if med <= 65.0:
        return "soft"
    elif med <= 95.0:
        return "medium"
    else:
        return "strong"


def parse_piece_mood(raw_moods: List[str]) -> str:
    """Map raw mood tags from dataset to a supported mood category."""
    if not raw_moods:
        return "any"
    cleaned = {str(m).strip().lower() for m in raw_moods}
    for target, aliases in MOOD_ALIAS_MAP.items():
        if cleaned & aliases:
            return target
    return "any"


def parse_piece_tempo(tempo_val: Optional[float], tempo_word: Optional[str]) -> str:
    """Map tempo BPM or descriptive tempo word to slow, moderate, or fast."""
    if tempo_val is not None and not np.isnan(tempo_val):
        t = float(tempo_val)
        if t < 90.0:
            return "slow"
        elif t <= 130.0:
            return "moderate"
        else:
            return "fast"
    tw = str(tempo_word or "").lower()
    if any(w in tw for w in ["slow", "adagio", "lento", "grave", "andante"]):
        return "slow"
    elif any(w in tw for w in ["fast", "allegro", "presto", "vivace", "very fast"]):
        return "fast"
    elif any(w in tw for w in ["moderate", "moderato", "andantino", "allegretto"]):
        return "moderate"
    return "moderate"


def parse_conditional_midi_file(
    filepath: Union[Path, str],
    cfg: Config,
    velocity_bins: int = 16,
) -> List[Tuple[int, int, int, int]]:
    """
    Parse a MIDI file safely, extracting chronological piano note events.
    Each event is a 4-tuple: (pitch_idx, duration_idx, step_idx, velocity_idx).
    Excludes non-piano tracks if instrument information is present.
    """
    from melodyloop.data import quantize_duration, quantize_step

    path = Path(filepath)
    if not path.exists():
        logger.warning(f"File not found: {path}")
        return []

    try:
        mid = mido.MidiFile(str(path), clip=True)
    except Exception as e:
        logger.warning(f"Error reading MIDI file {path.name}: {e}")
        return []

    # Map tracks/channels to program numbers if possible
    # In General MIDI, channel 9 (10 in 1-based) is percussion/drums
    current_time = 0.0
    active_notes: Dict[int, List[Tuple[float, int]]] = {}
    raw_notes: List[Dict[str, Any]] = []

    try:
        for msg in mid:
            current_time += getattr(msg, "time", 0.0)
            channel = getattr(msg, "channel", 0)
            if channel == 9:  # Skip drums/percussion
                continue

            if msg.type == "note_on" and msg.velocity > 0:
                active_notes.setdefault(msg.note, []).append((current_time, msg.velocity))
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active_notes and active_notes[msg.note]:
                    start_time, vel = active_notes[msg.note].pop(0)
                    dur = max(cfg.min_duration, current_time - start_time)
                    raw_notes.append({
                        "pitch": min(max(int(msg.note), 0), cfg.pitch_vocab_size - 1),
                        "start": start_time,
                        "duration": dur,
                        "velocity": min(max(int(vel), 1), 127),
                    })
    except Exception as e:
        logger.warning(f"Corrupted messages in {path.name}: {e}")

    # Close any unclosed notes
    for pitch, starts in active_notes.items():
        for st, vel in starts:
            dur = max(cfg.min_duration, current_time - st)
            raw_notes.append({
                "pitch": min(max(int(pitch), 0), cfg.pitch_vocab_size - 1),
                "start": st,
                "duration": dur,
                "velocity": min(max(int(vel), 1), 127),
            })

    if not raw_notes:
        return []

    # Sort chronologically by start time, then pitch
    raw_notes.sort(key=lambda n: (n["start"], n["pitch"]))

    events: List[Tuple[int, int, int, int]] = []
    num_notes = len(raw_notes)
    for i in range(num_notes):
        n = raw_notes[i]
        if i + 1 < num_notes:
            step = max(0.0, raw_notes[i + 1]["start"] - n["start"])
        else:
            step = 0.25

        p_idx = n["pitch"]
        d_idx = quantize_duration(n["duration"], cfg)
        s_idx = quantize_step(step, cfg)
        v_idx = quantize_velocity(n["velocity"], num_bins=velocity_bins)
        events.append((p_idx, d_idx, s_idx, v_idx))

    return events


def create_conditional_sequences(
    events: List[Tuple[int, int, int, int]],
    piece_mood: str,
    piece_tempo: str,
    seq_length: int = 32,
    stride: int = 4,
    velocity_bins: int = 16,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build input sequences X, target next-events y, and condition vectors C from note events.
    X shape: (num_seqs, seq_length, 4) -> (pitch, dur, step, vel)
    y shape: (num_seqs, 4)             -> (pitch, dur, step, vel)
    C shape: (num_seqs, 4)             -> (mood_idx, tempo_idx, register_idx, dynamics_idx)
    """
    if len(events) <= seq_length:
        return (
            np.empty((0, seq_length, 4), dtype=np.uint8),
            np.empty((0, 4), dtype=np.uint8),
            np.empty((0, 4), dtype=np.uint8),
        )

    mood_idx = MOOD_TO_IDX.get(piece_mood, 0)
    tempo_idx = TEMPO_TO_IDX.get(piece_tempo, 0)

    xs = []
    ys = []
    conds = []

    for i in range(0, len(events) - seq_length, stride):
        seq = events[i : i + seq_length]
        target = events[i + seq_length]

        # Derive local register and dynamics for this exact sequence
        seq_pitches = [item[0] for item in seq]
        seq_velocities = [dequantize_velocity(item[3], num_bins=velocity_bins) for item in seq]

        reg_str = determine_register(seq_pitches)
        dyn_str = determine_dynamics(seq_velocities)

        reg_idx = REGISTER_TO_IDX.get(reg_str, 0)
        dyn_idx = DYNAMICS_TO_IDX.get(dyn_str, 0)

        xs.append(seq)
        ys.append(target)
        conds.append([mood_idx, tempo_idx, reg_idx, dyn_idx])

    return (
        np.array(xs, dtype=np.uint8),
        np.array(ys, dtype=np.uint8),
        np.array(conds, dtype=np.uint8),
    )


class ConditionalMelodyDataset(Dataset):
    """
    Bounded-memory PyTorch Dataset for Conditional MelodyLoop sequences.
    Stores arrays as compact uint8 tensors in RAM for minimal footprint,
    and returns torch.long tensors on __getitem__.
    """

    def __init__(
        self,
        sequences: Union[np.ndarray, torch.Tensor],
        targets: Union[np.ndarray, torch.Tensor],
        conditions: Union[np.ndarray, torch.Tensor],
    ):
        super().__init__()
        if isinstance(sequences, torch.Tensor):
            self.x = sequences.to(torch.uint8)
        else:
            self.x = torch.from_numpy(np.asarray(sequences, dtype=np.uint8))

        if isinstance(targets, torch.Tensor):
            targets_tensor = targets.to(torch.uint8)
        else:
            targets_tensor = torch.from_numpy(np.asarray(targets, dtype=np.uint8))

        if isinstance(conditions, torch.Tensor):
            self.cond = conditions.to(torch.uint8)
        else:
            self.cond = torch.from_numpy(np.asarray(conditions, dtype=np.uint8))

        self.y_pitch = targets_tensor[:, 0]
        self.y_duration = targets_tensor[:, 1]
        self.y_step = targets_tensor[:, 2]
        self.y_velocity = targets_tensor[:, 3]

    def __len__(self) -> int:
        return len(self.x)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        return {
            "x": self.x[idx].long(),                # Shape (seq_len, 4)
            "cond": self.cond[idx].long(),          # Shape (4,) -> [mood, tempo, reg, dyn]
            "pitch": self.y_pitch[idx].long(),
            "duration": self.y_duration[idx].long(),
            "step": self.y_step[idx].long(),
            "velocity": self.y_velocity[idx].long(),
        }


def build_or_load_conditional_dataset(
    cfg: Config,
    json_path: Union[str, Path] = "data_midicaps/train.json",
    midi_root: Union[str, Path] = "data_midicaps/midicaps",
    max_train_sequences: int = 60000,
    max_val_sequences: int = 6000,
    force_rebuild: bool = False,
    cache_path: Optional[Union[str, Path]] = None,
) -> Tuple[ConditionalMelodyDataset, ConditionalMelodyDataset, Dict[str, Any]]:
    """
    Load precomputed conditional dataset from disk cache if available,
    or build deterministically from MidiCaps metadata and MIDI files.
    """
    if cache_path is None:
        cache_path = cfg.cache_dir / "midicaps_conditional_cache.npz"
    cache_path = Path(cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if not force_rebuild and cache_path.exists():
        logger.info(f"Loading cached conditional dataset from {cache_path}")
        data = np.load(str(cache_path))
        train_ds = ConditionalMelodyDataset(data["train_x"], data["train_y"], data["train_cond"])
        val_ds = ConditionalMelodyDataset(data["val_x"], data["val_y"], data["val_cond"])
        meta = json.loads(str(data["meta"])) if "meta" in data else {}
        logger.info(f"Loaded {len(train_ds):,} train sequences and {len(val_ds):,} val sequences from cache.")
        return train_ds, val_ds, meta

    logger.info("Building conditional dataset from MidiCaps...")
    json_path = Path(json_path)
    midi_root = Path(midi_root)

    # Deterministic split: Collect solo piano pieces from train.json
    train_pieces: List[Dict[str, Any]] = []
    val_pieces: List[Dict[str, Any]] = []
    test_pieces: List[Dict[str, Any]] = []

    rng = np.random.RandomState(cfg.seed)

    with open(json_path, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            nums = r.get("instrument_numbers_sorted", [])
            summary = r.get("instrument_summary", [])
            is_solo_piano = (nums and all(p in PIANO_PROGRAMS for p in nums)) or (
                summary and all("piano" in str(s).lower() for s in summary)
            )
            if not is_solo_piano:
                continue

            loc = r.get("location")
            if not loc or not (midi_root / loc).exists():
                continue

            if r.get("test_set", False):
                test_pieces.append(r)
            else:
                train_pieces.append(r)

    # Deterministic 90/10 split on training-side pieces
    rng.shuffle(train_pieces)
    val_size = max(int(0.10 * len(train_pieces)), 10)
    actual_val_pieces = train_pieces[:val_size]
    actual_train_pieces = train_pieces[val_size:]

    logger.info(
        f"MidiCaps Solo Piano split: {len(actual_train_pieces):,} train pieces, "
        f"{len(actual_val_pieces):,} val pieces, {len(test_pieces):,} held-out test pieces."
    )

    def extract_sequences(pieces_list: List[Dict[str, Any]], max_seqs: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        all_x, all_y, all_cond = [], [], []
        collected = 0

        for r in pieces_list:
            if collected >= max_seqs:
                break
            loc = r.get("location")
            p = midi_root / loc
            events = parse_conditional_midi_file(p, cfg, velocity_bins=16)
            if len(events) <= cfg.seq_length:
                continue

            mood_str = parse_piece_mood(r.get("mood", []))
            tempo_str = parse_piece_tempo(r.get("tempo"), r.get("tempo_word"))

            xs, ys, conds = create_conditional_sequences(
                events,
                piece_mood=mood_str,
                piece_tempo=tempo_str,
                seq_length=cfg.seq_length,
                stride=cfg.stride,
                velocity_bins=16,
            )
            if len(xs) == 0:
                continue

            take = min(len(xs), max_seqs - collected)
            all_x.append(xs[:take])
            all_y.append(ys[:take])
            all_cond.append(conds[:take])
            collected += take

        if all_x:
            return (
                np.concatenate(all_x, axis=0),
                np.concatenate(all_y, axis=0),
                np.concatenate(all_cond, axis=0),
            )
        return (
            np.empty((0, cfg.seq_length, 4), dtype=np.uint8),
            np.empty((0, 4), dtype=np.uint8),
            np.empty((0, 4), dtype=np.uint8),
        )

    train_x, train_y, train_cond = extract_sequences(actual_train_pieces, max_train_sequences)
    val_x, val_y, val_cond = extract_sequences(actual_val_pieces, max_val_sequences)

    meta = {
        "train_pieces_count": len(actual_train_pieces),
        "val_pieces_count": len(actual_val_pieces),
        "test_pieces_count": len(test_pieces),
        "train_sequences_count": int(len(train_x)),
        "val_sequences_count": int(len(val_x)),
        "seq_length": cfg.seq_length,
        "stride": cfg.stride,
        "velocity_bins": 16,
        "seed": cfg.seed,
    }

    np.savez_compressed(
        str(cache_path),
        train_x=train_x,
        train_y=train_y,
        train_cond=train_cond,
        val_x=val_x,
        val_y=val_y,
        val_cond=val_cond,
        meta=json.dumps(meta),
    )
    logger.info(f"Saved conditional dataset cache to {cache_path} ({cache_path.stat().st_size / 1024**2:.2f} MB)")

    train_ds = ConditionalMelodyDataset(train_x, train_y, train_cond)
    val_ds = ConditionalMelodyDataset(val_x, val_y, val_cond)
    return train_ds, val_ds, meta

