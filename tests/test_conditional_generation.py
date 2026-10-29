"""
Unit tests for conditional music generation, MIDI export, and audio synthesis.
"""

import tempfile
from pathlib import Path
import mido
from scipy.io import wavfile
import torch
import pytest

from config import Config
from melodyloop.conditional_model import ConditionalMelodyLSTM
from melodyloop.conditional_generation import (
    initialize_seed_sequence,
    generate_conditional_melody,
    export_conditional_notes_to_midi,
    synthesize_conditional_audio,
)


def test_seed_sequence_initialization():
    cfg = Config()
    # Low register seed
    low_seed = initialize_seed_sequence(cfg, register="low", dynamics="soft", seq_length=16)
    assert len(low_seed) == 16
    assert low_seed[0][0] < 60  # Low pitch

    # High register seed
    high_seed = initialize_seed_sequence(cfg, register="high", dynamics="strong", seq_length=16)
    assert len(high_seed) == 16
    assert high_seed[0][0] >= 70  # High pitch


def test_conditional_generation_outputs():
    cfg = Config()
    model = ConditionalMelodyLSTM(cfg)
    model.eval()

    condition = {"mood": "calm", "tempo": "slow", "pitch_register": "middle", "dynamics": "soft"}
    notes = generate_conditional_melody(
        model=model,
        cfg=cfg,
        condition=condition,
        length=20,
        temperature=0.8,
        seed=42,
    )

    assert len(notes) == 20
    for n in notes:
        assert 0 <= n["pitch"] < 128
        assert n["duration"] > 0
        assert n["start"] >= 0
        assert 1 <= n["velocity"] <= 127


def test_midi_and_audio_export():
    notes = [
        {"pitch": 60, "start": 0.0, "duration": 0.4, "velocity": 45, "step": 0.25},
        {"pitch": 64, "start": 0.25, "duration": 0.4, "velocity": 75, "step": 0.25},
        {"pitch": 67, "start": 0.50, "duration": 0.4, "velocity": 110, "step": 0.5},
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        midi_path = Path(tmpdir) / "output.mid"
        wav_path = Path(tmpdir) / "output.wav"

        export_conditional_notes_to_midi(notes, midi_path, tempo_bpm=100)
        assert midi_path.exists()
        mid = mido.MidiFile(str(midi_path))
        assert len(mid.tracks) >= 1
        note_msgs = [m for m in mid.tracks[0] if m.type in ("note_on", "note_off")]
        assert len(note_msgs) == 6  # 3 notes * 2 (on and off)

        synthesize_conditional_audio(notes, wav_path)
        assert wav_path.exists()
        sr, audio_data = wavfile.read(str(wav_path))
        assert sr == 44100
        assert len(audio_data) > 0
