"""
Generate dark-theme, publication-grade diagram assets for MelodyLoop_Presentation_Professional.pptx.
Palette:
- Background: #0B1020 (Deep Navy)
- Card Surface: #151D36 / #1A2342
- Accents: #26D9F1 (Cyan), #2855D9 (Royal Blue), #FFC857 (Gold), #FF6B6B (Coral), #F4F3EB (Ivory), #94A3B8 (Slate)
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

ASSETS_DIR = Path("artifacts/presentation_assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"


def fig_piano_keyboard():
    """Slide 4: Accurate piano keyboard with Middle C (60), A4 (69), and 88-key bounds."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#0B1020")
    ax.set_facecolor("#0B1020")
    ax.set_xlim(-5, 133)
    ax.set_ylim(-0.35, 1.35)
    ax.axis("off")

    # Title & Subtitle
    ax.text(64, 1.25, "Standard 88-Key Acoustic Piano Range vs. 128 MIDI Note Numbers",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#F4F3EB")
    ax.text(64, 1.12, "Physical Acoustic Keys: A0 (MIDI 21) to C8 (MIDI 108) | Pitch Representation: Integer [0, 127]",
            ha="center", va="top", fontsize=8.5, color="#94A3B8")

    # Range Bar (Full MIDI 0-127)
    y_bar = 0.68
    h_bar = 0.16
    ax.add_patch(patches.Rectangle((0, y_bar), 128, h_bar, facecolor="#151D36", edgecolor="#2A3B6A", linewidth=1.5, zorder=2))
    # Playable 88 Keys (21 to 108)
    ax.add_patch(patches.Rectangle((21, y_bar), 88, h_bar, facecolor="#1E3A8A", edgecolor="#26D9F1", linewidth=2.0, zorder=3))

    # Middle C (60) Highlight on bar
    ax.add_patch(patches.Rectangle((59.3, y_bar - 0.03), 2.4, h_bar + 0.06, facecolor="#FF6B6B", edgecolor="#F4F3EB", linewidth=1.8, zorder=4))

    # Range Labels
    ax.text(10, y_bar + h_bar/2, "Sub-Audio\n(0-20)", ha="center", va="center", fontsize=7.5, color="#64748B", zorder=5)
    ax.text(64, y_bar + h_bar/2, "Standard 88 Acoustic Piano Keys (MIDI 21 - 108)", ha="center", va="center", fontsize=9, fontweight="bold", color="#F4F3EB", zorder=5)
    ax.text(118, y_bar + h_bar/2, "Ultra-High\n(109-127)", ha="center", va="center", fontsize=7.5, color="#64748B", zorder=5)

    # Key callout lines
    ax.plot([21, 21], [y_bar - 0.08, y_bar + h_bar + 0.06], color="#26D9F1", linestyle="--", linewidth=1.2)
    ax.text(21, y_bar - 0.10, "A0 (21)\n27.5 Hz", ha="center", va="top", fontsize=7.5, color="#26D9F1", fontweight="bold")

    ax.plot([60, 60], [y_bar - 0.08, y_bar + h_bar + 0.05], color="#FF6B6B", linestyle="-", linewidth=1.5)
    ax.text(60, y_bar + h_bar + 0.07, "Middle C (C4, 60)\n261.63 Hz", ha="center", va="bottom", fontsize=8.5, color="#FF6B6B", fontweight="bold")

    ax.plot([69, 69], [y_bar - 0.08, y_bar + h_bar + 0.06], color="#FFC857", linestyle=":", linewidth=1.5)
    ax.text(69, y_bar - 0.10, "Concert A (A4, 69)\n440.0 Hz", ha="center", va="top", fontsize=7.5, color="#FFC857", fontweight="bold")

    ax.plot([108, 108], [y_bar - 0.08, y_bar + h_bar + 0.06], color="#26D9F1", linestyle="--", linewidth=1.2)
    ax.text(108, y_bar - 0.10, "C8 (108)\n4186 Hz", ha="center", va="top", fontsize=7.5, color="#26D9F1", fontweight="bold")

    # Detailed keyboard illustration (C3 to C5: 2 octaves, 48 to 72)
    key_y = 0.08
    key_w = 4.2
    key_h = 0.32
    white_notes = [0, 2, 4, 5, 7, 9, 11]
    black_notes = [1, 3, 6, 8, 10]

    # White keys
    w_count = 0
    white_key_x = {}
    start_x = 22.0
    for p in range(48, 73):
        semitone = (p - 48) % 12
        if semitone in white_notes:
            kx = start_x + w_count * key_w
            white_key_x[p] = kx
            is_c4 = (p == 60)
            fc = "#381822" if is_c4 else "#F4F3EB"
            ec = "#FF6B6B" if is_c4 else "#475569"
            ax.add_patch(patches.Rectangle((kx, key_y), key_w, key_h, facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=6))
            if is_c4:
                ax.text(kx + key_w/2, key_y + 0.04, "C4 (60)\nMiddle C", ha="center", va="bottom", fontsize=7.5, color="#FF6B6B", fontweight="bold", zorder=8)
            elif p in (48, 72):
                lbl = "C3 (48)" if p == 48 else "C5 (72)"
                ax.text(kx + key_w/2, key_y + 0.04, lbl, ha="center", va="bottom", fontsize=7, color="#64748B", zorder=8)
            w_count += 1

    # Black keys
    b_key_w = key_w * 0.62
    b_key_h = key_h * 0.60
    b_key_y = key_y + (key_h - b_key_h)
    for p in range(48, 72):
        semitone = (p - 48) % 12
        if semitone in black_notes:
            # Position between white key p-1 and white key p+1
            left_p = p - 1
            kx = white_key_x[left_p] + key_w - (b_key_w / 2.0)
            ax.add_patch(patches.Rectangle((kx, b_key_y), b_key_w, b_key_h, facecolor="#151D36", edgecolor="#26D9F1", linewidth=1.0, zorder=7))

    out_path = ASSETS_DIR / "fig_piano_keyboard.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_midi_vs_audio():
    """Slide 5: Symbolic MIDI instructions vs. Synthesized Audio Waveform."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#0B1020")

    # Panel 1: MIDI Symbolic Data
    ax1.set_facecolor("#151D36")
    ax1.set_title("Symbolic MIDI Event Matrix (Discrete Tokens)", color="#26D9F1", fontsize=10, fontweight="bold", pad=8)
    ax1.set_xlabel("Time (Seconds)", color="#94A3B8", fontsize=8.5)
    ax1.set_ylabel("MIDI Pitch (0-127)", color="#94A3B8", fontsize=8.5)
    ax1.tick_params(colors="#64748B", labelsize=8)
    for spine in ax1.spines.values():
        spine.set_color("#2A3B6A")

    # Draw symbolic note bars
    sample_notes = [
        (0.0, 0.45, 60, "C4"),
        (0.40, 0.40, 64, "E4"),
        (0.80, 0.60, 67, "G4"),
        (1.30, 0.35, 72, "C5"),
        (1.60, 0.50, 71, "B4"),
        (2.05, 0.40, 67, "G4"),
        (2.40, 0.60, 64, "E4"),
        (2.95, 0.80, 60, "C4"),
    ]
    for start, dur, pitch, name in sample_notes:
        ax1.add_patch(patches.Rectangle((start, pitch - 0.4), dur, 0.8, facecolor="#26D9F1", edgecolor="#F4F3EB", linewidth=1.2, alpha=0.9))
        ax1.text(start + dur/2, pitch, name, ha="center", va="center", fontsize=7.5, color="#0B1020", fontweight="bold")

    ax1.set_xlim(-0.1, 4.0)
    ax1.set_ylim(55, 76)
    ax1.axhline(60, color="#FF6B6B", linestyle=":", alpha=0.6, label="Middle C (60)")
    ax1.legend(facecolor="#0B1020", edgecolor="#2A3B6A", labelcolor="#F4F3EB", fontsize=7.5, loc="upper right")

    # Panel 2: Synthesized Audio Waveform
    ax2.set_facecolor("#151D36")
    ax2.set_title("Synthesized Waveform: s(t) = A(t) Σ a_k sin(2π k f_0 t)", color="#FFC857", fontsize=10, fontweight="bold", pad=8)
    ax2.set_xlabel("Time (Seconds)", color="#94A3B8", fontsize=8.5)
    ax2.set_ylabel("Amplitude [-1.0, 1.0]", color="#94A3B8", fontsize=8.5)
    ax2.tick_params(colors="#64748B", labelsize=8)
    for spine in ax2.spines.values():
        spine.set_color("#2A3B6A")

    t = np.linspace(0, 3.8, 1500)
    # Simulate fundamental + decay waveform
    wave = np.zeros_like(t)
    for start, dur, pitch, _ in sample_notes:
        f0 = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))
        mask = (t >= start) & (t < start + dur)
        t_note = t[mask] - start
        env = np.exp(-3.5 * t_note / dur)
        sig = 0.6 * np.sin(2 * np.pi * f0 * t_note) + 0.3 * np.sin(4 * np.pi * f0 * t_note) + 0.1 * np.sin(6 * np.pi * f0 * t_note)
        wave[mask] += sig * env

    wave = np.clip(wave, -1.0, 1.0)
    ax2.plot(t, wave, color="#FFC857", linewidth=0.9, alpha=0.9)
    ax2.set_xlim(-0.1, 4.0)
    ax2.set_ylim(-1.15, 1.15)
    ax2.axhline(0, color="#64748B", linestyle="--", linewidth=0.7, alpha=0.5)

    out_path = ASSETS_DIR / "fig_midi_vs_audio.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_maestro_splits():
    """Slide 6: MAESTRO v3.0.0 official split breakdown."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6), dpi=250, gridspec_kw={'width_ratios': [1.3, 1.0]})
    fig.patch.set_facecolor("#0B1020")

    # Segmented horizontal split bar
    ax1.set_facecolor("#0B1020")
    ax1.set_xlim(0, 1276)
    ax1.set_ylim(0, 1.5)
    ax1.axis("off")

    ax1.text(0, 1.35, "Official MAESTRO v3.0.0 Dataset Split Distribution", fontsize=11, fontweight="bold", color="#F4F3EB")
    ax1.text(0, 1.18, "1,276 Virtuosic Piano Performances | International Piano-e-Competition Data", fontsize=8.5, color="#94A3B8")

    # Bars: Train (962), Val (137), Test (177)
    y_b = 0.55
    h_b = 0.40
    ax1.add_patch(patches.Rectangle((0, y_b), 962, h_b, facecolor="#2855D9", edgecolor="#F4F3EB", linewidth=1.5))
    ax1.add_patch(patches.Rectangle((962, y_b), 137, h_b, facecolor="#FFC857", edgecolor="#F4F3EB", linewidth=1.5))
    ax1.add_patch(patches.Rectangle((962 + 137, y_b), 177, h_b, facecolor="#FF6B6B", edgecolor="#F4F3EB", linewidth=1.5))

    ax1.text(481, y_b + h_b/2, "TRAINING SET\n962 Files (75.4%)\n5.66M Note Events", ha="center", va="center", color="#F4F3EB", fontsize=8.5, fontweight="bold")
    ax1.text(962 + 68, y_b + h_b/2, "VAL\n137 Files\n(10.7%)", ha="center", va="center", color="#0B1020", fontsize=7.5, fontweight="bold")
    ax1.text(962 + 137 + 88, y_b + h_b/2, "TEST\n177 Files\n(13.9%)", ha="center", va="center", color="#F4F3EB", fontsize=7.5, fontweight="bold")

    # Explanatory annotations
    ax1.text(0, 0.25, "• Training Split (962 files): Parameter optimization via gradient backpropagation.\n• Validation Split (137 files): Epoch monitoring & best checkpoint selection (no gradients).\n• Test Split (177 files): Held-out evaluation (e.g. Scriabin Op. 63) - Zero data leakage.", fontsize=8, color="#F4F3EB")

    # Pie/Donut Chart on right
    ax2.set_facecolor("#0B1020")
    splits = [962, 137, 177]
    colors = ["#2855D9", "#FFC857", "#FF6B6B"]
    explode = (0.02, 0.05, 0.05)
    wedges, texts, autotexts = ax2.pie(
        splits,
        labels=["Train (962)", "Val (137)", "Test (177)"],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        explode=explode,
        textprops=dict(color="#F4F3EB", fontsize=8),
        wedgeprops=dict(width=0.45, edgecolor="#0B1020", linewidth=2)
    )
    for at in autotexts:
        at.set_color("#F4F3EB")
        at.set_fontweight("bold")
        at.set_fontsize(7.5)

    out_path = ASSETS_DIR / "fig_maestro_splits.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_dataset_scaling():
    """Slide 7: Visual comparison of Baseline (13 files) vs Expanded (962 files)."""
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=250)
    fig.patch.set_facecolor("#0B1020")
    ax.set_facecolor("#151D36")

    metrics = ["Train Files", "Notes Extracted (k)", "Sequences (k)", "Val Files", "Val Seqs (k)"]
    baseline = [13, 64.26, 15.0, 1, 3.92]
    expanded = [962, 5659.3, 100.0, 137, 10.0]

    x = np.arange(len(metrics))
    width = 0.35

    ax.set_yscale('log')
    rects1 = ax.bar(x - width/2, baseline, width, label="Baseline Experiment (v1)", color="#64748B", edgecolor="#94A3B8")
    rects2 = ax.bar(x + width/2, expanded, width, label="Expanded Experiment (v2)", color="#26D9F1", edgecolor="#F4F3EB")

    ax.set_title("Dataset Expansion Metrics: Baseline vs. Expanded Corpus (Log Scale)", color="#F4F3EB", fontsize=10.5, fontweight="bold", pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, color="#F4F3EB", fontsize=8.5, fontweight="bold")
    ax.tick_params(colors="#64748B", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#2A3B6A")

    # Multiplier callouts
    multipliers = ["74x", "88x", "6.7x", "137x", "2.5x"]
    for i, mult in enumerate(multipliers):
        ax.text(x[i] + width/2, expanded[i] * 1.35, mult, ha="center", va="bottom", color="#FFC857", fontsize=8.5, fontweight="bold")

    ax.legend(facecolor="#0B1020", edgecolor="#2A3B6A", labelcolor="#F4F3EB", fontsize=8, loc="upper left")
    out_path = ASSETS_DIR / "fig_dataset_scaling.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_training_loss():
    """Slide 14: Actual training dynamics from expanded training run (training_expanded.log)."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#0B1020")
    ax.set_facecolor("#151D36")

    epochs = np.arange(1, 16)
    # Actual values from artifacts/logs/training_expanded.log
    train_loss = [6.3280, 5.8187, 5.6420, 5.5198, 5.4207, 5.3436, 5.2762, 5.2152, 5.1601, 5.1093, 5.0650, 5.0210, 4.9832, 4.9447, 4.9121]
    val_loss =   [6.2395, 6.0683, 6.0120, 5.9745, 5.9519, 5.9274, 5.9151, 5.9181, 5.9320, 5.9462, 5.9571, 5.9780, 5.9936, 6.0153, 6.0386]

    ax.plot(epochs, train_loss, 'o-', color="#26D9F1", linewidth=2.4, markersize=5.5, label="Train Loss (Multi-Task Cross-Entropy)")
    ax.plot(epochs, val_loss, 's-', color="#FFC857", linewidth=2.4, markersize=5.5, label="Val Loss (Held-out 10k Sequences)")

    # Highlight best epoch 7
    ax.scatter([7], [5.9151], color="#22C55E", s=140, zorder=6, edgecolors="#F4F3EB", linewidths=1.5, label="Best Checkpoint (Epoch 7, Loss 5.9151)")
    ax.annotate("BEST CHECKPOINT\nEpoch 7 (Val Loss: 5.9151)", xy=(7, 5.9151), xytext=(7.4, 5.65),
                arrowprops=dict(facecolor="#22C55E", edgecolor="#F4F3EB", shrink=0.08, width=1.5, headwidth=6),
                fontsize=8, fontweight="bold", color="#22C55E")

    # Early stopping at epoch 15
    ax.axvline(x=15, color="#FF6B6B", linestyle="--", linewidth=1.5, alpha=0.8)
    ax.text(14.6, 5.40, "Early Stopping (Patience 8)", rotation=90, color="#FF6B6B", fontsize=7.5, va="bottom", fontweight="bold")

    # Old baseline reference line
    ax.axhline(6.1791, color="#94A3B8", linestyle=":", linewidth=1.2, alpha=0.7)
    ax.text(1.2, 6.195, "Baseline Model Best Val Loss (6.1791)", color="#94A3B8", fontsize=7.5)

    ax.set_title("MelodyLoop Expanded Training Dynamics (NVIDIA RTX 3050 Laptop GPU, 17.2s / Epoch)", color="#F4F3EB", fontsize=10.5, fontweight="bold", pad=8)
    ax.set_xlabel("Epoch", color="#94A3B8", fontsize=8.5)
    ax.set_ylabel("Total Cross-Entropy Loss", color="#94A3B8", fontsize=8.5)
    ax.tick_params(colors="#64748B", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#2A3B6A")

    ax.set_xlim(0.5, 16.5)
    ax.set_ylim(4.7, 6.5)
    ax.legend(facecolor="#0B1020", edgecolor="#2A3B6A", labelcolor="#F4F3EB", fontsize=7.5, loc=(0.56, 0.72))

    out_path = ASSETS_DIR / "fig_training_loss.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_evaluation_comparison():
    """Slide 19: Musical evaluation chart comparing Baseline vs Expanded vs Real MAESTRO."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6), dpi=250)
    fig.patch.set_facecolor("#0B1020")

    # Subplot 1: Repetition rate & Avg Pitch Jump
    ax1.set_facecolor("#151D36")
    categories = ["Real MAESTRO\n(Scriabin Op.63)", "Baseline Model\n(13 Pieces)", "Expanded Model\n(962 Pieces)"]
    rep_rates = [0.0, 17.7, 10.1]
    colors1 = ["#2855D9", "#FF6B6B", "#22C55E"]

    bars1 = ax1.bar(categories, rep_rates, color=colors1, width=0.55, edgecolor="#F4F3EB", linewidth=1.0)
    ax1.set_title("Repeated-Note Monotony Rate (%)", color="#F4F3EB", fontsize=9.5, fontweight="bold", pad=8)
    ax1.set_ylabel("Repetition Percentage (%)", color="#94A3B8", fontsize=8)
    ax1.tick_params(colors="#94A3B8", labelsize=7.5)
    for spine in ax1.spines.values():
        spine.set_color("#2A3B6A")

    for b, val in zip(bars1, rep_rates):
        ax1.text(b.get_x() + b.get_width()/2, val + 0.6, f"{val:.1f}%", ha="center", va="bottom", color="#F4F3EB", fontsize=8, fontweight="bold")
    ax1.set_ylim(0, 22)

    # Subplot 2: Duration & Step comparison
    ax2.set_facecolor("#151D36")
    x = np.arange(len(categories))
    w = 0.35
    durs = [0.48, 0.06, 0.34]
    steps = [0.21, 0.05, 0.25]

    ax2.bar(x - w/2, durs, w, label="Avg Note Duration (s)", color="#26D9F1", edgecolor="#F4F3EB")
    ax2.bar(x + w/2, steps, w, label="Avg Step Interval (s)", color="#FFC857", edgecolor="#F4F3EB")

    ax2.set_title("Temporal Pacing & Rhythmic Dynamics", color="#F4F3EB", fontsize=9.5, fontweight="bold", pad=8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, color="#94A3B8", fontsize=7.5)
    ax2.set_ylabel("Seconds", color="#94A3B8", fontsize=8)
    ax2.tick_params(colors="#94A3B8", labelsize=7.5)
    for spine in ax2.spines.values():
        spine.set_color("#2A3B6A")
    ax2.legend(facecolor="#0B1020", edgecolor="#2A3B6A", labelcolor="#F4F3EB", fontsize=7.5, loc="upper right")
    ax2.set_ylim(0, 0.65)

    out_path = ASSETS_DIR / "fig_evaluation_comparison.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_piano_roll():
    """Slide 18: Piano roll comparing Prompt phrase vs LSTM continuation."""
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=250)
    fig.patch.set_facecolor("#0B1020")
    ax.set_facecolor("#151D36")

    # Real human prompt (Franz Schubert Sonata in A minor) - 16 notes
    seed_notes = [
        (0.0, 0.4, 69), (0.4, 0.2, 72), (0.6, 0.2, 76), (0.8, 0.6, 81),
        (1.4, 0.3, 76), (1.7, 0.3, 72), (2.0, 0.5, 69), (2.5, 0.3, 67),
        (2.8, 0.4, 65), (3.2, 0.3, 69), (3.5, 0.3, 72), (3.8, 0.6, 74),
        (4.4, 0.3, 72), (4.7, 0.3, 69), (5.0, 0.5, 67), (5.5, 0.5, 69)
    ]
    # LSTM continuation - 24 notes with coherent intervals
    lstm_notes = [
        (6.0, 0.3, 72), (6.3, 0.3, 74), (6.6, 0.4, 76), (7.0, 0.3, 72),
        (7.3, 0.2, 69), (7.5, 0.4, 67), (7.9, 0.3, 69), (8.2, 0.5, 72),
        (8.7, 0.4, 76), (9.1, 0.3, 79), (9.4, 0.6, 81), (10.0, 0.3, 76),
        (10.3, 0.3, 74), (10.6, 0.4, 72), (11.0, 0.3, 69), (11.3, 0.5, 67),
        (11.8, 0.3, 65), (12.1, 0.4, 69), (12.5, 0.3, 72), (12.8, 0.6, 76),
        (13.4, 0.4, 74), (13.8, 0.3, 72), (14.1, 0.4, 69), (14.5, 0.8, 69)
    ]

    for s, d, p in seed_notes:
        ax.barh(y=p, width=d, left=s, height=0.75, color="#FFC857", edgecolor="#F4F3EB", linewidth=0.8, alpha=0.9,
                label="Prompt Phrase (MAESTRO)" if s == 0.0 else "")

    for s, d, p in lstm_notes:
        ax.barh(y=p, width=d, left=s, height=0.75, color="#26D9F1", edgecolor="#F4F3EB", linewidth=0.8, alpha=0.9,
                label="LSTM Autoregressive Continuation" if s == 6.0 else "")

    ax.axvline(x=6.0, color="#FF6B6B", linestyle="--", linewidth=1.5, label="Inference Transition Boundary (t = 6.0s)")
    ax.axhline(60, color="#64748B", linestyle=":", alpha=0.5, label="Middle C (60)")

    ax.set_title("MelodyLoop Interactive Piano-Roll: Seed Continuation (Temp=0.6, Top-K=5)", color="#F4F3EB", fontsize=10, fontweight="bold", pad=8)
    ax.set_xlabel("Time (Seconds)", color="#94A3B8", fontsize=8.5)
    ax.set_ylabel("MIDI Pitch (0-127)", color="#94A3B8", fontsize=8.5)
    ax.tick_params(colors="#64748B", labelsize=8)
    ax.set_ylim(60, 85)
    ax.set_xlim(-0.5, 16.0)
    for spine in ax.spines.values():
        spine.set_color("#2A3B6A")

    ax.legend(facecolor="#0B1020", edgecolor="#2A3B6A", labelcolor="#F4F3EB", fontsize=7.5, loc="upper right")

    out_path = ASSETS_DIR / "fig_piano_roll.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_lstm_cell_dark():
    """Slide 11: Dark-themed LSTM Cell Gates and Equations."""
    fig, ax = plt.subplots(figsize=(10, 4.0), dpi=250)
    fig.patch.set_facecolor("#0B1020")
    ax.set_facecolor("#0B1020")

    ax.text(0.5, 0.96, "LSTM Internal Cell Architecture & Mathematical Gate Formulations",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#F4F3EB", transform=ax.transAxes)

    # Main cell body
    ax.add_patch(patches.FancyBboxPatch(
        (0.18, 0.12), 0.64, 0.72, boxstyle="round,pad=0.03,rounding_size=0.04",
        facecolor="#151D36", edgecolor="#26D9F1", linewidth=2.0, zorder=2
    ))
    ax.text(0.5, 0.81, "LSTM Cell Recurrent Core (Hidden Dim = 128)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#26D9F1", zorder=3)

    # Inputs and Outputs lines
    # C_{t-1} in
    ax.annotate("", xy=(0.18, 0.68), xytext=(0.04, 0.68), arrowprops=dict(arrowstyle="->", color="#FFC857", lw=2.2))
    ax.text(0.09, 0.72, "Cell State\n$C_{t-1}$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#FFC857")

    # h_{t-1} and x_t in
    ax.annotate("", xy=(0.18, 0.28), xytext=(0.04, 0.28), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=2.2))
    ax.text(0.09, 0.32, "Hidden\n$h_{t-1}$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#26D9F1")

    ax.annotate("", xy=(0.32, 0.12), xytext=(0.32, 0.02), arrowprops=dict(arrowstyle="->", color="#22C55E", lw=2.2))
    ax.text(0.32, 0.00, "Input Vector $x_t$\n(Dim=128)", ha="center", va="top", fontsize=8.5, fontweight="bold", color="#22C55E")

    # Gate Boxes inside Cell
    # Forget Gate
    ax.add_patch(patches.Rectangle((0.24, 0.40), 0.10, 0.16, facecolor="#3B1824", edgecolor="#FF6B6B", lw=1.5, zorder=3))
    ax.text(0.29, 0.48, "Forget\nGate $\\sigma$\n$f_t$", ha="center", va="center", fontsize=8, fontweight="bold", color="#FF6B6B", zorder=4)

    # Input Gate
    ax.add_patch(patches.Rectangle((0.38, 0.40), 0.10, 0.16, facecolor="#1E2958", edgecolor="#2855D9", lw=1.5, zorder=3))
    ax.text(0.43, 0.48, "Input\nGate $\\sigma$\n$i_t$", ha="center", va="center", fontsize=8, fontweight="bold", color="#26D9F1", zorder=4)

    # Candidate Cell State
    ax.add_patch(patches.Rectangle((0.52, 0.40), 0.10, 0.16, facecolor="#143828", edgecolor="#22C55E", lw=1.5, zorder=3))
    ax.text(0.57, 0.48, "Candidate\n$\\tanh$\n$\\tilde{C}_t$", ha="center", va="center", fontsize=8, fontweight="bold", color="#22C55E", zorder=4)

    # Output Gate
    ax.add_patch(patches.Rectangle((0.66, 0.40), 0.10, 0.16, facecolor="#3D3212", edgecolor="#FFC857", lw=1.5, zorder=3))
    ax.text(0.71, 0.48, "Output\nGate $\\sigma$\n$o_t$", ha="center", va="center", fontsize=8, fontweight="bold", color="#FFC857", zorder=4)

    # Operation Circles
    ax.add_patch(patches.Circle((0.29, 0.68), 0.024, facecolor="#3B1824", edgecolor="#FF6B6B", lw=1.5, zorder=4))
    ax.text(0.29, 0.68, "$\\times$", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#FF6B6B", zorder=5)

    ax.add_patch(patches.Circle((0.50, 0.58), 0.024, facecolor="#143828", edgecolor="#22C55E", lw=1.5, zorder=4))
    ax.text(0.50, 0.58, "$\\times$", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#22C55E", zorder=5)

    ax.add_patch(patches.Circle((0.50, 0.68), 0.024, facecolor="#3D3212", edgecolor="#FFC857", lw=1.5, zorder=4))
    ax.text(0.50, 0.68, "$+$", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#FFC857", zorder=5)

    # Outputs
    ax.annotate("", xy=(0.96, 0.68), xytext=(0.82, 0.68), arrowprops=dict(arrowstyle="->", color="#FFC857", lw=2.2))
    ax.text(0.91, 0.72, "Cell State\n$C_t$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#FFC857")

    ax.annotate("", xy=(0.96, 0.28), xytext=(0.82, 0.28), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=2.2))
    ax.text(0.91, 0.32, "Hidden\n$h_t$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#26D9F1")

    # Math equations panel at bottom
    ax.text(0.5, 0.17, "Governing Equations: $f_t = \\sigma(W_f [h_{t-1}, x_t] + b_f)$ | $i_t = \\sigma(W_i [h_{t-1}, x_t] + b_i)$ | $\\tilde{C}_t = \\tanh(W_c [h_{t-1}, x_t] + b_c)$\n$C_t = f_t \\odot C_{t-1} + i_t \\odot \\tilde{C}_t$ | $o_t = \\sigma(W_o [h_{t-1}, x_t] + b_o)$ | $h_t = o_t \\odot \\tanh(C_t)$",
            ha="center", va="center", fontsize=8, color="#F4F3EB", bbox=dict(facecolor="#151D36", edgecolor="#2A3B6A", boxstyle="round,pad=0.4"))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    out_path = ASSETS_DIR / "fig_lstm_cell.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_model_architecture_dark():
    """Slide 12: Dark-themed MelodyLSTM PyTorch Architecture & Multi-Task Heads."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#0B1020")
    ax.set_facecolor("#0B1020")

    ax.text(0.5, 0.96, "MelodyLSTM Multi-Task Neural Network Architecture (167,104 Parameters)",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#F4F3EB", transform=ax.transAxes)

    # 1. Inputs
    ax.add_patch(patches.Rectangle((0.02, 0.40), 0.13, 0.35, facecolor="#151D36", edgecolor="#64748B", lw=1.5))
    ax.text(0.085, 0.57, "Input Indices\n[B, 32, 3]\nPitch (0-127)\nDur (0-31)\nStep (0-31)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#F4F3EB")

    # 2. Embedding Layers
    ax.add_patch(patches.Rectangle((0.19, 0.66), 0.15, 0.18, facecolor="#1E3A8A", edgecolor="#26D9F1", lw=1.5))
    ax.text(0.265, 0.75, "Pitch Embed\n128 -> 64\n(8,192 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#26D9F1")

    ax.add_patch(patches.Rectangle((0.19, 0.44), 0.15, 0.18, facecolor="#1E3A8A", edgecolor="#26D9F1", lw=1.5))
    ax.text(0.265, 0.53, "Duration Embed\n32 -> 32\n(1,024 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#26D9F1")

    ax.add_patch(patches.Rectangle((0.19, 0.22), 0.15, 0.18, facecolor="#1E3A8A", edgecolor="#26D9F1", lw=1.5))
    ax.text(0.265, 0.31, "Step Embed\n32 -> 32\n(1,024 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#26D9F1")

    # 3. Concatenate
    ax.add_patch(patches.Rectangle((0.38, 0.35), 0.12, 0.42, facecolor="#151D36", edgecolor="#FFC857", lw=1.5))
    ax.text(0.44, 0.56, "Concatenate\n64 + 32 + 32\n= 128 Dim\nDropout(0.1)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#FFC857")

    # 4. LSTM Core
    ax.add_patch(patches.Rectangle((0.54, 0.33), 0.16, 0.46, facecolor="#2855D9", edgecolor="#F4F3EB", lw=2.0))
    ax.text(0.62, 0.56, "LSTM Layer\nInput: 128\nHidden: 128\n1 Layer\n(132,096 params)", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#F4F3EB")

    # 5. Output Heads
    ax.add_patch(patches.Rectangle((0.74, 0.66), 0.15, 0.18, facecolor="#1E3A8A", edgecolor="#26D9F1", lw=1.5))
    ax.text(0.815, 0.75, "Pitch Head\nLinear(128 -> 128)\n(16,512 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#26D9F1")

    ax.add_patch(patches.Rectangle((0.74, 0.44), 0.15, 0.18, facecolor="#1E3A8A", edgecolor="#26D9F1", lw=1.5))
    ax.text(0.815, 0.53, "Duration Head\nLinear(128 -> 32)\n(4,128 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#26D9F1")

    ax.add_patch(patches.Rectangle((0.74, 0.22), 0.15, 0.18, facecolor="#1E3A8A", edgecolor="#26D9F1", lw=1.5))
    ax.text(0.815, 0.31, "Step Head\nLinear(128 -> 32)\n(4,128 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#26D9F1")

    # Connectors
    ax.annotate("", xy=(0.19, 0.75), xytext=(0.15, 0.65), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=1.5))
    ax.annotate("", xy=(0.19, 0.53), xytext=(0.15, 0.57), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=1.5))
    ax.annotate("", xy=(0.19, 0.31), xytext=(0.15, 0.49), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=1.5))

    ax.annotate("", xy=(0.38, 0.56), xytext=(0.34, 0.56), arrowprops=dict(arrowstyle="->", color="#FFC857", lw=1.8))
    ax.annotate("", xy=(0.54, 0.56), xytext=(0.50, 0.56), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=1.8))

    ax.annotate("", xy=(0.74, 0.75), xytext=(0.70, 0.62), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=1.5))
    ax.annotate("", xy=(0.74, 0.53), xytext=(0.70, 0.56), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=1.5))
    ax.annotate("", xy=(0.74, 0.31), xytext=(0.70, 0.50), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=1.5))

    # Loss callout at bottom
    ax.text(0.5, 0.09, "Multi-Task Loss Objective: $\\mathcal{L}_{total} = \\text{CrossEntropy}(\\hat{y}_p, y_p) + \\text{CrossEntropy}(\\hat{y}_d, y_d) + \\text{CrossEntropy}(\\hat{y}_s, y_s)$",
            ha="center", va="center", fontsize=8, color="#F4F3EB", bbox=dict(facecolor="#151D36", edgecolor="#2A3B6A", boxstyle="round,pad=0.3"))

    ax.set_xlim(0, 0.95)
    ax.set_ylim(0, 1)
    ax.axis("off")
    out_path = ASSETS_DIR / "fig_model_architecture.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_autoregressive_dark():
    """Slide 16: Dark-themed Autoregressive Sampling Loop & Top-K Filtering."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6), dpi=250)
    fig.patch.set_facecolor("#0B1020")

    # Left: Autoregressive Loop
    ax1.set_facecolor("#151D36")
    ax1.set_title("1. Autoregressive Rolling Context Loop", fontsize=9.5, fontweight="bold", color="#26D9F1", pad=8)

    steps = [
        "Initial Seed Buffer (32 notes)",
        "MelodyLSTM Forward Pass",
        "Sample Next Event (p, d, s)",
        "Slide Window: Pop oldest, push new",
        "Repeat N times -> Export MIDI & WAV"
    ]
    for i, s in enumerate(steps):
        y = 0.82 - i * 0.17
        fc = "#1E2958" if i in (0, 3) else "#143828" if i == 2 else "#2855D9" if i == 1 else "#3D3212"
        ec = "#26D9F1" if i in (0, 3) else "#22C55E" if i == 2 else "#F4F3EB" if i == 1 else "#FFC857"
        ax1.add_patch(patches.FancyBboxPatch((0.08, y), 0.84, 0.12, boxstyle="round,pad=0.02", facecolor=fc, edgecolor=ec, lw=1.2))
        ax1.text(0.5, y + 0.06, s, ha="center", va="center", fontsize=8.0, fontweight="bold", color="#F4F3EB")
        if i < len(steps) - 1:
            ax1.annotate("", xy=(0.5, y - 0.01), xytext=(0.5, y + 0.01), arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=1.5))

    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis("off")

    # Right: Temperature & Top-K Effect
    ax2.set_facecolor("#151D36")
    ax2.set_title("2. Temperature Scaling & Top-K=5 Filtering", fontsize=9.5, fontweight="bold", color="#FFC857", pad=8)

    candidates = ["C4 (60)", "E4 (64)", "G4 (67)", "D4 (62)", "A4 (69)", "F4 (65)", "B4 (71)", "C#4 (61)"]
    raw_probs = [0.40, 0.25, 0.18, 0.08, 0.04, 0.03, 0.015, 0.005]
    colors = ["#26D9F1", "#26D9F1", "#26D9F1", "#26D9F1", "#26D9F1", "#475569", "#475569", "#475569"]

    bars = ax2.bar(candidates, raw_probs, color=colors, edgecolor="#F4F3EB", width=0.6, zorder=3)
    ax2.axvline(4.5, color="#FF6B6B", linestyle="--", linewidth=1.8, zorder=4)
    ax2.text(2.2, 0.35, "Top-K = 5 Candidates\n(Kept & Renormalized)", ha="center", va="center", fontsize=7.5, color="#26D9F1", fontweight="bold",
             bbox=dict(facecolor="#0B1020", edgecolor="#26D9F1", boxstyle="round,pad=0.2"))
    ax2.text(6.0, 0.28, "Tail Pruned\n(-inf logits)", ha="center", va="center", fontsize=7.5, color="#FF6B6B", fontweight="bold",
             bbox=dict(facecolor="#0B1020", edgecolor="#FF6B6B", boxstyle="round,pad=0.2"))

    ax2.set_ylabel("Probability $P(y_i)$", fontsize=8, color="#94A3B8")
    ax2.tick_params(axis="x", rotation=35, labelsize=7.5, colors="#F4F3EB")
    ax2.tick_params(axis="y", labelsize=7.5, colors="#94A3B8")
    for spine in ax2.spines.values():
        spine.set_color("#2A3B6A")
    ax2.set_ylim(0, 0.46)

    out_path = ASSETS_DIR / "fig_autoregressive_loop.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_audio_synthesis_dark():
    """Slide 17: Dark-themed Additive Synthesis & ADSR Decay Mechanics."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6), dpi=250)
    fig.patch.set_facecolor("#0B1020")

    sr = 44100
    dur = 0.5
    t = np.linspace(0, dur, int(sr * dur))
    freq = 261.63  # Middle C (C4)

    # Harmonics
    f1 = 0.60 * np.sin(2 * np.pi * freq * t)
    f2 = 0.25 * np.sin(2 * np.pi * (2 * freq) * t)
    f3 = 0.15 * np.sin(2 * np.pi * (3 * freq) * t)
    combined = f1 + f2 + f3

    # Left: Harmonics breakdown
    ax1.set_facecolor("#151D36")
    ax1.set_title("1. Additive Harmonics ($f_0 = 261.63$ Hz)", fontsize=9.5, fontweight="bold", color="#26D9F1", pad=8)
    ax1.plot(t[:200]*1000, f1[:200], label="Fundamental f0 (60%)", color="#26D9F1", lw=1.2)
    ax1.plot(t[:200]*1000, f2[:200], label="2nd Harmonic 2f0 (25%)", color="#22C55E", lw=1.0, linestyle="--")
    ax1.plot(t[:200]*1000, f3[:200], label="3rd Harmonic 3f0 (15%)", color="#FFC857", lw=1.0, linestyle=":")
    ax1.plot(t[:200]*1000, combined[:200], label="Composite Wave", color="#F4F3EB", lw=1.6)
    ax1.set_xlabel("Time (milliseconds)", fontsize=8, color="#94A3B8")
    ax1.set_ylabel("Amplitude", fontsize=8, color="#94A3B8")
    ax1.tick_params(colors="#94A3B8", labelsize=7.5)
    for spine in ax1.spines.values():
        spine.set_color("#2A3B6A")
    ax1.legend(loc="upper right", fontsize=6.5, facecolor="#0B1020", edgecolor="#2A3B6A", labelcolor="#F4F3EB")

    # Right: ADSR Envelope
    ax2.set_facecolor("#151D36")
    ax2.set_title("2. ADSR Decay Envelope & Resulting Audio", fontsize=9.5, fontweight="bold", color="#FFC857", pad=8)

    envelope = np.exp(-3.0 * t / dur)
    attack_len = int(0.005 * sr)
    envelope[:attack_len] *= np.linspace(0.0, 1.0, attack_len)
    release_len = int(0.01 * sr)
    envelope[-release_len:] *= np.linspace(1.0, 0.0, release_len)

    audio = combined * envelope
    ax2.plot(t, envelope, color="#FF6B6B", linewidth=1.5, linestyle="--", label="Decay Envelope", zorder=4)
    ax2.plot(t, audio, color="#26D9F1", linewidth=0.6, alpha=0.85, label="Synthesized Waveform", zorder=3)
    ax2.set_xlabel("Time (seconds)", fontsize=8, color="#94A3B8")
    ax2.set_ylabel("Normalized Amplitude", fontsize=8, color="#94A3B8")
    ax2.tick_params(colors="#94A3B8", labelsize=7.5)
    for spine in ax2.spines.values():
        spine.set_color("#2A3B6A")
    ax2.legend(loc="upper right", fontsize=6.5, facecolor="#0B1020", edgecolor="#2A3B6A", labelcolor="#F4F3EB")

    out_path = ASSETS_DIR / "fig_audio_synthesis.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_end_to_end_dark():
    """Slide 3: Dark-themed complete end-to-end system workflow."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#0B1020")
    ax.set_facecolor("#0B1020")

    ax.text(0.5, 0.96, "MelodyLoop Complete End-to-End Deep Learning Architecture Pipeline",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#F4F3EB", transform=ax.transAxes)

    # 3 Phase containers
    # 1. Ingestion & Preprocessing
    ax.add_patch(patches.FancyBboxPatch((0.02, 0.10), 0.28, 0.74, boxstyle="round,pad=0.02", facecolor="#151D36", edgecolor="#26D9F1", lw=1.5))
    ax.text(0.16, 0.78, "PHASE 1: DATA PIPELINE", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#26D9F1")
    ax.text(0.16, 0.64, "MAESTRO v3.0 (962 Pieces)\n5.66M Note Events\nMulti-Process Parsing", ha="center", va="center", fontsize=7.5, color="#F4F3EB")
    ax.text(0.16, 0.44, "3-Tuple Quantization\nPitch (128) | Dur (32) | Step (32)\nmelodyloop/data.py", ha="center", va="center", fontsize=7.5, color="#FFC857")
    ax.text(0.16, 0.24, "Bounded uint8 Dataset\n100,000 Sequences (Seq Len: 32)\nProportional Piece Sampling", ha="center", va="center", fontsize=7.5, color="#F4F3EB")

    # 2. LSTM Training & Checkpointing
    ax.add_patch(patches.FancyBboxPatch((0.36, 0.10), 0.28, 0.74, boxstyle="round,pad=0.02", facecolor="#151D36", edgecolor="#2855D9", lw=1.5))
    ax.text(0.50, 0.78, "PHASE 2: LSTM OPTIMIZATION", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#2855D9")
    ax.text(0.50, 0.64, "MelodyLSTM Core\n128-d Hidden, 167k Params\nParallel Embeddings (p, d, s)", ha="center", va="center", fontsize=7.5, color="#F4F3EB")
    ax.text(0.50, 0.44, "Multi-Task Training (train.py)\nAdam Optimizer (lr=1e-3)\nTotal Cross-Entropy Loss", ha="center", va="center", fontsize=7.5, color="#FFC857")
    ax.text(0.50, 0.24, "Artifact Checkpoint (.pt)\nEpoch 7 Best (Val Loss: 5.9151)\nEarly Stopping at Epoch 15", ha="center", va="center", fontsize=7.5, color="#22C55E")

    # 3. Generation & Synthesis
    ax.add_patch(patches.FancyBboxPatch((0.70, 0.10), 0.28, 0.74, boxstyle="round,pad=0.02", facecolor="#151D36", edgecolor="#FF6B6B", lw=1.5))
    ax.text(0.84, 0.78, "PHASE 3: INFERENCE & AUDIO", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#FF6B6B")
    ax.text(0.84, 0.64, "Autoregressive Sampling\nTemperature Scaling (0.6)\nTop-K Filtering (k=5)", ha="center", va="center", fontsize=7.5, color="#F4F3EB")
    ax.text(0.84, 0.44, "MIDI & Audio Synthesis\nmido Event Export (.mid)\nAdditive Harmonic WAV (.wav)", ha="center", va="center", fontsize=7.5, color="#FFC857")
    ax.text(0.84, 0.24, "Interactive UI (app.py)\nStreamlit Web Dashboard\nMulti-Model Side-by-Side", ha="center", va="center", fontsize=7.5, color="#26D9F1")

    # Flow arrows
    ax.annotate("", xy=(0.36, 0.47), xytext=(0.30, 0.47), arrowprops=dict(arrowstyle="->", color="#26D9F1", lw=2.2))
    ax.annotate("", xy=(0.70, 0.47), xytext=(0.64, 0.47), arrowprops=dict(arrowstyle="->", color="#2855D9", lw=2.2))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    out_path = ASSETS_DIR / "fig_end_to_end_flowchart.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def main():
    print("Generating custom presentation figures...")
    p1 = fig_piano_keyboard()
    print("Generated:", p1)
    p2 = fig_midi_vs_audio()
    print("Generated:", p2)
    p3 = fig_maestro_splits()
    print("Generated:", p3)
    p4 = fig_dataset_scaling()
    print("Generated:", p4)
    p5 = fig_training_loss()
    print("Generated:", p5)
    p6 = fig_evaluation_comparison()
    print("Generated:", p6)
    p7 = fig_piano_roll()
    print("Generated:", p7)
    p8 = fig_lstm_cell_dark()
    print("Generated:", p8)
    p9 = fig_model_architecture_dark()
    print("Generated:", p9)
    p10 = fig_autoregressive_dark()
    print("Generated:", p10)
    p11 = fig_audio_synthesis_dark()
    print("Generated:", p11)
    p12 = fig_end_to_end_dark()
    print("Generated:", p12)
    print("All custom presentation figures created successfully.")


if __name__ == "__main__":
    main()

