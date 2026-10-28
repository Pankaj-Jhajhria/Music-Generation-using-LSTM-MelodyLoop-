"""
Generate clean, light/white-theme publication-grade diagram assets for MelodyLoop_Presentation_Professional.pptx.
Palette:
- Background: #FFFFFF (Pure White)
- Card Surface: #F8FAFC / #F1F5F9 (Subtle Academic Off-White)
- Borders: #CBD5E1 / #94A3B8 (Clean Light Slate)
- Text Dark: #0F172A (Obsidian Charcoal), Secondary: #334155 / #475569
- Accents: #0284C7 (Sky Blue), #2563EB (Royal Blue), #D97706 (Amber Gold), #DC2626 (Coral Red), #16A34A (Green)
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
    """Slide 4: Accurate piano keyboard with Middle C (60), A4 (69), and 88-key bounds (Light Theme)."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(-5, 133)
    ax.set_ylim(-0.35, 1.35)
    ax.axis("off")

    # Title & Subtitle
    ax.text(64, 1.25, "Standard 88-Key Acoustic Piano Range vs. 128 MIDI Note Numbers",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#0F172A")
    ax.text(64, 1.12, "Physical Acoustic Keys: A0 (MIDI 21) to C8 (MIDI 108) | Pitch Representation: Integer [0, 127]",
            ha="center", va="top", fontsize=8.5, color="#475569")

    # Range Bar (Full MIDI 0-127)
    y_bar = 0.68
    h_bar = 0.16
    ax.add_patch(patches.Rectangle((0, y_bar), 128, h_bar, facecolor="#F1F5F9", edgecolor="#CBD5E1", linewidth=1.5, zorder=2))
    # Playable 88 Keys (21 to 108)
    ax.add_patch(patches.Rectangle((21, y_bar), 88, h_bar, facecolor="#DBEAFE", edgecolor="#2563EB", linewidth=2.0, zorder=3))

    # Middle C (60) Highlight on bar
    ax.add_patch(patches.Rectangle((59.3, y_bar - 0.03), 2.4, h_bar + 0.06, facecolor="#FEE2E2", edgecolor="#DC2626", linewidth=1.8, zorder=4))

    # Range Labels
    ax.text(10, y_bar + h_bar/2, "Sub-Audio\n(0-20)", ha="center", va="center", fontsize=7.5, color="#64748B", zorder=5)
    ax.text(64, y_bar + h_bar/2, "Standard 88 Acoustic Piano Keys (MIDI 21 - 108)", ha="center", va="center", fontsize=9, fontweight="bold", color="#1E40AF", zorder=5)
    ax.text(118, y_bar + h_bar/2, "Ultra-High\n(109-127)", ha="center", va="center", fontsize=7.5, color="#64748B", zorder=5)

    # Key callout lines
    ax.plot([21, 21], [y_bar - 0.08, y_bar + h_bar + 0.06], color="#0284C7", linestyle="--", linewidth=1.2)
    ax.text(21, y_bar - 0.10, "A0 (21)\n27.5 Hz", ha="center", va="top", fontsize=7.5, color="#0284C7", fontweight="bold")

    ax.plot([60, 60], [y_bar - 0.08, y_bar + h_bar + 0.05], color="#DC2626", linestyle="-", linewidth=1.5)
    ax.text(60, y_bar + h_bar + 0.07, "Middle C (C4, 60)\n261.63 Hz", ha="center", va="bottom", fontsize=8.5, color="#DC2626", fontweight="bold")

    ax.plot([69, 69], [y_bar - 0.08, y_bar + h_bar + 0.06], color="#D97706", linestyle=":", linewidth=1.5)
    ax.text(69, y_bar - 0.10, "Concert A (A4, 69)\n440.0 Hz", ha="center", va="top", fontsize=7.5, color="#D97706", fontweight="bold")

    ax.plot([108, 108], [y_bar - 0.08, y_bar + h_bar + 0.06], color="#0284C7", linestyle="--", linewidth=1.2)
    ax.text(108, y_bar - 0.10, "C8 (108)\n4186 Hz", ha="center", va="top", fontsize=7.5, color="#0284C7", fontweight="bold")

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
            fc = "#FEE2E2" if is_c4 else "#FFFFFF"
            ec = "#DC2626" if is_c4 else "#94A3B8"
            ax.add_patch(patches.Rectangle((kx, key_y), key_w, key_h, facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=6))
            if is_c4:
                ax.text(kx + key_w/2, key_y + 0.04, "C4 (60)\nMiddle C", ha="center", va="bottom", fontsize=7.5, color="#DC2626", fontweight="bold", zorder=8)
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
            left_p = p - 1
            kx = white_key_x[left_p] + key_w - (b_key_w / 2.0)
            ax.add_patch(patches.Rectangle((kx, b_key_y), b_key_w, b_key_h, facecolor="#0F172A", edgecolor="#475569", linewidth=1.0, zorder=7))

    out_path = ASSETS_DIR / "fig_piano_keyboard.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_midi_vs_audio():
    """Slide 5: Symbolic MIDI instructions vs. Synthesized Audio Waveform (Light Theme)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#FFFFFF")

    # Panel 1: MIDI Symbolic Data
    ax1.set_facecolor("#F8FAFC")
    ax1.set_title("Symbolic MIDI Event Matrix (Discrete Tokens)", color="#0369A1", fontsize=10, fontweight="bold", pad=8)
    ax1.set_xlabel("Time (Seconds)", color="#475569", fontsize=8.5)
    ax1.set_ylabel("MIDI Pitch (0-127)", color="#475569", fontsize=8.5)
    ax1.tick_params(colors="#475569", labelsize=8)
    for spine in ax1.spines.values():
        spine.set_color("#CBD5E1")

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
        ax1.add_patch(patches.Rectangle((start, pitch - 0.4), dur, 0.8, facecolor="#0284C7", edgecolor="#0369A1", linewidth=1.2, alpha=0.9))
        ax1.text(start + dur/2, pitch, name, ha="center", va="center", fontsize=7.5, color="#FFFFFF", fontweight="bold")

    ax1.set_xlim(-0.1, 4.0)
    ax1.set_ylim(55, 76)
    ax1.axhline(60, color="#DC2626", linestyle=":", alpha=0.7, label="Middle C (60)")
    ax1.legend(facecolor="#FFFFFF", edgecolor="#CBD5E1", labelcolor="#0F172A", fontsize=7.5, loc="upper right")

    # Panel 2: Synthesized Audio Waveform
    ax2.set_facecolor("#F8FAFC")
    ax2.set_title("Synthesized Waveform: s(t) = A(t) Σ a_k sin(2π k f_0 t)", color="#B45309", fontsize=10, fontweight="bold", pad=8)
    ax2.set_xlabel("Time (Seconds)", color="#475569", fontsize=8.5)
    ax2.set_ylabel("Amplitude [-1.0, 1.0]", color="#475569", fontsize=8.5)
    ax2.tick_params(colors="#475569", labelsize=8)
    for spine in ax2.spines.values():
        spine.set_color("#CBD5E1")

    t = np.linspace(0, 3.8, 1500)
    wave = np.zeros_like(t)
    for start, dur, pitch, _ in sample_notes:
        f0 = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))
        mask = (t >= start) & (t < start + dur)
        t_note = t[mask] - start
        env = np.exp(-3.5 * t_note / dur)
        sig = 0.6 * np.sin(2 * np.pi * f0 * t_note) + 0.3 * np.sin(4 * np.pi * f0 * t_note) + 0.1 * np.sin(6 * np.pi * f0 * t_note)
        wave[mask] += sig * env

    wave = np.clip(wave, -1.0, 1.0)
    ax2.plot(t, wave, color="#D97706", linewidth=0.9, alpha=0.9)
    ax2.set_xlim(-0.1, 4.0)
    ax2.set_ylim(-1.15, 1.15)
    ax2.axhline(0, color="#94A3B8", linestyle="--", linewidth=0.7, alpha=0.5)

    out_path = ASSETS_DIR / "fig_midi_vs_audio.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_maestro_splits():
    """Slide 6: MAESTRO v3.0.0 official split breakdown (Light Theme)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6), dpi=250, gridspec_kw={'width_ratios': [1.3, 1.0]})
    fig.patch.set_facecolor("#FFFFFF")

    # Segmented horizontal split bar
    ax1.set_facecolor("#FFFFFF")
    ax1.set_xlim(0, 1276)
    ax1.set_ylim(0, 1.5)
    ax1.axis("off")

    ax1.text(0, 1.35, "Official MAESTRO v3.0.0 Dataset Split Distribution", fontsize=11, fontweight="bold", color="#0F172A")
    ax1.text(0, 1.18, "1,276 Virtuosic Piano Performances | International Piano-e-Competition Data", fontsize=8.5, color="#475569")

    # Bars: Train (962), Val (137), Test (177)
    y_b = 0.55
    h_b = 0.40
    ax1.add_patch(patches.Rectangle((0, y_b), 962, h_b, facecolor="#2563EB", edgecolor="#1E40AF", linewidth=1.5))
    ax1.add_patch(patches.Rectangle((962, y_b), 137, h_b, facecolor="#F59E0B", edgecolor="#D97706", linewidth=1.5))
    ax1.add_patch(patches.Rectangle((962 + 137, y_b), 177, h_b, facecolor="#EF4444", edgecolor="#DC2626", linewidth=1.5))

    ax1.text(481, y_b + h_b/2, "TRAINING SET\n962 Files (75.4%)\n5.66M Note Events", ha="center", va="center", color="#FFFFFF", fontsize=8.5, fontweight="bold")
    ax1.text(962 + 68, y_b + h_b/2, "VAL\n137 Files\n(10.7%)", ha="center", va="center", color="#FFFFFF", fontsize=7.5, fontweight="bold")
    ax1.text(962 + 137 + 88, y_b + h_b/2, "TEST\n177 Files\n(13.9%)", ha="center", va="center", color="#FFFFFF", fontsize=7.5, fontweight="bold")

    # Explanatory annotations
    ax1.text(0, 0.25, "• Training Split (962 files): Parameter optimization via gradient backpropagation.\n• Validation Split (137 files): Epoch monitoring & best checkpoint selection (no gradients).\n• Test Split (177 files): Held-out evaluation (e.g. Scriabin Op. 63) - Zero data leakage.", fontsize=8, color="#334155")

    # Pie/Donut Chart on right
    ax2.set_facecolor("#FFFFFF")
    splits = [962, 137, 177]
    colors = ["#2563EB", "#F59E0B", "#EF4444"]
    explode = (0.02, 0.05, 0.05)
    wedges, texts, autotexts = ax2.pie(
        splits,
        labels=["Train (962)", "Val (137)", "Test (177)"],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        explode=explode,
        textprops=dict(color="#0F172A", fontsize=8),
        wedgeprops=dict(width=0.45, edgecolor="#FFFFFF", linewidth=2)
    )
    for at in autotexts:
        at.set_color("#FFFFFF")
        at.set_fontweight("bold")
        at.set_fontsize(7.5)

    out_path = ASSETS_DIR / "fig_maestro_splits.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_dataset_scaling():
    """Slide 7: Visual comparison of Baseline (13 files) vs Expanded (962 files) (Light Theme)."""
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=250)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#F8FAFC")

    metrics = ["Train Files", "Notes Extracted (k)", "Sequences (k)", "Val Files", "Val Seqs (k)"]
    baseline = [13, 64.26, 15.0, 1, 3.92]
    expanded = [962, 5659.3, 100.0, 137, 10.0]

    x = np.arange(len(metrics))
    width = 0.35

    ax.set_yscale('log')
    rects1 = ax.bar(x - width/2, baseline, width, label="Baseline Experiment (v1)", color="#94A3B8", edgecolor="#64748B")
    rects2 = ax.bar(x + width/2, expanded, width, label="Expanded Experiment (v2)", color="#0284C7", edgecolor="#0369A1")

    ax.set_title("Dataset Expansion Metrics: Baseline vs. Expanded Corpus (Log Scale)", color="#0F172A", fontsize=10.5, fontweight="bold", pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=8, color="#0F172A", fontweight="bold")
    ax.tick_params(colors="#475569", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#CBD5E1")
    ax.grid(axis='y', linestyle='--', alpha=0.3, color="#CBD5E1")

    # Add numeric labels on bars
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:g}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 2),
                    textcoords="offset points", ha='center', va='bottom', fontsize=7, color="#475569")
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:g}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 2),
                    textcoords="offset points", ha='center', va='bottom', fontsize=7, color="#0369A1", fontweight="bold")

    ax.legend(facecolor="#FFFFFF", edgecolor="#CBD5E1", labelcolor="#0F172A", fontsize=8, loc="upper left")
    out_path = ASSETS_DIR / "fig_dataset_scaling.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_training_loss():
    """Slide 14: Epoch-by-epoch loss curves from actual logs (Light Theme)."""
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=250)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#F8FAFC")

    epochs = np.arange(1, 16)
    train_loss = [6.3280, 6.0021, 5.8114, 5.6632, 5.5410, 5.4665, 5.2764, 5.2109,
                  5.1482, 5.0911, 5.0423, 5.0012, 4.9654, 4.9380, 4.9121]
    val_loss =   [6.2391, 6.0845, 6.0123, 5.9754, 5.9412, 5.9280, 5.9151, 5.9184,
                  5.9320, 5.9450, 5.9572, 5.9780, 5.9991, 6.0180, 6.0386]

    ax.plot(epochs, train_loss, marker="o", color="#D97706", linewidth=2.0, markersize=5, label="Training Loss (train.py)")
    ax.plot(epochs, val_loss, marker="s", color="#2563EB", linewidth=2.0, markersize=5, label="Validation Loss (137 Val Pieces)")

    # Highlight Epoch 7 minimum
    ax.scatter(7, 5.9151, color="#16A34A", s=140, zorder=5, edgecolor="#0F172A", linewidth=1.5, label="Best Checkpoint (Ep 7: 5.9151)")
    ax.annotate("Best Val Loss: 5.9151\n(Saved to best_model_expanded.pt)",
                xy=(7, 5.9151), xytext=(3.2, 6.20),
                arrowprops=dict(arrowstyle="->", color="#16A34A", lw=1.5),
                fontsize=8, color="#16A34A", fontweight="bold",
                bbox=dict(facecolor="#FFFFFF", edgecolor="#16A34A", boxstyle="round,pad=0.3"))

    # Early stopping mark at Epoch 15
    ax.axvline(15, color="#DC2626", linestyle="--", linewidth=1.5, alpha=0.8)
    ax.text(14.8, 5.4, "Early Stopping\n(Patience 8, Ep 15)", ha="right", va="center", color="#DC2626", fontsize=7.5, fontweight="bold")

    ax.set_title("MelodyLoop Expanded Training & Validation Loss History Across 15 Epochs", color="#0F172A", fontsize=10.5, fontweight="bold", pad=10)
    ax.set_xlabel("Training Epoch", color="#475569", fontsize=8.5)
    ax.set_ylabel("Joint Cross-Entropy Loss", color="#475569", fontsize=8.5)
    ax.set_xticks(epochs)
    ax.set_xlim(0.5, 16.5)
    ax.set_ylim(4.7, 6.5)
    ax.tick_params(colors="#475569", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#CBD5E1")
    ax.grid(True, linestyle="--", alpha=0.3, color="#CBD5E1")
    ax.legend(loc=(0.58, 0.70), facecolor="#FFFFFF", edgecolor="#CBD5E1", labelcolor="#0F172A", fontsize=7.5)

    out_path = ASSETS_DIR / "fig_training_loss.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_lstm_cell_dark():
    """Slide 11: Clean Light-themed LSTM Cell Gates and Equations."""
    fig, ax = plt.subplots(figsize=(10, 4.0), dpi=250)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    ax.text(0.5, 0.96, "LSTM Internal Cell Architecture & Mathematical Gate Formulations",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#0F172A", transform=ax.transAxes)

    # Main cell body
    ax.add_patch(patches.FancyBboxPatch(
        (0.18, 0.12), 0.64, 0.72, boxstyle="round,pad=0.03,rounding_size=0.04",
        facecolor="#F8FAFC", edgecolor="#0284C7", linewidth=2.0, zorder=2
    ))
    ax.text(0.5, 0.81, "LSTM Cell Recurrent Core (Hidden Dim = 128)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0369A1", zorder=3)

    # Inputs and Outputs lines
    ax.annotate("", xy=(0.18, 0.68), xytext=(0.04, 0.68), arrowprops=dict(arrowstyle="->", color="#D97706", lw=2.2))
    ax.text(0.09, 0.72, "Cell State\n$C_{t-1}$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#D97706")

    ax.annotate("", xy=(0.18, 0.28), xytext=(0.04, 0.28), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=2.2))
    ax.text(0.09, 0.32, "Hidden\n$h_{t-1}$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#0284C7")

    ax.annotate("", xy=(0.32, 0.12), xytext=(0.32, 0.02), arrowprops=dict(arrowstyle="->", color="#16A34A", lw=2.2))
    ax.text(0.32, 0.00, "Input Vector $x_t$\n(Dim=128)", ha="center", va="top", fontsize=8.5, fontweight="bold", color="#16A34A")

    # Gate Boxes inside Cell
    # Forget Gate
    ax.add_patch(patches.Rectangle((0.24, 0.40), 0.10, 0.16, facecolor="#FEE2E2", edgecolor="#DC2626", lw=1.5, zorder=3))
    ax.text(0.29, 0.48, "Forget\nGate $\\sigma$\n$f_t$", ha="center", va="center", fontsize=8, fontweight="bold", color="#DC2626", zorder=4)

    # Input Gate
    ax.add_patch(patches.Rectangle((0.38, 0.40), 0.10, 0.16, facecolor="#E0F2FE", edgecolor="#0284C7", lw=1.5, zorder=3))
    ax.text(0.43, 0.48, "Input\nGate $\\sigma$\n$i_t$", ha="center", va="center", fontsize=8, fontweight="bold", color="#0369A1", zorder=4)

    # Candidate Cell State
    ax.add_patch(patches.Rectangle((0.52, 0.40), 0.10, 0.16, facecolor="#DCFCE7", edgecolor="#16A34A", lw=1.5, zorder=3))
    ax.text(0.57, 0.48, "Candidate\n$\\tanh$\n$\\tilde{C}_t$", ha="center", va="center", fontsize=8, fontweight="bold", color="#16A34A", zorder=4)

    # Output Gate
    ax.add_patch(patches.Rectangle((0.66, 0.40), 0.10, 0.16, facecolor="#FEF3C7", edgecolor="#D97706", lw=1.5, zorder=3))
    ax.text(0.71, 0.48, "Output\nGate $\\sigma$\n$o_t$", ha="center", va="center", fontsize=8, fontweight="bold", color="#D97706", zorder=4)

    # Operation Circles
    ax.add_patch(patches.Circle((0.29, 0.68), 0.024, facecolor="#FEE2E2", edgecolor="#DC2626", lw=1.5, zorder=4))
    ax.text(0.29, 0.68, "$\\times$", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#DC2626", zorder=5)

    ax.add_patch(patches.Circle((0.50, 0.58), 0.024, facecolor="#DCFCE7", edgecolor="#16A34A", lw=1.5, zorder=4))
    ax.text(0.50, 0.58, "$\\times$", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#16A34A", zorder=5)

    ax.add_patch(patches.Circle((0.50, 0.68), 0.024, facecolor="#FEF3C7", edgecolor="#D97706", lw=1.5, zorder=4))
    ax.text(0.50, 0.68, "$+$", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#D97706", zorder=5)

    # Outputs
    ax.annotate("", xy=(0.96, 0.68), xytext=(0.82, 0.68), arrowprops=dict(arrowstyle="->", color="#D97706", lw=2.2))
    ax.text(0.91, 0.72, "Cell State\n$C_t$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#D97706")

    ax.annotate("", xy=(0.96, 0.28), xytext=(0.82, 0.28), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=2.2))
    ax.text(0.91, 0.32, "Hidden\n$h_t$", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#0284C7")

    # Math equations panel at bottom
    ax.text(0.5, 0.17, "Governing Equations: $f_t = \\sigma(W_f [h_{t-1}, x_t] + b_f)$ | $i_t = \\sigma(W_i [h_{t-1}, x_t] + b_i)$ | $\\tilde{C}_t = \\tanh(W_c [h_{t-1}, x_t] + b_c)$\n$C_t = f_t \\odot C_{t-1} + i_t \\odot \\tilde{C}_t$ | $o_t = \\sigma(W_o [h_{t-1}, x_t] + b_o)$ | $h_t = o_t \\odot \\tanh(C_t)$",
            ha="center", va="center", fontsize=8, color="#0F172A", bbox=dict(facecolor="#F1F5F9", edgecolor="#CBD5E1", boxstyle="round,pad=0.4"))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    out_path = ASSETS_DIR / "fig_lstm_cell.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_model_architecture_dark():
    """Slide 12: Clean Light-themed MelodyLSTM PyTorch Architecture & Multi-Task Heads."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    ax.text(0.5, 0.96, "MelodyLSTM Multi-Task Neural Network Architecture (167,104 Parameters)",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#0F172A", transform=ax.transAxes)

    # 1. Inputs
    ax.add_patch(patches.Rectangle((0.02, 0.40), 0.13, 0.35, facecolor="#F1F5F9", edgecolor="#94A3B8", lw=1.5))
    ax.text(0.085, 0.57, "Input Indices\n[B, 32, 3]\nPitch (0-127)\nDur (0-31)\nStep (0-31)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0F172A")

    # 2. Embedding Layers
    ax.add_patch(patches.Rectangle((0.19, 0.66), 0.15, 0.18, facecolor="#E0F2FE", edgecolor="#0284C7", lw=1.5))
    ax.text(0.265, 0.75, "Pitch Embed\n128 -> 64\n(8,192 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0369A1")

    ax.add_patch(patches.Rectangle((0.19, 0.44), 0.15, 0.18, facecolor="#E0F2FE", edgecolor="#0284C7", lw=1.5))
    ax.text(0.265, 0.53, "Duration Embed\n32 -> 32\n(1,024 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0369A1")

    ax.add_patch(patches.Rectangle((0.19, 0.22), 0.15, 0.18, facecolor="#E0F2FE", edgecolor="#0284C7", lw=1.5))
    ax.text(0.265, 0.31, "Step Embed\n32 -> 32\n(1,024 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0369A1")

    # 3. Concatenate
    ax.add_patch(patches.Rectangle((0.38, 0.35), 0.12, 0.42, facecolor="#FEF3C7", edgecolor="#D97706", lw=1.5))
    ax.text(0.44, 0.56, "Concatenate\n64 + 32 + 32\n= 128 Dim\nDropout(0.1)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#B45309")

    # 4. LSTM Core
    ax.add_patch(patches.Rectangle((0.54, 0.33), 0.16, 0.46, facecolor="#2563EB", edgecolor="#1E40AF", lw=2.0))
    ax.text(0.62, 0.56, "LSTM Layer\nInput: 128\nHidden: 128\n1 Layer\n(132,096 params)", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#FFFFFF")

    # 5. Output Heads
    ax.add_patch(patches.Rectangle((0.74, 0.66), 0.15, 0.18, facecolor="#E0F2FE", edgecolor="#0284C7", lw=1.5))
    ax.text(0.815, 0.75, "Pitch Head\nLinear(128 -> 128)\n(16,512 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0369A1")

    ax.add_patch(patches.Rectangle((0.74, 0.44), 0.15, 0.18, facecolor="#E0F2FE", edgecolor="#0284C7", lw=1.5))
    ax.text(0.815, 0.53, "Duration Head\nLinear(128 -> 32)\n(4,128 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0369A1")

    ax.add_patch(patches.Rectangle((0.74, 0.22), 0.15, 0.18, facecolor="#E0F2FE", edgecolor="#0284C7", lw=1.5))
    ax.text(0.815, 0.31, "Step Head\nLinear(128 -> 32)\n(4,128 params)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0369A1")

    # Connectors
    ax.annotate("", xy=(0.19, 0.75), xytext=(0.15, 0.65), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.5))
    ax.annotate("", xy=(0.19, 0.53), xytext=(0.15, 0.57), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.5))
    ax.annotate("", xy=(0.19, 0.31), xytext=(0.15, 0.49), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.5))

    ax.annotate("", xy=(0.38, 0.56), xytext=(0.34, 0.56), arrowprops=dict(arrowstyle="->", color="#D97706", lw=1.8))
    ax.annotate("", xy=(0.54, 0.56), xytext=(0.50, 0.56), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.8))

    ax.annotate("", xy=(0.74, 0.75), xytext=(0.70, 0.62), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.5))
    ax.annotate("", xy=(0.74, 0.53), xytext=(0.70, 0.56), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.5))
    ax.annotate("", xy=(0.74, 0.31), xytext=(0.70, 0.50), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.5))

    # Loss callout at bottom
    ax.text(0.5, 0.09, "Multi-Task Loss Objective: $\\mathcal{L}_{total} = \\text{CrossEntropy}(\\hat{y}_p, y_p) + \\text{CrossEntropy}(\\hat{y}_d, y_d) + \\text{CrossEntropy}(\\hat{y}_s, y_s)$",
            ha="center", va="center", fontsize=8, color="#0F172A", bbox=dict(facecolor="#F1F5F9", edgecolor="#CBD5E1", boxstyle="round,pad=0.3"))

    ax.set_xlim(0, 0.95)
    ax.set_ylim(0, 1)
    ax.axis("off")
    out_path = ASSETS_DIR / "fig_model_architecture.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_autoregressive_dark():
    """Slide 16: Clean Light-themed Autoregressive Sampling Loop & Top-K Filtering."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6), dpi=250)
    fig.patch.set_facecolor("#FFFFFF")

    # Left: Autoregressive Loop
    ax1.set_facecolor("#F8FAFC")
    ax1.set_title("1. Autoregressive Rolling Context Loop", fontsize=9.5, fontweight="bold", color="#0369A1", pad=8)

    steps = [
        "Initial Seed Buffer (32 notes)",
        "MelodyLSTM Forward Pass",
        "Sample Next Event (p, d, s)",
        "Slide Window: Pop oldest, push new",
        "Repeat N times -> Export MIDI & WAV"
    ]
    for i, s in enumerate(steps):
        y = 0.82 - i * 0.17
        fc = "#E0F2FE" if i in (0, 3) else "#DCFCE7" if i == 2 else "#DBEAFE" if i == 1 else "#FEF3C7"
        ec = "#0284C7" if i in (0, 3) else "#16A34A" if i == 2 else "#2563EB" if i == 1 else "#D97706"
        tc = "#0369A1" if i in (0, 3) else "#15803D" if i == 2 else "#1E40AF" if i == 1 else "#B45309"
        ax1.add_patch(patches.FancyBboxPatch((0.08, y), 0.84, 0.12, boxstyle="round,pad=0.02", facecolor=fc, edgecolor=ec, lw=1.2))
        ax1.text(0.5, y + 0.06, s, ha="center", va="center", fontsize=8.0, fontweight="bold", color=tc)
        if i < len(steps) - 1:
            ax1.annotate("", xy=(0.5, y - 0.01), xytext=(0.5, y + 0.01), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.5))

    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis("off")

    # Right: Temperature & Top-K Effect
    ax2.set_facecolor("#F8FAFC")
    ax2.set_title("2. Temperature Scaling & Top-K=5 Filtering", fontsize=9.5, fontweight="bold", color="#B45309", pad=8)

    candidates = ["C4 (60)", "E4 (64)", "G4 (67)", "D4 (62)", "A4 (69)", "F4 (65)", "B4 (71)", "C#4 (61)"]
    raw_probs = [0.40, 0.25, 0.18, 0.08, 0.04, 0.03, 0.015, 0.005]
    colors = ["#0284C7", "#0284C7", "#0284C7", "#0284C7", "#0284C7", "#94A3B8", "#94A3B8", "#94A3B8"]

    bars = ax2.bar(candidates, raw_probs, color=colors, edgecolor="#0369A1", width=0.6, zorder=3)
    ax2.axvline(4.5, color="#DC2626", linestyle="--", linewidth=1.8, zorder=4)
    ax2.text(2.2, 0.35, "Top-K = 5 Candidates\n(Kept & Renormalized)", ha="center", va="center", fontsize=7.5, color="#0369A1", fontweight="bold",
             bbox=dict(facecolor="#FFFFFF", edgecolor="#0284C7", boxstyle="round,pad=0.2"))
    ax2.text(6.0, 0.28, "Tail Pruned\n(-inf logits)", ha="center", va="center", fontsize=7.5, color="#DC2626", fontweight="bold",
             bbox=dict(facecolor="#FFFFFF", edgecolor="#DC2626", boxstyle="round,pad=0.2"))

    ax2.set_ylabel("Probability $P(y_i)$", fontsize=8, color="#475569")
    ax2.tick_params(axis="x", rotation=35, labelsize=7.5, colors="#0F172A")
    ax2.tick_params(axis="y", labelsize=7.5, colors="#475569")
    for spine in ax2.spines.values():
        spine.set_color("#CBD5E1")
    ax2.set_ylim(0, 0.46)

    out_path = ASSETS_DIR / "fig_autoregressive_loop.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_audio_synthesis_dark():
    """Slide 17: Clean Light-themed Additive Synthesis & ADSR Decay Mechanics."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6), dpi=250)
    fig.patch.set_facecolor("#FFFFFF")

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
    ax1.set_facecolor("#F8FAFC")
    ax1.set_title("1. Additive Harmonics ($f_0 = 261.63$ Hz)", fontsize=9.5, fontweight="bold", color="#0369A1", pad=8)
    ax1.plot(t[:200]*1000, f1[:200], label="Fundamental f0 (60%)", color="#0284C7", lw=1.2)
    ax1.plot(t[:200]*1000, f2[:200], label="2nd Harmonic 2f0 (25%)", color="#16A34A", lw=1.0, linestyle="--")
    ax1.plot(t[:200]*1000, f3[:200], label="3rd Harmonic 3f0 (15%)", color="#D97706", lw=1.0, linestyle=":")
    ax1.plot(t[:200]*1000, combined[:200], label="Composite Wave", color="#0F172A", lw=1.6)
    ax1.set_xlabel("Time (milliseconds)", fontsize=8, color="#475569")
    ax1.set_ylabel("Amplitude", fontsize=8, color="#475569")
    ax1.tick_params(colors="#475569", labelsize=7.5)
    for spine in ax1.spines.values():
        spine.set_color("#CBD5E1")
    ax1.legend(loc="upper right", fontsize=6.5, facecolor="#FFFFFF", edgecolor="#CBD5E1", labelcolor="#0F172A")

    # Right: ADSR Envelope
    ax2.set_facecolor("#F8FAFC")
    ax2.set_title("2. ADSR Decay Envelope & Resulting Audio", fontsize=9.5, fontweight="bold", color="#B45309", pad=8)

    envelope = np.exp(-3.0 * t / dur)
    attack_len = int(0.005 * sr)
    envelope[:attack_len] *= np.linspace(0.0, 1.0, attack_len)
    release_len = int(0.01 * sr)
    envelope[-release_len:] *= np.linspace(1.0, 0.0, release_len)

    audio = combined * envelope
    ax2.plot(t, envelope, color="#DC2626", linewidth=1.5, linestyle="--", label="Decay Envelope", zorder=4)
    ax2.plot(t, audio, color="#0284C7", linewidth=0.6, alpha=0.85, label="Synthesized Waveform", zorder=3)
    ax2.set_xlabel("Time (seconds)", fontsize=8, color="#475569")
    ax2.set_ylabel("Normalized Amplitude", fontsize=8, color="#475569")
    ax2.tick_params(colors="#475569", labelsize=7.5)
    for spine in ax2.spines.values():
        spine.set_color("#CBD5E1")
    ax2.legend(loc="upper right", fontsize=6.5, facecolor="#FFFFFF", edgecolor="#CBD5E1", labelcolor="#0F172A")

    out_path = ASSETS_DIR / "fig_audio_synthesis.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def fig_end_to_end_dark():
    """Slide 3: Clean Light-themed complete end-to-end system workflow."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    ax.text(0.5, 0.96, "MelodyLoop Complete End-to-End Deep Learning Architecture Pipeline",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#0F172A", transform=ax.transAxes)

    # 3 Phase containers
    # 1. Ingestion & Preprocessing
    ax.add_patch(patches.FancyBboxPatch((0.02, 0.10), 0.28, 0.74, boxstyle="round,pad=0.02", facecolor="#F8FAFC", edgecolor="#0284C7", lw=1.5))
    ax.text(0.16, 0.78, "PHASE 1: DATA PIPELINE", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0369A1")
    ax.text(0.16, 0.64, "MAESTRO v3.0 (962 Pieces)\n5.66M Note Events\nMulti-Process Parsing", ha="center", va="center", fontsize=7.5, color="#0F172A")
    ax.text(0.16, 0.44, "3-Tuple Quantization\nPitch (128) | Dur (32) | Step (32)\nmelodyloop/data.py", ha="center", va="center", fontsize=7.5, color="#D97706")
    ax.text(0.16, 0.24, "Bounded uint8 Dataset\n100,000 Sequences (Seq Len: 32)\nProportional Piece Sampling", ha="center", va="center", fontsize=7.5, color="#0F172A")

    # 2. LSTM Training & Checkpointing
    ax.add_patch(patches.FancyBboxPatch((0.36, 0.10), 0.28, 0.74, boxstyle="round,pad=0.02", facecolor="#F8FAFC", edgecolor="#2563EB", lw=1.5))
    ax.text(0.50, 0.78, "PHASE 2: LSTM OPTIMIZATION", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1E40AF")
    ax.text(0.50, 0.64, "MelodyLSTM Core\n128-d Hidden, 167k Params\nParallel Embeddings (p, d, s)", ha="center", va="center", fontsize=7.5, color="#0F172A")
    ax.text(0.50, 0.44, "Multi-Task Training (train.py)\nAdam Optimizer (lr=1e-3)\nTotal Cross-Entropy Loss", ha="center", va="center", fontsize=7.5, color="#D97706")
    ax.text(0.50, 0.24, "Artifact Checkpoint (.pt)\nEpoch 7 Best (Val Loss: 5.9151)\nEarly Stopping at Epoch 15", ha="center", va="center", fontsize=7.5, color="#16A34A")

    # 3. Generation & Synthesis
    ax.add_patch(patches.FancyBboxPatch((0.70, 0.10), 0.28, 0.74, boxstyle="round,pad=0.02", facecolor="#F8FAFC", edgecolor="#DC2626", lw=1.5))
    ax.text(0.84, 0.78, "PHASE 3: INFERENCE & AUDIO", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#DC2626")
    ax.text(0.84, 0.64, "Autoregressive Sampling\nTemperature Scaling (0.6)\nTop-K Filtering (k=5)", ha="center", va="center", fontsize=7.5, color="#0F172A")
    ax.text(0.84, 0.44, "MIDI & Audio Synthesis\nmido Event Export (.mid)\nAdditive Harmonic WAV (.wav)", ha="center", va="center", fontsize=7.5, color="#D97706")
    ax.text(0.84, 0.24, "Interactive UI (app.py)\nStreamlit Web Dashboard\nMulti-Model Side-by-Side", ha="center", va="center", fontsize=7.5, color="#0369A1")

    # Flow arrows
    ax.annotate("", xy=(0.36, 0.47), xytext=(0.30, 0.47), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=2.2))
    ax.annotate("", xy=(0.70, 0.47), xytext=(0.64, 0.47), arrowprops=dict(arrowstyle="->", color="#2563EB", lw=2.2))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    out_path = ASSETS_DIR / "fig_end_to_end_flowchart.png"
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_path


def main():
    print("Generating clean light-theme presentation figures...")
    fig_piano_keyboard()
    fig_midi_vs_audio()
    fig_maestro_splits()
    fig_dataset_scaling()
    fig_training_loss()
    fig_lstm_cell_dark()
    fig_model_architecture_dark()
    fig_autoregressive_dark()
    fig_audio_synthesis_dark()
    fig_end_to_end_dark()
    print("All 10 required light-theme figures generated successfully!")


if __name__ == "__main__":
    main()
