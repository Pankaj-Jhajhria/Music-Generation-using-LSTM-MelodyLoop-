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


def sample_with_temperature(
    logits: torch.Tensor,
    temperature: float = 0.6,
    top_k: int = 5,
    recent_tokens: Optional[List[int]] = None,
    repetition_penalty: float = 1.0,
    max_jump: Optional[int] = None,
) -> int:
    """
    Sample an index from logits using temperature scaling, top-k filtering,
    repetition penalty, and interval regularization.
    
    - temperature: Controls diversity (0.55-0.65 optimal for melodic coherence).
    - top_k: Restricts candidates to the top-K highest probability options,
             eliminating chaotic tail selections.
    - repetition_penalty: Mildly discourages immediate note looping if > 1.0.
    - max_jump: Mildly penalizes leaps exceeding max_jump semitones.
    """
    if temperature <= 0.05 or top_k == 1:
        return int(torch.argmax(logits, dim=-1).item())

    scaled_logits = logits.clone()

    # 1. Repetition penalty on recent notes
    if recent_tokens and repetition_penalty > 1.0:
        penalty_amount = 0.6 * (repetition_penalty - 1.0)
        for token in set(recent_tokens[-3:]):
            if 0 <= token < len(scaled_logits):
                scaled_logits[token] -= penalty_amount

    # 2. Large interval jump penalty (e.g. leaps > 16 semitones)
    if recent_tokens and max_jump is not None and max_jump > 0:
        last_pitch = recent_tokens[-1]
        for p in range(len(scaled_logits)):
            jump = abs(p - last_pitch)
            if jump > max_jump:
                scaled_logits[p] -= 0.12 * (jump - max_jump)

    # 3. Top-K filtering
    if top_k is not None and 0 < top_k < scaled_logits.shape[-1]:
        val, _ = torch.topk(scaled_logits, top_k)
        scaled_logits = torch.where(
            scaled_logits < val[-1],
            torch.tensor(float("-inf"), device=scaled_logits.device),
            scaled_logits,
        )

    # 4. Temperature scaling & Softmax
    probs = torch.softmax(scaled_logits / max(temperature, 1e-4), dim=-1)
    probs = torch.nan_to_num(probs, nan=1.0 / probs.shape[-1])
    probs_sum = torch.sum(probs)
    if probs_sum > 0:
        probs = probs / probs_sum
        sampled_idx = torch.multinomial(probs, num_samples=1).item()
        return int(sampled_idx)

    return int(torch.argmax(logits, dim=-1).item())


def generate_melody(
    model: MelodyLSTM,
    cfg: Config,
    num_notes: int = 80,
    temperature: float = 0.6,
    pitch_top_k: int = 5,
    dur_top_k: int = 3,
    step_top_k: int = 3,
    seed: int = 42,
    seed_sequence: Optional[List[Dict[str, Any]]] = None,
    device: Optional[str] = None,
    repetition_penalty: float = 1.15,
    max_pitch_jump: int = 16,
) -> List[Dict[str, Any]]:
    """
    Autoregressively generate a sequence of note events using MelodyLSTM.
    
    Supports:
      - Free generation from a classical harmonic cadence.
      - Seeded continuation from a real MIDI phrase (preserves prompt notes).
      - Top-k categorical sampling for pitch, duration, and step.
      - Repetition and interval regularity controls.
    """
    dev = torch.device(device or cfg.device)
    model.eval()
    model.to(dev)

    # Set random seed
    torch.manual_seed(seed)
    np.random.seed(seed)

    generated_notes: List[Dict[str, Any]] = []
    current_events: List[Tuple[int, int, int]] = []
    current_time = 0.0

    # 1. Handle seed sequence (if supplied for phrase continuation)
    if seed_sequence:
        first_start = seed_sequence[0].get("start", 0.0)
        for s in seed_sequence:
            norm_start = max(0.0, s.get("start", current_time) - first_start)
            dur_sec = max(cfg.min_duration, s.get("duration", 0.25))
            step_sec = max(0.0, s.get("step", 0.25))
            p = min(max(int(s.get("pitch", 60)), 0), cfg.pitch_vocab_size - 1)

            note_dict = {
                "pitch": p,
                "start": norm_start,
                "duration": dur_sec,
                "step": step_sec,
                "is_seed": True,
            }
            generated_notes.append(note_dict)

            d_idx = quantize_duration(dur_sec, cfg)
            s_idx = quantize_step(step_sec, cfg)
            current_events.append((p, d_idx, s_idx))
            current_time = norm_start + step_sec

    # 2. If no seed or seed is short, pad context with a classical harmonic cadence (I - IV - V - I)
    if len(current_events) < cfg.seq_length:
        cadence = [
            60, 64, 67, 72,  # C major (I)
            60, 65, 69, 72,  # F major (IV)
            59, 62, 67, 71,  # G major (V)
            60, 64, 67, 72,  # C major (I)
        ]
        needed = cfg.seq_length - len(current_events)
        padding = []
        for i in range(needed):
            pitch = cadence[i % len(cadence)]
            d_idx = quantize_duration(0.35, cfg)
            s_idx = quantize_step(0.25, cfg)
            padding.append((pitch, d_idx, s_idx))
        current_events = padding + current_events

    # 3. Autoregressive generation loop
    recent_pitches = [e[0] for e in current_events[-10:]]

    with torch.no_grad():
        for _ in range(num_notes):
            window_tensor = (
                torch.tensor(current_events[-cfg.seq_length :], dtype=torch.long)
                .unsqueeze(0)
                .to(dev)
            )

            logits_p, logits_d, logits_s, _ = model(window_tensor)

            p_idx = sample_with_temperature(
                logits_p[0],
                temperature=temperature,
                top_k=pitch_top_k,
                recent_tokens=recent_pitches,
                repetition_penalty=repetition_penalty,
                max_jump=max_pitch_jump,
            )
            d_idx = sample_with_temperature(
                logits_d[0],
                temperature=temperature,
                top_k=dur_top_k,
            )
            s_idx = sample_with_temperature(
                logits_s[0],
                temperature=temperature,
                top_k=step_top_k,
            )

            # Clamp indices
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
                "is_seed": False,
            }
            generated_notes.append(note_event)
            recent_pitches.append(p_idx)

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
