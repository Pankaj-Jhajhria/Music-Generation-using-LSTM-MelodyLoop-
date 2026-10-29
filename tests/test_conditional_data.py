"""
Tests for conditional dataset handling, velocity quantization, condition encoding,
and dataset tensor dtypes.
"""

import tempfile
from pathlib import Path
import mido
import numpy as np
import pytest
import torch

from config import Config
from melodyloop.conditional_data import (
    quantize_velocity,
    dequantize_velocity,
    determine_register,
    determine_dynamics,
    parse_piece_mood,
    parse_piece_tempo,
    parse_conditional_midi_file,
    create_conditional_sequences,
    ConditionalMelodyDataset,
    MOOD_VOCAB,
    TEMPO_VOCAB,
    REGISTER_VOCAB,
    DYNAMICS_VOCAB,
)


def test_velocity_quantization():
    # Test min and max bounds
    assert quantize_velocity(1) == 0
    assert quantize_velocity(127) == 15
    assert quantize_velocity(64) == 8

    # Test round trip sanity
    for v in [10, 40, 70, 100, 120]:
        bin_idx = quantize_velocity(v, num_bins=16)
        restored = dequantize_velocity(bin_idx, num_bins=16)
        assert abs(v - restored) <= 10


def test_register_and_dynamics_determination():
    # Pitch register: low (<=58), middle (59-71), high (>=72)
    assert determine_register([36, 40, 48]) == "low"
    assert determine_register([60, 62, 64, 65]) == "middle"
    assert determine_register([72, 76, 84, 88]) == "high"

    # Dynamics: soft (<=65), medium (66-95), strong (>=96)
    assert determine_dynamics([30, 40, 50]) == "soft"
    assert determine_dynamics([70, 80, 85]) == "medium"
    assert determine_dynamics([100, 110, 120]) == "strong"


def test_mood_and_tempo_parsing():
    assert parse_piece_mood(["relaxing", "calm"]) == "calm"
    assert parse_piece_mood(["happy", "joyful"]) == "happy"
    assert parse_piece_mood(["dark", "epic"]) == "dramatic"
    assert parse_piece_mood(["unknown_tag"]) == "any"

    assert parse_piece_tempo(75.0, None) == "slow"
    assert parse_piece_tempo(120.0, None) == "moderate"
    assert parse_piece_tempo(150.0, None) == "fast"
    assert parse_piece_tempo(None, "Andante") == "slow"
    assert parse_piece_tempo(None, "Presto") == "fast"


def test_synthetic_conditional_midi_parsing():
    cfg = Config()
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # 4 distinct notes with varying velocities
    notes = [
        (60, 40, 0, 480),     # C4, soft vel=40
        (64, 80, 480, 480),   # E4, med vel=80
        (67, 110, 960, 480),  # G4, strong vel=110
        (72, 90, 1440, 480),  # C5, med vel=90
    ]
    for pitch, vel, start_tick, dur_tick in notes:
        track.append(mido.Message("note_on", note=pitch, velocity=vel, time=start_tick if pitch == 60 else 0))
        track.append(mido.Message("note_off", note=pitch, velocity=0, time=dur_tick))

    with tempfile.TemporaryDirectory() as tmpdir:
        midi_path = Path(tmpdir) / "test_synth.mid"
        mid.save(str(midi_path))

        events = parse_conditional_midi_file(midi_path, cfg, velocity_bins=16)
        assert len(events) == 4
        # Each event is (pitch, dur_bin, step_bin, vel_bin)
        assert len(events[0]) == 4
        assert events[0][0] == 60
        assert quantize_velocity(40) == events[0][3]


def test_conditional_dataset_tensors():
    # Synthetic sequences: 20 sequences of len 16 with 4 features
    xs = np.random.randint(0, 16, size=(20, 16, 4), dtype=np.uint8)
    ys = np.random.randint(0, 16, size=(20, 4), dtype=np.uint8)
    conds = np.random.randint(0, 4, size=(20, 4), dtype=np.uint8)

    dataset = ConditionalMelodyDataset(xs, ys, conds)
    assert len(dataset) == 20

    item = dataset[0]
    assert item["x"].shape == (16, 4)
    assert item["x"].dtype == torch.long
    assert item["cond"].shape == (4,)
    assert item["cond"].dtype == torch.long
    assert item["pitch"].dtype == torch.long
    assert item["duration"].dtype == torch.long
    assert item["step"].dtype == torch.long
    assert item["velocity"].dtype == torch.long
