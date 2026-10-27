"""
Lightweight Audio Synthesis for MelodyLoop.
Generates WAV audio preview directly from note events using additive synthesis.
Runs locally with zero external dependencies (pure NumPy and SciPy).
"""

from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from scipy.io import wavfile


def synthesize_notes_to_wav(
    notes: List[Dict[str, float]],
    output_path: Path | str,
    sample_rate: int = 44100,
) -> Path:
    """
    Synthesize a list of note events to a 16-bit mono WAV file.
    Each note dict must contain:
        - 'pitch': MIDI note number (0-127)
        - 'start': start time in seconds
        - 'duration': duration in seconds
    """
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not notes:
        # Generate 1 second of silence if empty
        wavfile.write(str(out_p), sample_rate, np.zeros(sample_rate, dtype=np.int16))
        return out_p

    max_end = max(n["start"] + n["duration"] for n in notes)
    total_length = max_end + 0.5  # 0.5s reverb tail
    total_samples = int(total_length * sample_rate)
    audio = np.zeros(total_samples, dtype=np.float32)

    for n in notes:
        pitch = n["pitch"]
        start_sec = n["start"]
        dur_sec = max(0.05, n["duration"])

        # Convert MIDI pitch to frequency in Hz
        freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))

        start_idx = int(start_sec * sample_rate)
        note_samples = int(dur_sec * sample_rate)
        end_idx = min(start_idx + note_samples, total_samples)
        actual_len = end_idx - start_idx

        if actual_len <= 0:
            continue

        t = np.arange(actual_len) / sample_rate

        # Additive synthesis: Fundamental + 2nd & 3rd harmonics for warm piano-like timbre
        waveform = (
            0.60 * np.sin(2 * np.pi * freq * t)
            + 0.25 * np.sin(2 * np.pi * (2 * freq) * t)
            + 0.15 * np.sin(2 * np.pi * (3 * freq) * t)
        )

        # ADSR Envelope: Fast 5ms attack, exponential natural decay
        attack_len = min(int(0.005 * sample_rate), actual_len)
        envelope = np.exp(-3.0 * t / max(dur_sec, 0.1))
        if attack_len > 0:
            envelope[:attack_len] *= np.linspace(0.0, 1.0, attack_len)

        # Smooth release at the very end to prevent clicking
        release_len = min(int(0.01 * sample_rate), actual_len)
        if release_len > 0:
            envelope[-release_len:] *= np.linspace(1.0, 0.0, release_len)

        audio[start_idx:end_idx] += waveform * envelope

    # Peak normalization to prevent clipping
    max_val = np.max(np.abs(audio))
    if max_val > 1e-4:
        audio = (audio / max_val) * 0.90

    # Convert to 16-bit PCM integer
    audio_int16 = (audio * 32767.0).astype(np.int16)
    wavfile.write(str(out_p), sample_rate, audio_int16)

    return out_p
