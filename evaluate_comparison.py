"""
MelodyLoop Evaluation and Musical Comparison Script.
Generates comparable melodies and seeded continuations from both:
1. Baseline model (trained on limited 13-performance dataset)
2. Expanded model (trained on 962 MAESTRO performances, 100k sequences)
Computes musical statistics (pitch range, jumps, repetition rate, duration, steps)
and compares against real held-out MAESTRO ground-truth performances.
"""

from pathlib import Path
import json
import numpy as np
import torch
import pandas as pd

from config import Config
from melodyloop.audio import synthesize_notes_to_wav
from melodyloop.data import parse_midi_file, dequantize_duration, dequantize_step
from melodyloop.generation import generate_melody, export_notes_to_midi
from melodyloop.model import MelodyLSTM


def compute_musical_metrics(notes: list[dict]) -> dict:
    """Compute quantifiable musical characteristics from note events."""
    if not notes:
        return {}

    pitches = [n["pitch"] for n in notes]
    durations = [n["duration"] for n in notes]
    steps = [n["step"] for n in notes]

    # Pitch jumps between consecutive notes
    jumps = [abs(pitches[i] - pitches[i - 1]) for i in range(1, len(pitches))]
    repeated_count = sum(1 for j in jumps if j == 0)
    rep_rate = (repeated_count / max(len(jumps), 1)) * 100.0

    return {
        "num_notes": len(notes),
        "pitch_min": int(np.min(pitches)),
        "pitch_max": int(np.max(pitches)),
        "pitch_range": int(np.max(pitches) - np.min(pitches)),
        "pitch_unique": int(len(set(pitches))),
        "pitch_mean": float(np.mean(pitches)),
        "pitch_std": float(np.std(pitches)),
        "avg_pitch_jump": float(np.mean(jumps)) if jumps else 0.0,
        "max_pitch_jump": int(np.max(jumps)) if jumps else 0,
        "repeated_note_pct": float(rep_rate),
        "avg_duration": float(np.mean(durations)),
        "std_duration": float(np.std(durations)),
        "avg_step": float(np.mean(steps)),
        "std_step": float(np.std(steps)),
        "total_duration_sec": float(notes[-1]["start"] + notes[-1]["duration"]),
    }


def load_model(ckpt_path: Path, cfg: Config, device: torch.device):
    ckpt = torch.load(str(ckpt_path), map_location=device)
    saved_cfg = ckpt.get("config", {})
    if "hidden_dim" in saved_cfg:
        cfg.hidden_dim = saved_cfg["hidden_dim"]
    model = MelodyLSTM(cfg).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    return model, ckpt


def main():
    cfg = Config()
    device = torch.device(cfg.device if torch.cuda.is_available() else "cpu")

    baseline_path = cfg.artifacts_dir / "checkpoints" / "best_model_v1_baseline.pt"
    expanded_path = cfg.artifacts_dir / "checkpoints" / "best_model_expanded.pt"
    if not expanded_path.exists():
        expanded_path = cfg.best_model_path

    out_dir = cfg.generated_dir / "comparisons"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("MelodyLoop: Model Evaluation & Musical Output Comparison")
    print("=" * 70)

    # 1. Ground Truth from Held-out Test Split
    print("\n[1/4] Extracting held-out MAESTRO test piece ground-truth baseline...")
    csv_path = cfg.data_dir / cfg.csv_filename
    test_metrics = None
    prompt_seed_notes = []

    if csv_path.exists():
        df = pd.read_csv(csv_path)
        test_df = df[df["split"] == "test"]
        if not test_df.empty:
            test_row = test_df.iloc[0]
            test_midi_path = cfg.data_dir / test_row["midi_filename"]
            if test_midi_path.exists():
                print(f"Test piece: {test_row.get('canonical_composer')} - {test_row.get('canonical_title')}")
                events = parse_midi_file(test_midi_path, cfg)
                real_notes = []
                curr_t = 0.0
                for p, d, s in events[:80]:
                    dur = dequantize_duration(d, cfg)
                    step = dequantize_step(s, cfg)
                    real_notes.append({"pitch": p, "start": curr_t, "duration": dur, "step": step, "is_seed": True})
                    curr_t += step
                test_metrics = compute_musical_metrics(real_notes)
                prompt_seed_notes = real_notes[:32]

                # Export ground truth sample
                export_notes_to_midi(real_notes, out_dir / "real_maestro_test_clip.mid")
                synthesize_notes_to_wav(real_notes, out_dir / "real_maestro_test_clip.wav")

    # 2. Free Generation Comparison
    results = {}
    if test_metrics:
        results["Real MAESTRO (Held-out Test)"] = test_metrics

    models = {}
    if baseline_path.exists():
        m_base, c_base = load_model(baseline_path, cfg, device)
        models["Baseline (v1: 13 Pieces, 15k Seqs)"] = (m_base, c_base, "baseline")
    if expanded_path.exists():
        m_exp, c_exp = load_model(expanded_path, cfg, device)
        models["Expanded (v2: 962 Pieces, 100k Seqs)"] = (m_exp, c_exp, "expanded")

    print(f"\n[2/4] Generating comparative melodies (Seed=42, Temp=0.6, Length=80)...")
    for name, (model, ckpt, tag) in models.items():
        print(f"Generating with {name} (Val Loss: {ckpt.get('val_loss', 'N/A'):.4f})...")
        notes = generate_melody(
            model=model,
            cfg=cfg,
            num_notes=80,
            temperature=0.6,
            pitch_top_k=5,
            seed=42,
            device=str(device),
        )
        mid_file = out_dir / f"{tag}_free_seed42_temp0.6.mid"
        wav_file = out_dir / f"{tag}_free_seed42_temp0.6.wav"
        export_notes_to_midi(notes, mid_file)
        synthesize_notes_to_wav(notes, wav_file)

        metrics = compute_musical_metrics(notes)
        metrics["epoch"] = ckpt.get("epoch", "N/A")
        metrics["val_loss"] = ckpt.get("val_loss", "N/A")
        results[name] = metrics

    # 3. Seeded Continuation Comparison
    if prompt_seed_notes and len(models) >= 2:
        print(f"\n[3/4] Generating seeded continuations from common 32-note prompt...")
        for name, (model, ckpt, tag) in models.items():
            notes_cont = generate_melody(
                model=model,
                cfg=cfg,
                num_notes=80,
                temperature=0.6,
                pitch_top_k=5,
                seed=42,
                seed_sequence=prompt_seed_notes,
                device=str(device),
            )
            mid_file = out_dir / f"{tag}_seeded_continuation_seed42.mid"
            wav_file = out_dir / f"{tag}_seeded_continuation_seed42.wav"
            export_notes_to_midi(notes_cont, mid_file)
            synthesize_notes_to_wav(notes_cont, wav_file)

    # 4. Print Comparison Table
    print("\n[4/4] Quantitative Musical Comparison Results:")
    print("-" * 95)
    cols = [
        "Model / Source", "Val Loss", "Pitch Range", "Unique Pitches",
        "Repeated %", "Avg Jump", "Avg Dur(s)", "Avg Step(s)"
    ]
    print(f"{cols[0]:<36} | {cols[1]:<8} | {cols[2]:<11} | {cols[3]:<14} | {cols[4]:<10} | {cols[5]:<8} | {cols[6]:<10} | {cols[7]:<10}")
    print("-" * 95)

    for name, m in results.items():
        vloss = f"{m.get('val_loss', 0):.4f}" if isinstance(m.get('val_loss'), (float, int)) else "N/A"
        p_range = f"{m.get('pitch_min', 0)}-{m.get('pitch_max', 0)} ({m.get('pitch_range', 0)})"
        u_pitches = str(m.get("pitch_unique", 0))
        rep_pct = f"{m.get('repeated_note_pct', 0):.1f}%"
        avg_jump = f"{m.get('avg_pitch_jump', 0):.2f}"
        avg_dur = f"{m.get('avg_duration', 0):.2f}s"
        avg_step = f"{m.get('avg_step', 0):.2f}s"
        print(f"{name:<36} | {vloss:<8} | {p_range:<11} | {u_pitches:<14} | {rep_pct:<10} | {avg_jump:<8} | {avg_dur:<10} | {avg_step:<10}")
    print("-" * 95)

    # Save metrics JSON
    metrics_path = out_dir / "evaluation_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed metrics saved to: {metrics_path}")


if __name__ == "__main__":
    main()
