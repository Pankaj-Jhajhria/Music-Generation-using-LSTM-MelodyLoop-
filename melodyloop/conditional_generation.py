"""
Generation pipeline for MelodyLoop 2.0.
Condition-aware autoregressive music generation, velocity-sensitive MIDI export,
and audio rendering.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union
import json
import logging
import mido
import numpy as np
import torch
import torch.nn.functional as F

from config import Config
from melodyloop.conditional_data import (
    dequantize_velocity,
    MOOD_VOCAB,
    TEMPO_VOCAB,
    REGISTER_VOCAB,
    DYNAMICS_VOCAB,
    MOOD_TO_IDX,
    TEMPO_TO_IDX,
    REGISTER_TO_IDX,
    DYNAMICS_TO_IDX,
)
from melodyloop.conditional_model import ConditionalMelodyLSTM
from melodyloop.data import dequantize_duration, dequantize_step
from melodyloop.audio import synthesize_notes_to_wav

logger = logging.getLogger(__name__)


def sample_with_temperature(
    logits: torch.Tensor,
    temperature: float = 1.0,
    top_k: int = 0,
) -> int:
    """
    Sample an index from logits using temperature scaling and optional top-k truncation.
    """
    if temperature <= 0.01:
        return int(torch.argmax(logits).item())

    scaled_logits = logits / max(temperature, 1e-4)

    if top_k > 0 and top_k < scaled_logits.size(-1):
        topk_vals, _ = torch.topk(scaled_logits, top_k)
        min_topk = topk_vals[-1]
        scaled_logits = torch.where(
            scaled_logits < min_topk,
            torch.full_like(scaled_logits, -float("inf")),
            scaled_logits,
        )

    probs = F.softmax(scaled_logits, dim=-1)
    sampled = torch.multinomial(probs, num_samples=1)
    return int(sampled.item())


def initialize_seed_sequence(
    cfg: Config,
    register: str = "middle",
    dynamics: str = "medium",
    tempo: str = "moderate",
    seq_length: int = 32,
) -> List[Tuple[int, int, int, int]]:
    """
    Generate an initial seed event sequence consistent with the requested register, dynamics, and tempo.
    Each event is (pitch, duration_bin, step_bin, velocity_bin).
    """
    from melodyloop.conditional_data import quantize_velocity
    from melodyloop.data import quantize_duration, quantize_step

    # 1. Pitch Register Root & Scale
    if register == "low":
        base_pitch = 38  # D2 bass octave
        scale_offsets = [0, 2, 3, 5, 7, 5, 3, 2]  # Natural minor bass contour
    elif register == "high":
        base_pitch = 74  # D5 treble octave
        scale_offsets = [0, 2, 4, 7, 9, 7, 4, 2]  # Pentatonic soprano contour
    else:
        base_pitch = 62  # D4 central keyboard range
        scale_offsets = [0, 2, 4, 5, 7, 5, 4, 2]  # Central diatonic contour

    # 2. Dynamics Velocity Root
    if dynamics == "soft":
        base_vel = 45  # piano (p)
    elif dynamics == "strong":
        base_vel = 110  # forte (f)
    else:
        base_vel = 80  # mezzo-forte (mf)

    # 3. Tempo Timing Root
    if tempo == "fast":
        base_step = 0.10
        base_dur = 0.15
    elif tempo == "slow":
        base_step = 0.38
        base_dur = 0.50
    else:
        base_step = 0.20
        base_dur = 0.30

    d_bin = quantize_duration(base_dur, cfg)
    s_bin = quantize_step(base_step, cfg)
    v_bin = quantize_velocity(base_vel, num_bins=16)

    events: List[Tuple[int, int, int, int]] = []
    for i in range(seq_length):
        offset = scale_offsets[i % len(scale_offsets)]
        p = min(max(base_pitch + offset, 0), cfg.pitch_vocab_size - 1)
        events.append((p, d_bin, s_bin, v_bin))

    return events


def generate_conditional_melody(
    model: ConditionalMelodyLSTM,
    cfg: Config,
    condition: Union[Tuple[int, int, int, int], List[int], Dict[str, str]],
    length: int = 80,
    temperature: float = 0.75,
    top_k: int = 6,
    seed: Optional[int] = None,
    seed_events: Optional[List[Tuple[int, int, int, int]]] = None,
    device: Optional[torch.device] = None,
) -> List[Dict[str, Any]]:
    """
    Generate an autoregressive melody conditioned on (mood, tempo, register, dynamics).
    Applies gentle condition anchoring to prevent autoregressive drift.
    Returns a list of note dictionaries:
      {"pitch": int, "start": float, "duration": float, "velocity": int, "step": float}
    """
    if seed is not None:
        torch.manual_seed(seed)
        np.random.seed(seed)

    if device is None:
        device = next(model.parameters()).device

    model.eval()

    # Parse condition input
    if isinstance(condition, dict):
        cond_indices = [
            MOOD_TO_IDX.get(condition.get("mood", "any"), 0),
            TEMPO_TO_IDX.get(condition.get("tempo", "any"), 0),
            REGISTER_TO_IDX.get(condition.get("pitch_register", "any"), 0),
            DYNAMICS_TO_IDX.get(condition.get("dynamics", "any"), 0),
        ]
    else:
        cond_indices = list(condition)

    cond_tensor = torch.tensor([cond_indices], dtype=torch.long, device=device)

    # Resolve register, dynamics, and tempo strings for initial seed
    tempo_str = TEMPO_VOCAB[cond_indices[1]] if cond_indices[1] < len(TEMPO_VOCAB) else "moderate"
    reg_str = REGISTER_VOCAB[cond_indices[2]] if cond_indices[2] < len(REGISTER_VOCAB) else "middle"
    dyn_str = DYNAMICS_VOCAB[cond_indices[3]] if cond_indices[3] < len(DYNAMICS_VOCAB) else "medium"

    if seed_events is None or len(seed_events) < cfg.seq_length:
        running_events = initialize_seed_sequence(
            cfg=cfg,
            register=reg_str,
            dynamics=dyn_str,
            tempo=tempo_str,
            seq_length=cfg.seq_length,
        )
    else:
        running_events = list(seed_events[-cfg.seq_length :])

    generated_events: List[Tuple[int, int, int, int]] = []
    pitches_all = torch.arange(cfg.pitch_vocab_size, dtype=torch.float32, device=device)
    vels_all = torch.arange(16, dtype=torch.float32, device=device)

    with torch.no_grad():
        for _ in range(length):
            # Input window: (1, seq_length, 4)
            window = running_events[-cfg.seq_length :]
            x = torch.tensor([window], dtype=torch.long, device=device)

            lp, ld, ls, lv, _ = model(x, cond_tensor)

            # Gentle register prior shaping to prevent autoregressive drift
            logits_p = lp[0].clone()
            if reg_str == "low":
                logits_p -= 0.28 * torch.clamp(pitches_all - 58.0, min=0.0)
            elif reg_str == "high":
                logits_p -= 0.28 * torch.clamp(68.0 - pitches_all, min=0.0)
            elif reg_str == "middle":
                logits_p -= 0.15 * torch.clamp(pitches_all - 71.0, min=0.0)
                logits_p -= 0.15 * torch.clamp(58.0 - pitches_all, min=0.0)

            # Gentle dynamics prior shaping
            logits_v = lv[0].clone()
            if dyn_str == "soft":
                logits_v -= 0.35 * torch.clamp(vels_all - 8.0, min=0.0)
            elif dyn_str == "strong":
                logits_v -= 0.35 * torch.clamp(10.0 - vels_all, min=0.0)

            # Sample next attributes
            p_idx = sample_with_temperature(logits_p, temperature=temperature, top_k=top_k)
            d_idx = sample_with_temperature(ld[0], temperature=temperature, top_k=top_k)
            s_idx = sample_with_temperature(ls[0], temperature=temperature, top_k=top_k)
            v_idx = sample_with_temperature(logits_v, temperature=temperature, top_k=top_k)

            # Ensure valid bounds
            p_idx = min(max(p_idx, 0), cfg.pitch_vocab_size - 1)
            d_idx = min(max(d_idx, 0), cfg.duration_bins - 1)
            s_idx = min(max(s_idx, 0), cfg.step_bins - 1)
            v_idx = min(max(v_idx, 0), 15)

            new_event = (p_idx, d_idx, s_idx, v_idx)
            running_events.append(new_event)
            generated_events.append(new_event)

    # Decode discrete tokens to continuous note events
    notes: List[Dict[str, Any]] = []
    current_time = 0.0

    # Timing calibration based on requested tempo
    if tempo_str == "slow":
        step_multiplier = 1.45
        min_step = 0.15
        max_step = 1.60
    elif tempo_str == "fast":
        step_multiplier = 0.65
        min_step = 0.04
        max_step = 0.24
    else:
        step_multiplier = 1.00
        min_step = 0.05
        max_step = 0.80

    for p_idx, d_idx, s_idx, v_idx in generated_events:
        dur = dequantize_duration(d_idx, cfg)
        raw_step = dequantize_step(s_idx, cfg) * step_multiplier
        step = min(max(raw_step, min_step), max_step)
        vel = dequantize_velocity(v_idx, num_bins=16)

        notes.append({
            "pitch": int(p_idx),
            "start": round(current_time, 4),
            "duration": round(dur, 4),
            "velocity": int(vel),
            "step": round(step, 4),
        })
        current_time += step

    return notes


def export_conditional_notes_to_midi(
    notes: List[Dict[str, Any]],
    output_path: Union[Path, str],
    tempo_bpm: int = 120,
) -> Path:
    """
    Export generated notes with velocity to a valid Standard MIDI File (Format 0).
    """
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    ticks_per_beat = 480
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Set Tempo & Instrument (Acoustic Grand Piano, GM 0)
    microsec_per_beat = mido.bpm2tempo(tempo_bpm)
    track.append(mido.MetaMessage("set_tempo", tempo=microsec_per_beat, time=0))
    track.append(mido.Message("program_change", channel=0, program=0, time=0))

    if not notes:
        mid.save(str(out_p))
        return out_p

    # Convert notes to timestamped on/off events
    events: List[Tuple[float, str, int, int]] = []
    for n in notes:
        p = min(max(int(n["pitch"]), 0), 127)
        v = min(max(int(n.get("velocity", 80)), 1), 127)
        st = n["start"]
        et = st + max(0.05, n["duration"])
        events.append((st, "note_on", p, v))
        events.append((et, "note_off", p, 0))

    # Sort events chronologically, note_off before note_on if simultaneous
    events.sort(key=lambda x: (x[0], 0 if x[1] == "note_off" else 1, x[2]))

    # Convert absolute seconds to delta ticks
    sec_per_tick = (60.0 / tempo_bpm) / ticks_per_beat
    last_tick = 0

    for time_sec, msg_type, pitch, vel in events:
        target_tick = int(time_sec / sec_per_tick)
        delta_tick = max(0, target_tick - last_tick)
        last_tick = target_tick
        track.append(mido.Message(msg_type, note=pitch, velocity=vel, time=delta_tick))

    mid.save(str(out_p))
    return out_p


def synthesize_conditional_audio(
    notes: List[Dict[str, Any]],
    output_path: Union[Path, str],
    sample_rate: int = 44100,
) -> Path:
    """
    Synthesize notes to a 16-bit mono WAV file with velocity-sensitive dynamics.
    Higher velocity yields stronger amplitude and richer harmonic timbre.
    """
    from scipy.io import wavfile

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not notes:
        wavfile.write(str(out_p), sample_rate, np.zeros(sample_rate, dtype=np.int16))
        return out_p

    max_end = max(n["start"] + n["duration"] for n in notes)
    total_length = max_end + 0.6  # 0.6s reverb tail
    total_samples = int(total_length * sample_rate)
    audio = np.zeros(total_samples, dtype=np.float32)

    for n in notes:
        pitch = n["pitch"]
        start_sec = n["start"]
        dur_sec = max(0.05, n["duration"])
        vel = n.get("velocity", 80)

        # Dynamic gain based on MIDI velocity (1-127)
        # Power curve: soft velocities (~40) produce ~0.3 amplitude, strong (~110) produce ~0.9
        gain = ((vel / 127.0) ** 1.2) * 0.85

        freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))
        start_idx = int(start_sec * sample_rate)
        note_samples = int(dur_sec * sample_rate)
        end_idx = min(start_idx + note_samples, total_samples)
        actual_len = end_idx - start_idx

        if actual_len <= 0:
            continue

        t = np.arange(actual_len) / sample_rate

        # Richer harmonic content at higher velocities (striking harder generates more overtones)
        h2_weight = 0.20 + 0.15 * (vel / 127.0)
        h3_weight = 0.10 + 0.12 * (vel / 127.0)
        waveform = (
            0.65 * np.sin(2 * np.pi * freq * t)
            + h2_weight * np.sin(2 * np.pi * (2 * freq) * t)
            + h3_weight * np.sin(2 * np.pi * (3 * freq) * t)
        )

        # ADSR Envelope
        attack_len = min(int(0.005 * sample_rate), actual_len)
        decay_factor = 2.5 + 1.0 * (1.0 - vel / 127.0)
        envelope = np.exp(-decay_factor * t / max(dur_sec, 0.1))
        if attack_len > 0:
            envelope[:attack_len] *= np.linspace(0.0, 1.0, attack_len)

        release_len = min(int(0.01 * sample_rate), actual_len)
        if release_len > 0:
            envelope[-release_len:] *= np.linspace(1.0, 0.0, release_len)

        audio[start_idx:end_idx] += waveform * envelope * gain

    # Safety ceiling: prevent digital clipping without destroying velocity dynamics contrast.
    # We do NOT normalize every piece to peak 0.90 because that would artificially boost soft pieces.
    max_val = float(np.max(np.abs(audio)))
    if max_val > 0.92:
        audio = (audio / max_val) * 0.92

    audio_int16 = (audio * 32767.0).astype(np.int16)
    wavfile.write(str(out_p), sample_rate, audio_int16)
    return out_p

