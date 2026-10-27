"""
Melody generation module for MelodyLoop.
Implements autoregressive next-event sampling with temperature and MIDI conversion.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import mido
import numpy as np
import torch

from config import Config
from melodyloop.data import (
    dequantize_duration,
    dequantize_step,
    quantize_duration,
    quantize_step,
)
from melodyloop.model import MelodyLSTM


def sample_with_temperature(logits: torch.Tensor, temperature: float = 1.0) -> int:
    """
    Sample an index from logits using temperature scaling.
    Low temperature (<0.2) approaches argmax / greedy sampling.
    """
    if temperature <= 0.05:
        return int(torch.argmax(logits, dim=-1).item())

    scaled_logits = logits / max(temperature, 1e-4)
    probs = torch.softmax(scaled_logits, dim=-1)
    # Numerical stability check
    probs = torch.nan_to_num(probs, nan=1.0 / probs.shape[-1])
    probs = probs / torch.sum(probs)
    sampled_idx = torch.multinomial(probs, num_samples=1).item()
    return int(sampled_idx)


def generate_melody(
    model: MelodyLSTM,
    cfg: Config,
    num_notes: int = 100,
    temperature: float = 0.9,
    seed: int = 42,
    seed_sequence: Optional[List[Dict[str, Any]]] = None,
    device: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Autoregressively generate a sequence of note events using MelodyLSTM.
    Returns a list of note dicts: [{'pitch': int, 'start': float, 'duration': float, 'step': float}, ...]
    """
    dev = torch.device(device or cfg.device)
    model.eval()
    model.to(dev)

    # Set random seed
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Construct initial seed context
    if seed_sequence is not None and len(seed_sequence) >= cfg.seq_length:
        current_events = [
            (
                s["pitch"],
                quantize_duration(s["duration"], cfg),
                quantize_step(s["step"], cfg),
            )
            for s in seed_sequence[-cfg.seq_length :]
        ]
    else:
        # Default educational seed: Gentle ascending piano arpeggio (C4, E4, G4, B4, C5)
        arpeggio = [60, 64, 67, 71, 72]
        current_events = []
        for i in range(cfg.seq_length):
            pitch = arpeggio[i % len(arpeggio)]
            dur_idx = quantize_duration(0.4, cfg)
            step_idx = quantize_step(0.25, cfg)
            current_events.append((pitch, dur_idx, step_idx))

    generated_notes: List[Dict[str, Any]] = []
    current_time = 0.0

    with torch.no_grad():
        for _ in range(num_notes):
            # Input window of shape (1, seq_length, 3)
            window_tensor = (
                torch.tensor(current_events[-cfg.seq_length :], dtype=torch.long)
                .unsqueeze(0)
                .to(dev)
            )

            logits_p, logits_d, logits_s, _ = model(window_tensor)

            p_idx = sample_with_temperature(logits_p[0], temperature)
            d_idx = sample_with_temperature(logits_d[0], temperature)
            s_idx = sample_with_temperature(logits_s[0], temperature)

            # Clamp indices safely
            p_idx = min(max(p_idx, 0), cfg.pitch_vocab_size - 1)
            d_idx = min(max(d_idx, 0), cfg.duration_bins - 1)
            s_idx = min(max(s_idx, 0), cfg.step_bins - 1)

            dur_sec = dequantize_duration(d_idx, cfg)
            step_sec = dequantize_step(s_idx, cfg)

            note_event = {
                "pitch": p_idx,
                "start": current_time,
                "duration": dur_sec,
                "step": step_sec,
            }
            generated_notes.append(note_event)

            # Advance current time by step
            current_time += step_sec

            # Append to history for next autoregressive step
            current_events.append((p_idx, d_idx, s_idx))

    return generated_notes


def export_notes_to_midi(
    notes: List[Dict[str, Any]],
    output_path: Path | str,
    bpm: int = 120,
    ticks_per_beat: int = 480,
) -> Path:
    """
    Convert a list of note events into a valid Standard MIDI File (.mid).
    Handles note timing, note-on and note-off events, and overlapping chords.
    """
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Add tempo meta message
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    track.append(mido.MetaMessage("track_name", name="MelodyLoop Piano", time=0))

    if not notes:
        mid.save(str(out_p))
        return out_p

    # Convert seconds to ticks: ticks_per_second = (bpm / 60.0) * ticks_per_beat
    ticks_per_sec = (bpm / 60.0) * ticks_per_beat

    events = []
    for n in notes:
        pitch = int(min(max(n["pitch"], 0), 127))
        start_tick = int(round(n["start"] * ticks_per_sec))
        end_tick = int(round((n["start"] + max(0.05, n["duration"])) * ticks_per_sec))
        events.append({"type": "note_on", "note": pitch, "vel": 85, "tick": start_tick})
        events.append({"type": "note_off", "note": pitch, "vel": 64, "tick": end_tick})

    # Sort events strictly by tick time. If same tick, note_off comes before note_on
    events.sort(key=lambda e: (e["tick"], 0 if e["type"] == "note_off" else 1))

    # Convert absolute tick times to delta times between consecutive events
    last_tick = 0
    for e in events:
        delta = max(0, e["tick"] - last_tick)
        track.append(mido.Message(e["type"], note=e["note"], velocity=e["vel"], time=delta))
        last_tick = e["tick"]

    # End of track
    track.append(mido.MetaMessage("end_of_track", time=0))
    mid.save(str(out_p))
    return out_p
