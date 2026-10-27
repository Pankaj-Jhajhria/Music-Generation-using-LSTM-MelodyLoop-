"""
Unit tests for MelodyLoop generation, MIDI export, and audio synthesis.
"""

import tempfile
from pathlib import Path
import mido
import numpy as np
from scipy.io import wavfile
import torch

from config import Config
from melodyloop.audio import synthesize_notes_to_wav
from melodyloop.generation import (
    sample_with_temperature,
    generate_melody,
    export_notes_to_midi,
)
from melodyloop.model import MelodyLSTM


def test_temperature_sampling():
    logits = torch.tensor([0.1, 0.2, 5.0, 0.3])
    # Very low temp should choose index 2
    sampled_greedy = sample_with_temperature(logits, temperature=0.01)
    assert sampled_greedy == 2

    # Higher temp should still sample within valid bounds
    sampled_high = sample_with_temperature(logits, temperature=1.5)
    assert 0 <= sampled_high < 4


def test_top_k_sampling():
    logits = torch.tensor([10.0, 0.1, 0.2, 9.0, 0.05])
    # With top_k=2, only indices 0 and 3 are allowed
    for s in range(20):
        sampled = sample_with_temperature(logits, temperature=1.0, top_k=2)
        assert sampled in (0, 3)


def test_seeded_phrase_continuation():
    cfg = Config(hidden_dim=64, num_layers=1)
    model = MelodyLSTM(cfg)
    prompt = [
        {"pitch": 60, "start": 0.0, "duration": 0.4, "step": 0.25},
        {"pitch": 64, "start": 0.25, "duration": 0.4, "step": 0.25},
    ]
    notes = generate_melody(
        model=model,
        cfg=cfg,
        num_notes=15,
        temperature=0.6,
        pitch_top_k=5,
        seed=42,
        seed_sequence=prompt,
        device="cpu",
    )
    # Total notes = 2 prompt notes + 15 generated notes = 17
    assert len(notes) == 17
    assert notes[0]["is_seed"] is True
    assert notes[1]["is_seed"] is True
    assert notes[2]["is_seed"] is False
    assert notes[0]["pitch"] == 60
    assert notes[1]["pitch"] == 64


def test_autoregressive_generation():
    cfg = Config(hidden_dim=64, num_layers=1)
    model = MelodyLSTM(cfg)
    
    notes = generate_melody(
        model=model,
        cfg=cfg,
        num_notes=20,
        temperature=0.8,
        seed=123,
        device="cpu",
    )
    
    assert len(notes) == 20
    for i, n in enumerate(notes):
        assert "pitch" in n and "start" in n and "duration" in n and "step" in n
        assert 0 <= n["pitch"] < cfg.pitch_vocab_size
        assert n["duration"] > 0
        assert n["start"] >= 0
        if i > 0:
            assert n["start"] >= notes[i - 1]["start"]


def test_midi_export_and_reparsing():
    cfg = Config()
    notes = [
        {"pitch": 60, "start": 0.0, "duration": 0.5, "step": 0.25},
        {"pitch": 64, "start": 0.25, "duration": 0.4, "step": 0.25},
        {"pitch": 67, "start": 0.5, "duration": 0.6, "step": 0.5},
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        midi_path = Path(tmpdir) / "output.mid"
        export_notes_to_midi(notes, midi_path, bpm=120)
        assert midi_path.exists()

        # Parse with mido
        mid = mido.MidiFile(str(midi_path))
        assert len(mid.tracks) > 0
        note_msgs = [m for m in mid if m.type in ("note_on", "note_off")]
        assert len(note_msgs) == 6  # 3 notes -> 3 on + 3 off


def test_wav_synthesis():
    notes = [
        {"pitch": 60, "start": 0.0, "duration": 0.3, "step": 0.2},
        {"pitch": 64, "start": 0.2, "duration": 0.3, "step": 0.2},
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = Path(tmpdir) / "preview.wav"
        synthesize_notes_to_wav(notes, wav_path, sample_rate=22050)
        assert wav_path.exists()
        assert wav_path.stat().st_size > 0

        sr, data = wavfile.read(str(wav_path))
        assert sr == 22050
        assert len(data) > 0
        assert np.max(np.abs(data)) > 0
