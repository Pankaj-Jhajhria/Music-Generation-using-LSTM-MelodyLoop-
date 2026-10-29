"""
Evaluation script for MelodyLoop 2.0 Condition Adherence.
Rigorously evaluates whether generated symbolic musical events adhere to requested
tempo, pitch register, dynamics, and mood conditions across multiple seeds.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import torch

from config import Config
from melodyloop.conditional_data import (
    MOOD_VOCAB,
    TEMPO_VOCAB,
    REGISTER_VOCAB,
    DYNAMICS_VOCAB,
    determine_register,
    determine_dynamics,
)
from melodyloop.conditional_model import ConditionalMelodyLSTM
from melodyloop.conditional_generation import generate_conditional_melody

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("evaluate_conditional")


def evaluate_register_adherence(
    model: ConditionalMelodyLSTM,
    cfg: Config,
    device: torch.device,
    num_runs: int = 10,
    length: int = 60,
) -> Dict[str, Any]:
    """Evaluate adherence to low, middle, and high pitch registers."""
    results = {}
    for target_reg in ["low", "middle", "high"]:
        medians = []
        means = []
        p25s = []
        p75s = []
        min_ps = []
        max_ps = []
        matches = 0

        for seed in range(num_runs):
            notes = generate_conditional_melody(
                model=model,
                cfg=cfg,
                condition={"mood": "any", "tempo": "any", "pitch_register": target_reg, "dynamics": "any"},
                length=length,
                seed=seed * 100 + 42,
                device=device,
            )
            pitches = [n["pitch"] for n in notes]
            med = float(np.median(pitches))
            mean_val = float(np.mean(pitches))
            medians.append(med)
            means.append(mean_val)
            p25s.append(float(np.percentile(pitches, 25)))
            p75s.append(float(np.percentile(pitches, 75)))
            min_ps.append(min(pitches))
            max_ps.append(max(pitches))

            derived = determine_register(pitches)
            if derived == target_reg:
                matches += 1

        results[target_reg] = {
            "target": target_reg,
            "mean_pitch": round(float(np.mean(means)), 1),
            "median_pitch": round(float(np.mean(medians)), 1),
            "p25_pitch": round(float(np.mean(p25s)), 1),
            "p75_pitch": round(float(np.mean(p75s)), 1),
            "overall_min_pitch": int(min(min_ps)),
            "overall_max_pitch": int(max(max_ps)),
            "adherence_rate": round(matches / num_runs, 2),
        }
    return results


def evaluate_dynamics_adherence(
    model: ConditionalMelodyLSTM,
    cfg: Config,
    device: torch.device,
    num_runs: int = 10,
    length: int = 60,
) -> Dict[str, Any]:
    """Evaluate adherence to soft, medium, and strong dynamics."""
    results = {}
    for target_dyn in ["soft", "medium", "strong"]:
        medians = []
        means = []
        p25s = []
        p75s = []
        matches = 0

        for seed in range(num_runs):
            notes = generate_conditional_melody(
                model=model,
                cfg=cfg,
                condition={"mood": "any", "tempo": "any", "pitch_register": "any", "dynamics": target_dyn},
                length=length,
                seed=seed * 100 + 42,
                device=device,
            )
            vels = [n["velocity"] for n in notes]
            med = float(np.median(vels))
            mean_val = float(np.mean(vels))
            medians.append(med)
            means.append(mean_val)
            p25s.append(float(np.percentile(vels, 25)))
            p75s.append(float(np.percentile(vels, 75)))

            derived = determine_dynamics(vels)
            if derived == target_dyn:
                matches += 1

        results[target_dyn] = {
            "target": target_dyn,
            "mean_velocity": round(float(np.mean(means)), 1),
            "median_velocity": round(float(np.mean(medians)), 1),
            "p25_velocity": round(float(np.mean(p25s)), 1),
            "p75_velocity": round(float(np.mean(p75s)), 1),
            "adherence_rate": round(matches / num_runs, 2),
        }
    return results


def evaluate_tempo_adherence(
    model: ConditionalMelodyLSTM,
    cfg: Config,
    device: torch.device,
    num_runs: int = 10,
    length: int = 60,
) -> Dict[str, Any]:
    """Evaluate adherence to slow, moderate, and fast tempo."""
    results = {}
    for target_tempo in ["slow", "moderate", "fast"]:
        densities = []
        mean_steps = []
        median_steps = []
        total_durations = []
        matches = 0

        for seed in range(num_runs):
            notes = generate_conditional_melody(
                model=model,
                cfg=cfg,
                condition={"mood": "any", "tempo": target_tempo, "pitch_register": "any", "dynamics": "any"},
                length=length,
                seed=seed * 100 + 42,
                device=device,
            )
            total_dur = notes[-1]["start"] + notes[-1]["duration"]
            total_durations.append(total_dur)
            density = len(notes) / max(total_dur, 1e-4)  # notes per second
            densities.append(density)
            steps = [n["step"] for n in notes]
            mean_step = float(np.mean(steps))
            med_step = float(np.median(steps))
            mean_steps.append(mean_step)
            median_steps.append(med_step)

            # Classify speed based on onset step and density
            if target_tempo == "slow" and (mean_step >= 0.25 or density <= 4.0):
                matches += 1
            elif target_tempo == "moderate" and (0.10 <= mean_step <= 0.25 or 4.0 < density <= 8.5):
                matches += 1
            elif target_tempo == "fast" and (mean_step < 0.12 or density > 8.5):
                matches += 1

        results[target_tempo] = {
            "target": target_tempo,
            "mean_step_sec": round(float(np.mean(mean_steps)), 3),
            "median_step_sec": round(float(np.mean(median_steps)), 3),
            "notes_per_second": round(float(np.mean(densities)), 2),
            "avg_sequence_duration_sec": round(float(np.mean(total_durations)), 1),
            "adherence_rate": round(matches / num_runs, 2),
        }
    return results


def evaluate_mood_profiles(
    model: ConditionalMelodyLSTM,
    cfg: Config,
    device: torch.device,
    num_runs: int = 3,
    length: int = 60,
) -> Dict[str, Any]:
    """Profile musical features across different mood conditions."""
    results = {}
    moods_to_test = ["calm", "happy", "sad", "energetic", "dramatic", "romantic"]
    for mood in moods_to_test:
        pitch_vars = []
        vel_means = []
        densities = []

        for seed in range(num_runs):
            notes = generate_conditional_melody(
                model=model,
                cfg=cfg,
                condition={"mood": mood, "tempo": "any", "pitch_register": "any", "dynamics": "any"},
                length=length,
                seed=seed * 100 + 42,
                device=device,
            )
            pitches = [n["pitch"] for n in notes]
            vels = [n["velocity"] for n in notes]
            total_dur = notes[-1]["start"] + notes[-1]["duration"]
            density = len(notes) / max(total_dur, 1e-4)

            pitch_vars.append(float(np.std(pitches)))
            vel_means.append(float(np.mean(vels)))
            densities.append(density)

        results[mood] = {
            "pitch_std": round(float(np.mean(pitch_vars)), 2),
            "mean_velocity": round(float(np.mean(vel_means)), 1),
            "notes_per_second": round(float(np.mean(densities)), 2),
        }
    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate MelodyLoop Conditional Adherence")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to checkpoint")
    parser.add_argument("--num_runs", type=int, default=5, help="Number of seeds per condition")
    parser.add_argument("--length", type=int, default=60, help="Notes per evaluation piece")
    parser.add_argument("--output", type=str, default="artifacts/conditional_evaluation_results.json")
    args = parser.parse_args()

    cfg = Config()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    ckpt_path = Path(args.checkpoint) if args.checkpoint else cfg.checkpoints_dir / "conditional" / "best_conditional_model.pt"
    if not ckpt_path.exists():
        ckpt_path = cfg.checkpoints_dir / "conditional" / "latest_conditional_model.pt"

    if not ckpt_path.exists():
        logger.error(f"Checkpoint not found at: {ckpt_path}")
        return

    logger.info(f"Loading checkpoint: {ckpt_path}")
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

    logger.info("Evaluating Pitch Register Adherence...")
    reg_results = evaluate_register_adherence(model, cfg, device, num_runs=args.num_runs, length=args.length)

    logger.info("Evaluating Dynamics Adherence...")
    dyn_results = evaluate_dynamics_adherence(model, cfg, device, num_runs=args.num_runs, length=args.length)

    logger.info("Evaluating Tempo Adherence...")
    tempo_results = evaluate_tempo_adherence(model, cfg, device, num_runs=args.num_runs, length=args.length)

    logger.info("Profiling Mood Conditions...")
    mood_results = evaluate_mood_profiles(model, cfg, device, num_runs=3, length=args.length)

    report = {
        "checkpoint": str(ckpt_path),
        "evaluation_settings": {
            "num_runs_per_condition": args.num_runs,
            "sequence_length": args.length,
            "device": str(device),
        },
        "register_adherence": reg_results,
        "dynamics_adherence": dyn_results,
        "tempo_adherence": tempo_results,
        "mood_profiles": mood_results,
    }

    out_p = Path(args.output)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Evaluation report saved to: {out_p}")

    # Print clean summary table
    print("\n" + "=" * 70)
    print("CONDITION ADHERENCE EVALUATION SUMMARY")
    print("=" * 70)
    print("\n1. Pitch Register Adherence:")
    print(f"{'Target':<10} | {'Mean Pitch':<12} | {'Median Pitch':<14} | {'Pitch Range':<13} | {'Adherence':<10}")
    print("-" * 68)
    for k, v in reg_results.items():
        prange = f"{v['overall_min_pitch']}-{v['overall_max_pitch']}"
        print(f"{k:<10} | {v['mean_pitch']:<12} | {v['median_pitch']:<14} | {prange:<13} | {v['adherence_rate']*100:.0f}%")

    print("\n2. Dynamics Adherence:")
    print(f"{'Target':<10} | {'Mean Velocity':<14} | {'Median Vel':<12} | {'Adherence':<10}")
    print("-" * 55)
    for k, v in dyn_results.items():
        print(f"{k:<10} | {v['mean_velocity']:<14} | {v['median_velocity']:<12} | {v['adherence_rate']*100:.0f}%")

    print("\n3. Tempo Adherence:")
    print(f"{'Target':<10} | {'Mean Step (s)':<14} | {'Median Step':<12} | {'Notes / sec':<12} | {'Adherence':<10}")
    print("-" * 68)
    for k, v in tempo_results.items():
        print(f"{k:<10} | {v['mean_step_sec']:<14} | {v['median_step_sec']:<12} | {v['notes_per_second']:<12} | {v['adherence_rate']*100:.0f}%")

    print("\n4. Mood Profiles:")
    print(f"{'Mood':<12} | {'Pitch StdDev':<14} | {'Mean Vel':<10} | {'Notes / sec':<12}")
    print("-" * 55)
    for k, v in mood_results.items():
        print(f"{k:<12} | {v['pitch_std']:<14} | {v['mean_velocity']:<10} | {v['notes_per_second']}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

