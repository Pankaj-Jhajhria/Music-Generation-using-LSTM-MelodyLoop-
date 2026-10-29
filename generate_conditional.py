"""
Standalone CLI entry point for MelodyLoop 2.0 Conditional Music Generation.
Generates condition-adherent MIDI and WAV audio files from text prompts or structured controls.
"""

import argparse
import json
import logging
import time
from pathlib import Path
import torch

from config import Config
from melodyloop.conditional_data import (
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
from melodyloop.conditional_generation import (
    generate_conditional_melody,
    export_conditional_notes_to_midi,
    synthesize_conditional_audio,
)
from melodyloop.prompt_parser import parse_text_prompt

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_conditional")


def main():
    parser = argparse.ArgumentParser(description="MelodyLoop 2.0: Conditional Music Generator")
    parser.add_argument("--prompt", type=str, default="", help="Natural language prompt describing music")
    parser.add_argument("--mood", type=str, default="any", choices=MOOD_VOCAB, help="Requested mood")
    parser.add_argument("--tempo", type=str, default="any", choices=TEMPO_VOCAB, help="Requested tempo")
    parser.add_argument("--register", type=str, default="any", choices=REGISTER_VOCAB, help="Pitch register")
    parser.add_argument("--dynamics", type=str, default="any", choices=DYNAMICS_VOCAB, help="Dynamics intensity")
    parser.add_argument("--length", type=int, default=80, help="Number of notes to generate")
    parser.add_argument("--temperature", type=float, default=0.8, help="Sampling temperature")
    parser.add_argument("--top_k", type=int, default=0, help="Top-k sampling truncation (0 for none)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to conditional model checkpoint")
    parser.add_argument("--output_dir", type=str, default=None, help="Directory to save generated artifacts")
    parser.add_argument("--bpm", type=int, default=120, help="Playback BPM in MIDI metadata")
    args = parser.parse_args()

    cfg = Config()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Locate checkpoint
    if args.checkpoint:
        ckpt_path = Path(args.checkpoint)
    else:
        candidate = cfg.checkpoints_dir / "conditional" / "best_conditional_model.pt"
        if candidate.exists():
            ckpt_path = candidate
        else:
            ckpt_path = cfg.checkpoints_dir / "conditional" / "latest_conditional_model.pt"

    if not ckpt_path.exists():
        logger.error(f"Checkpoint not found at: {ckpt_path}. Please train a conditional model first.")
        return

    logger.info(f"Loading conditional checkpoint: {ckpt_path}")
    checkpoint = torch.load(str(ckpt_path), map_location=device, weights_only=False)

    model = ConditionalMelodyLSTM(
        cfg=cfg,
        velocity_bins=16,
        mood_vocab_size=len(MOOD_VOCAB),
        tempo_vocab_size=len(TEMPO_VOCAB),
        register_vocab_size=len(REGISTER_VOCAB),
        dynamics_vocab_size=len(DYNAMICS_VOCAB),
    ).to(device)

    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    # Condition Resolution: Text prompt vs explicit CLI flags
    parsed_prompt = None
    if args.prompt.strip():
        parsed_prompt = parse_text_prompt(args.prompt)
        logger.info(f"Parsed prompt: \"{args.prompt}\"")
        logger.info(f"  Explicit conditions: {parsed_prompt.explicit_conditions}")
        if parsed_prompt.warnings:
            for w in parsed_prompt.warnings:
                logger.warning(f"  Warning: {w}")

        final_mood = args.mood if args.mood != "any" else parsed_prompt.mood
        final_tempo = args.tempo if args.tempo != "any" else parsed_prompt.tempo
        final_register = args.register if args.register != "any" else parsed_prompt.pitch_register
        final_dynamics = args.dynamics if args.dynamics != "any" else parsed_prompt.dynamics
    else:
        final_mood = args.mood
        final_tempo = args.tempo
        final_register = args.register
        final_dynamics = args.dynamics

    # BPM calibration for playback
    if final_tempo == "slow":
        actual_bpm = 75
    elif final_tempo == "fast":
        actual_bpm = 145
    else:
        actual_bpm = args.bpm

    logger.info("Final Resolved Conditions:")
    logger.info(f"  Mood: {final_mood} (idx {MOOD_TO_IDX.get(final_mood, 0)})")
    logger.info(f"  Tempo: {final_tempo} (idx {TEMPO_TO_IDX.get(final_tempo, 0)}) -> {actual_bpm} BPM")
    logger.info(f"  Pitch Register: {final_register} (idx {REGISTER_TO_IDX.get(final_register, 0)})")
    logger.info(f"  Dynamics: {final_dynamics} (idx {DYNAMICS_TO_IDX.get(final_dynamics, 0)})")

    # Generate melody
    t0 = time.time()
    notes = generate_conditional_melody(
        model=model,
        cfg=cfg,
        condition={
            "mood": final_mood,
            "tempo": final_tempo,
            "pitch_register": final_register,
            "dynamics": final_dynamics,
        },
        length=args.length,
        temperature=args.temperature,
        top_k=args.top_k,
        seed=args.seed,
        device=device,
    )
    gen_time = time.time() - t0
    logger.info(f"Generated {len(notes)} note events in {gen_time:.2f}s")

    # Output paths
    out_dir = Path(args.output_dir) if args.output_dir else cfg.generated_dir / "conditional"
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    base_name = f"gen_cond_{final_mood}_{final_tempo}_{final_register}_{final_dynamics}_{timestamp}"

    midi_path = out_dir / f"{base_name}.mid"
    wav_path = out_dir / f"{base_name}.wav"
    meta_path = out_dir / f"{base_name}_meta.json"

    export_conditional_notes_to_midi(notes, midi_path, tempo_bpm=actual_bpm)
    synthesize_conditional_audio(notes, wav_path)

    metadata = {
        "timestamp": timestamp,
        "prompt": args.prompt,
        "resolved_conditions": {
            "mood": final_mood,
            "tempo": final_tempo,
            "pitch_register": final_register,
            "dynamics": final_dynamics,
        },
        "bpm": actual_bpm,
        "length": len(notes),
        "temperature": args.temperature,
        "top_k": args.top_k,
        "seed": args.seed,
        "checkpoint": str(ckpt_path),
        "midi_file": str(midi_path),
        "wav_file": str(wav_path),
        "notes_sample": notes[:5],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Saved MIDI to: {midi_path}")
    logger.info(f"Saved WAV preview to: {wav_path}")
    logger.info(f"Saved Metadata to: {meta_path}")


if __name__ == "__main__":
    main()
