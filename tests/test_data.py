"""
Unit tests for MelodyLoop data preprocessing.
Uses synthetic MIDI files to keep tests lightweight and fast.
"""

import tempfile
from pathlib import Path
import pytest
import torch

from config import Config
from melodyloop.data import (
    quantize_value,
    dequantize_value,
    quantize_duration,
    dequantize_duration,
    quantize_step,
    dequantize_step,
    create_synthetic_midi,
    parse_midi_file,
    create_sequences_from_events,
    MelodyDataset,
)


def test_quantization_roundtrip():
    cfg = Config()
    
    # Test duration
    dur_bin = quantize_duration(0.5, cfg)
    assert 0 <= dur_bin < cfg.duration_bins
    rec_dur = dequantize_duration(dur_bin, cfg)
    assert abs(rec_dur - 0.5) < (cfg.max_duration - cfg.min_duration) / cfg.duration_bins
    
    # Test step
    step_bin = quantize_step(0.25, cfg)
    assert 0 <= step_bin < cfg.step_bins
    rec_step = dequantize_step(step_bin, cfg)
    assert abs(rec_step - 0.25) < (cfg.max_step - cfg.min_step) / cfg.step_bins


def test_synthetic_midi_parsing():
    cfg = Config()
    with tempfile.TemporaryDirectory() as tmpdir:
        synth_path = Path(tmpdir) / "test_scale.mid"
        create_synthetic_midi(synth_path, num_notes=48)
        assert synth_path.exists()
        
        events = parse_midi_file(synth_path, cfg)
        assert len(events) == 48
        
        for p, d, s in events:
            assert 0 <= p < cfg.pitch_vocab_size
            assert 0 <= d < cfg.duration_bins
            assert 0 <= s < cfg.step_bins


def test_sequence_generation_and_dataset():
    cfg = Config(seq_length=16, stride=2)
    with tempfile.TemporaryDirectory() as tmpdir:
        synth_path = Path(tmpdir) / "test_scale.mid"
        create_synthetic_midi(synth_path, num_notes=40)
        
        events = parse_midi_file(synth_path, cfg)
        x, y = create_sequences_from_events(events, cfg.seq_length, cfg.stride)
        
        assert len(x) > 0
        assert x.shape[1] == 16
        assert x.shape[2] == 3
        assert y.shape[1] == 3
        assert len(x) == len(y)
        
        dataset = MelodyDataset(x, y)
        assert len(dataset) == len(x)
        
        sample = dataset[0]
        assert "x" in sample and "pitch" in sample and "duration" in sample and "step" in sample
        assert sample["x"].shape == (16, 3)
        assert sample["x"].dtype == torch.long
        assert isinstance(sample["pitch"].item(), int)


def test_corrupt_file_handling():
    cfg = Config()
    with tempfile.TemporaryDirectory() as tmpdir:
        corrupt_path = Path(tmpdir) / "corrupt.mid"
        corrupt_path.write_bytes(b"NOT A REAL MIDI FILE CONTENT")
        
        events = parse_midi_file(corrupt_path, cfg)
        assert events == []
        
        non_existent = Path(tmpdir) / "does_not_exist.mid"
        assert parse_midi_file(non_existent, cfg) == []
