"""
Generate clean, publication-grade diagram figures for the MelodyLoop Comprehensive Guide PDF.
These diagrams illustrate key concepts:
1. Piano Keyboard layout vs MIDI Pitch Numbers (0-127 vs 88 keys)
2. Symbolic MIDI vs Audio Waveforms vs Synthesis
3. MAESTRO Dataset Splits & File Counts
4. Data Preprocessing & Quantization Pipeline
5. LSTM Cell Gate Architecture & Mathematical Equations
6. MelodyLSTM PyTorch Architecture & Tensor Shapes
7. Actual Training & Validation Loss Curves from training.log
8. Autoregressive Generation Loop & Sampling Strategy
9. Additive Harmonic Synthesis & ADSR Envelope
10. Master End-to-End Workflow Flowchart
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

FIGURES_DIR = Path("artifacts/doc_figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"


def fig1_piano_and_midi():
    """Figure 1: Piano keyboard layout vs MIDI numbers (0-127)."""
    fig, ax = plt.subplots(figsize=(9, 3.2), dpi=220)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    # Title & Subtitle
    ax.text(0.5, 0.93, "Standard 88-Key Piano Keyboard vs. MIDI Pitch Numbers (0-127)",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#0f172a", transform=ax.transAxes)
    ax.text(0.5, 0.85, "Physical Piano Range: A0 (MIDI 21) to C8 (MIDI 108) | Middle C = C4 (MIDI 60)",
            ha="center", va="top", fontsize=8.5, color="#475569", transform=ax.transAxes)

    # Draw timeline / range bar
    # Full MIDI range 0 to 127
    y_bar = 0.52
    h_bar = 0.16
    ax.add_patch(patches.Rectangle((0, y_bar), 128, h_bar, facecolor="#e2e8f0", edgecolor="#94a3b8", linewidth=1.2, zorder=2))
    
    # Playable piano range 21 to 108
    ax.add_patch(patches.Rectangle((21, y_bar), 88, h_bar, facecolor="#93c5fd", edgecolor="#2563eb", linewidth=1.5, zorder=3))

    # Highlight Middle C (60)
    ax.add_patch(patches.Rectangle((59.5, y_bar - 0.03), 2, h_bar + 0.06, facecolor="#ef4444", edgecolor="#b91c1c", linewidth=1.5, zorder=4))

    # Annotations
    ax.text(10, y_bar + h_bar/2, "Sub-Audio / Unused\n(0 - 20)", ha="center", va="center", fontsize=7.5, color="#64748b", zorder=5)
    ax.text(65, y_bar + h_bar/2, "Standard 88 Acoustic Piano Keys (21 - 108)", ha="center", va="center", fontsize=9, fontweight="bold", color="#1e3a8a", zorder=5)
    ax.text(118, y_bar + h_bar/2, "Ultra-High\n(109 - 127)", ha="center", va="center", fontsize=7.5, color="#64748b", zorder=5)

    # Markers
    ax.plot([21, 21], [y_bar - 0.08, y_bar + h_bar + 0.08], color="#1d4ed8", linestyle="--", linewidth=1.2)
    ax.text(21, y_bar - 0.10, "A0 (21)\n27.5 Hz", ha="center", va="top", fontsize=7.5, color="#1e40af", fontweight="bold")

    ax.plot([60, 60], [y_bar - 0.08, y_bar + h_bar + 0.08], color="#dc2626", linestyle="-", linewidth=1.5)
    ax.text(60, y_bar + h_bar + 0.10, "Middle C (C4, 60)\n261.63 Hz", ha="center", va="bottom", fontsize=8, color="#b91c1c", fontweight="bold")

    ax.plot([69, 69], [y_bar - 0.08, y_bar + h_bar + 0.08], color="#047857", linestyle=":", linewidth=1.2)
    ax.text(69, y_bar - 0.10, "Concert A (A4, 69)\n440.00 Hz", ha="center", va="top", fontsize=7.5, color="#047857", fontweight="bold")

    ax.plot([108, 108], [y_bar - 0.08, y_bar + h_bar + 0.08], color="#1d4ed8", linestyle="--", linewidth=1.2)
    ax.text(108, y_bar - 0.10, "C8 (108)\n4186 Hz", ha="center", va="top", fontsize=7.5, color="#1e40af", fontweight="bold")

    # Bottom keys illustration (representing 2 octaves around Middle C: C3 (48) to C5 (72))
    key_y = 0.06
    key_w = 2.4
    key_h = 0.18
    octave_start = 48
    white_notes = [0, 2, 4, 5, 7, 9, 11]
    black_notes = [1, 3, 6, 8, 10]
    
    # White keys
    w_idx = 0
    for p in range(48, 73):
        semitone = (p - 48) % 12
        if semitone in white_notes:
            kx = 20 + w_idx * key_w
            fc = "#fee2e2" if p == 60 else "#ffffff"
            ec = "#b91c1c" if p == 60 else "#334155"
            ax.add_patch(patches.Rectangle((kx, key_y), key_w, key_h, facecolor=fc, edgecolor=ec, linewidth=1, zorder=6))
            if p == 60:
                ax.text(kx + key_w/2, key_y + 0.03, "C4\n(60)", ha="center", va="bottom", fontsize=6.5, color="#991b1b", fontweight="bold", zorder=8)
            elif p in (48, 72):
                name = "C3\n(48)" if p == 48 else "C5\n(72)"
                ax.text(kx + key_w/2, key_y + 0.03, name, ha="center", va="bottom", fontsize=6.5, color="#475569", zorder=8)
            w_idx += 1

    # Black keys
    w_idx = 0
    for p in range(48, 72):
        semitone = (p - 48) % 12
        if semitone in white_notes:
            # check if next is black
            if (semitone + 1) in black_notes:
                bx = 20 + w_idx * key_w + key_w * 0.65
                ax.add_patch(patches.Rectangle((bx, key_y + key_h*0.38), key_w*0.65, key_h*0.62, facecolor="#1e293b", edgecolor="#0f172a", linewidth=0.8, zorder=7))
            w_idx += 1

    ax.text(8, key_y + key_h/2, "Piano Keyboard\nZoom (C3 - C5):", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#334155")

    ax.set_xlim(-2, 130)
    ax.set_ylim(-0.02, 1.0)
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig1_piano_midi.png", dpi=220)
    plt.close(fig)


def fig2_symbolic_vs_audio():
    """Figure 2: Symbolic MIDI Instructions vs Raw Audio Waveform."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.2), dpi=220)
    fig.patch.set_facecolor("#ffffff")

    # Panel 1: Symbolic MIDI Events (Piano Roll)
    ax1.set_facecolor("#f8fafc")
    ax1.set_title("1. Symbolic MIDI Events (Instructions)", fontsize=10, fontweight="bold", color="#0f172a", pad=8)
    
    notes = [
        {"pitch": 60, "start": 0.0, "dur": 0.45, "vel": 85, "name": "C4"},
        {"pitch": 64, "start": 0.3, "dur": 0.40, "vel": 80, "name": "E4"},
        {"pitch": 67, "start": 0.55, "dur": 0.50, "vel": 90, "name": "G4"},
        {"pitch": 72, "start": 0.85, "dur": 0.60, "vel": 95, "name": "C5"},
    ]
    colors = ["#2563eb", "#059669", "#d97706", "#7c3aed"]
    
    for i, n in enumerate(notes):
        ax1.barh(n["pitch"], n["dur"], left=n["start"], height=1.6, color=colors[i], edgecolor="#0f172a", alpha=0.9, zorder=3)
        ax1.text(n["start"] + n["dur"]/2, n["pitch"], f"{n['name']} (vel={n['vel']})", ha="center", va="center", color="#ffffff", fontsize=7.5, fontweight="bold", zorder=4)

    ax1.set_xlim(-0.05, 1.6)
    ax1.set_ylim(57, 75)
    ax1.set_xlabel("Time (seconds)", fontsize=8.5, color="#334155")
    ax1.set_ylabel("MIDI Pitch (0-127)", fontsize=8.5, color="#334155")
    ax1.grid(True, linestyle="--", alpha=0.3, color="#94a3b8")
    ax1.tick_params(labelsize=8)
    ax1.text(0.05, 0.08, "Data: ~30 bytes\nNo sound samples, just instructions!", transform=ax1.transAxes, fontsize=7.5, bbox=dict(facecolor="#f1f5f9", edgecolor="#cbd5e1", boxstyle="round,pad=0.3"))

    # Panel 2: Synthesized Audio Waveform (WAV)
    ax2.set_facecolor("#f8fafc")
    ax2.set_title("2. Acoustic Audio Waveform (WAV / MP3)", fontsize=10, fontweight="bold", color="#0f172a", pad=8)
    
    # Generate a realistic additive synthesis wave
    sr = 4000
    t = np.linspace(0, 1.5, int(sr * 1.5))
    waveform = np.zeros_like(t)
    for n in notes:
        freq = 440.0 * (2.0 ** ((n["pitch"] - 69.0) / 12.0))
        mask = (t >= n["start"]) & (t < n["start"] + n["dur"])
        t_note = t[mask] - n["start"]
        env = np.exp(-3.5 * t_note / n["dur"])
        sig = (0.6 * np.sin(2 * np.pi * freq * t_note) + 0.25 * np.sin(4 * np.pi * freq * t_note)) * env
        waveform[mask] += sig

    waveform = waveform / (np.max(np.abs(waveform)) + 1e-5) * 0.9
    ax2.plot(t, waveform, color="#2563eb", linewidth=0.7, zorder=3)
    ax2.set_xlim(-0.05, 1.6)
    ax2.set_ylim(-1.1, 1.1)
    ax2.set_xlabel("Time (seconds)", fontsize=8.5, color="#334155")
    ax2.set_ylabel("Amplitude [-1.0, +1.0]", fontsize=8.5, color="#334155")
    ax2.grid(True, linestyle="--", alpha=0.3, color="#94a3b8")
    ax2.tick_params(labelsize=8)
    ax2.text(0.05, 0.08, "Data: ~132,000 samples @ 44.1kHz\nPhysical air pressure vibrations", transform=ax2.transAxes, fontsize=7.5, bbox=dict(facecolor="#f1f5f9", edgecolor="#cbd5e1", boxstyle="round,pad=0.3"))

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig2_symbolic_vs_audio.png", dpi=220)
    plt.close(fig)


def fig3_dataset_and_splits():
    """Figure 3: MAESTRO v3.0 Dataset composition and split distribution."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.2), dpi=220)
    fig.patch.set_facecolor("#ffffff")

    # Left: Splits Pie Chart
    splits = ["Train (962 files, 75.4%)", "Test (177 files, 13.9%)", "Val (137 files, 10.7%)"]
    sizes = [962, 177, 137]
    colors = ["#2563eb", "#059669", "#d97706"]
    explode = (0.04, 0.05, 0.05)

    wedges, texts, autotexts = ax1.pie(
        sizes, explode=explode, labels=splits, colors=colors, autopct="%1.1f%%",
        startangle=140, textprops=dict(color="#1e293b", fontsize=7.5)
    )
    for at in autotexts:
        at.set_fontsize(7.5)
        at.set_weight("bold")
        at.set_color("#ffffff")
    ax1.set_title("MAESTRO v3.0 Splits\n(1,276 Total Virtuoso Performances)", fontsize=9.5, fontweight="bold", color="#0f172a")

    # Right: Years Breakdown Bar Chart
    ax2.set_facecolor("#f8fafc")
    years = ["2004", "2006", "2008", "2009", "2011", "2013", "2014", "2015", "2017", "2018"]
    counts = [132, 115, 147, 125, 163, 127, 105, 129, 140, 93]
    
    bars = ax2.bar(years, counts, color="#3b82f6", edgecolor="#1d4ed8", width=0.65, zorder=3)
    ax2.set_title("Year-wise Performance Distribution (2004–2018)", fontsize=9.5, fontweight="bold", color="#0f172a")
    ax2.set_xlabel("Competition Year", fontsize=8.5, color="#334155")
    ax2.set_ylabel("Number of MIDI Files", fontsize=8.5, color="#334155")
    ax2.grid(True, linestyle="--", alpha=0.3, color="#94a3b8", axis="y")
    ax2.tick_params(labelsize=8)

    for b in bars:
        h = b.get_height()
        ax2.annotate(f"{h}", xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 2),
                     textcoords="offset points", ha="center", va="bottom", fontsize=7.5, color="#1e293b")

    ax2.set_ylim(0, 185)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig3_dataset_splits.png", dpi=220)
    plt.close(fig)


def fig4_preprocessing_pipeline():
    """Figure 4: Data Preprocessing, Quantization, and Sequence Construction."""
    fig, ax = plt.subplots(figsize=(9.5, 3.4), dpi=220)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    ax.text(0.5, 0.95, "MelodyLoop Data Preprocessing Pipeline (data.py)",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#0f172a", transform=ax.transAxes)

    steps = [
        ("1. Raw MIDI Parser", "mido reads note_on\n& note_off events;\ncalculates start & dur"),
        ("2. Chronological Sort", "Sorts notes by\n(start_time, pitch);\ncalculates step to next"),
        ("3. Quantization", "Pitch: 0-127 (128)\nDuration: 32 bins\nStep: 32 bins"),
        ("4. Sliding Window", "Seq Length = 32\nStride = 4\nInput: (N, 32, 3)"),
        ("5. PyTorch Dataset", "Targets: Next note\ny_pitch, y_dur, y_step\nBatches = 32")
    ]

    box_w = 0.16
    box_h = 0.52
    y_pos = 0.22

    for i, (title, desc) in enumerate(steps):
        x = 0.04 + i * 0.19
        # Card
        ax.add_patch(patches.FancyBboxPatch(
            (x, y_pos), box_w, box_h, boxstyle="round,pad=0.02,rounding_size=0.03",
            facecolor="#eff6ff" if i < 4 else "#ecfdf5",
            edgecolor="#2563eb" if i < 4 else "#059669",
            linewidth=1.3, zorder=2
        ))
        ax.text(x + box_w/2, y_pos + box_h - 0.06, title, ha="center", va="top", fontsize=8.5, fontweight="bold",
                color="#1e3a8a" if i < 4 else "#065f46", zorder=3)
        ax.text(x + box_w/2, y_pos + box_h/2 - 0.05, desc, ha="center", va="center", fontsize=7.2, color="#334155", zorder=3)

        # Arrow to next
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + box_w + 0.028, y_pos + box_h/2), xytext=(x + box_w + 0.002, y_pos + box_h/2),
                        arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.5), zorder=4)

    # Tensor notation at bottom
    ax.text(0.5, 0.08, "Constructed Tensors: Input X = [Batch=32, SeqLen=32, Features=3 (p, d, s)]  -->  Targets y = [y_p, y_d, y_s]",
            ha="center", va="center", fontsize=8, fontweight="bold", color="#1e40af", transform=ax.transAxes,
            bbox=dict(facecolor="#dbeafe", edgecolor="#93c5fd", boxstyle="round,pad=0.3"))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig4_preprocessing_pipeline.png", dpi=220)
    plt.close(fig)


def fig5_lstm_cell_math():
    """Figure 5: LSTM Cell Gates and Equations."""
    fig, ax = plt.subplots(figsize=(9.5, 3.8), dpi=220)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    ax.text(0.5, 0.96, "LSTM Internal Cell Architecture & Mathematical Gate Formulations",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#0f172a", transform=ax.transAxes)

    # Main cell body
    ax.add_patch(patches.FancyBboxPatch(
        (0.18, 0.12), 0.64, 0.72, boxstyle="round,pad=0.03,rounding_size=0.04",
        facecolor="#ffffff", edgecolor="#3b82f6", linewidth=1.8, zorder=2
    ))
    ax.text(0.5, 0.81, "LSTM Cell at Time Step t", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1e3a8a", zorder=3)

    # Inputs and Outputs lines
    # C_{t-1} in
    ax.annotate("", xy=(0.18, 0.68), xytext=(0.04, 0.68), arrowprops=dict(arrowstyle="->", color="#d97706", lw=2))
    ax.text(0.09, 0.72, "Cell State\n$C_{t-1}$", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#b45309")

    # h_{t-1} and x_t in
    ax.annotate("", xy=(0.18, 0.28), xytext=(0.04, 0.28), arrowprops=dict(arrowstyle="->", color="#2563eb", lw=2))
    ax.text(0.09, 0.32, "Hidden\n$h_{t-1}$", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#1d4ed8")

    ax.annotate("", xy=(0.32, 0.12), xytext=(0.32, 0.02), arrowprops=dict(arrowstyle="->", color="#059669", lw=2))
    ax.text(0.32, 0.00, "Input Vector $x_t$\n(Dim=128)", ha="center", va="top", fontsize=8, fontweight="bold", color="#047857")

    # Gate Boxes inside Cell
    # Forget Gate
    ax.add_patch(patches.Rectangle((0.24, 0.40), 0.10, 0.16, facecolor="#fee2e2", edgecolor="#ef4444", lw=1.2, zorder=3))
    ax.text(0.29, 0.48, "Forget\nGate $\sigma$\n$f_t$", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#991b1b", zorder=4)

    # Input Gate
    ax.add_patch(patches.Rectangle((0.38, 0.40), 0.10, 0.16, facecolor="#e0e7ff", edgecolor="#6366f1", lw=1.2, zorder=3))
    ax.text(0.43, 0.48, "Input\nGate $\sigma$\n$i_t$", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#3730a3", zorder=4)

    # Candidate Cell State
    ax.add_patch(patches.Rectangle((0.52, 0.40), 0.10, 0.16, facecolor="#dcfce7", edgecolor="#22c55e", lw=1.2, zorder=3))
    ax.text(0.57, 0.48, "Candidate\n$\\tanh$\n$\\tilde{C}_t$", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#166534", zorder=4)

    # Output Gate
    ax.add_patch(patches.Rectangle((0.66, 0.40), 0.10, 0.16, facecolor="#fef3c7", edgecolor="#f59e0b", lw=1.2, zorder=3))
    ax.text(0.71, 0.48, "Output\nGate $\sigma$\n$o_t$", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#92400e", zorder=4)

    # Operation Circles
    # multiply forget
    ax.add_patch(patches.Circle((0.29, 0.68), 0.024, facecolor="#fca5a5", edgecolor="#dc2626", zorder=4))
    ax.text(0.29, 0.68, "$\\times$", ha="center", va="center", fontsize=9, fontweight="bold", color="#7f1d1d", zorder=5)

    # multiply input * candidate
    ax.add_patch(patches.Circle((0.50, 0.58), 0.024, facecolor="#bbf7d0", edgecolor="#16a34a", zorder=4))
    ax.text(0.50, 0.58, "$\\times$", ha="center", va="center", fontsize=9, fontweight="bold", color="#14532d", zorder=5)

    # add to cell state
    ax.add_patch(patches.Circle((0.50, 0.68), 0.024, facecolor="#fed7aa", edgecolor="#ea580c", zorder=4))
    ax.text(0.50, 0.68, "$+$", ha="center", va="center", fontsize=10, fontweight="bold", color="#7c2d12", zorder=5)

    # Outputs
    # C_t out
    ax.annotate("", xy=(0.96, 0.68), xytext=(0.82, 0.68), arrowprops=dict(arrowstyle="->", color="#d97706", lw=2))
    ax.text(0.91, 0.72, "Cell State\n$C_t$", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#b45309")

    # h_t out
    ax.annotate("", xy=(0.96, 0.28), xytext=(0.82, 0.28), arrowprops=dict(arrowstyle="->", color="#2563eb", lw=2))
    ax.text(0.91, 0.32, "Hidden\n$h_t$", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#1d4ed8")

    # Math equations panel on right/bottom
    ax.text(0.5, 0.17, "Governing Equations: $f_t = \\sigma(W_f [h_{t-1}, x_t] + b_f)$ | $i_t = \\sigma(W_i [h_{t-1}, x_t] + b_i)$ | $\\tilde{C}_t = \\tanh(W_c [h_{t-1}, x_t] + b_c)$\n$C_t = f_t \\odot C_{t-1} + i_t \\odot \\tilde{C}_t$ | $o_t = \\sigma(W_o [h_{t-1}, x_t] + b_o)$ | $h_t = o_t \\odot \\tanh(C_t)$",
            ha="center", va="center", fontsize=7.5, color="#1e293b", bbox=dict(facecolor="#f1f5f9", edgecolor="#cbd5e1", boxstyle="round,pad=0.3"))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig5_lstm_cell_math.png", dpi=220)
    plt.close(fig)


def fig6_model_architecture():
    """Figure 6: MelodyLSTM PyTorch Architecture & Multi-Task Heads."""
    fig, ax = plt.subplots(figsize=(9.5, 3.6), dpi=220)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    ax.text(0.5, 0.95, "MelodyLSTM Multi-Task Neural Network Architecture (model.py)",
            ha="center", va="top", fontsize=11, fontweight="bold", color="#0f172a", transform=ax.transAxes)

    # 1. Inputs
    ax.add_patch(patches.Rectangle((0.03, 0.58), 0.14, 0.25, facecolor="#f1f5f9", edgecolor="#64748b", lw=1.2))
    ax.text(0.10, 0.70, "Input Indices\n[B, 32, 3]\n(p, d, s)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#1e293b")

    # 2. Embedding Layers
    ax.add_patch(patches.Rectangle((0.21, 0.72), 0.15, 0.16, facecolor="#dbeafe", edgecolor="#2563eb", lw=1.2))
    ax.text(0.285, 0.80, "Pitch Embed\n128 -> 64", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#1e40af")

    ax.add_patch(patches.Rectangle((0.21, 0.52), 0.15, 0.16, facecolor="#dbeafe", edgecolor="#2563eb", lw=1.2))
    ax.text(0.285, 0.60, "Duration Embed\n32 -> 32", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#1e40af")

    ax.add_patch(patches.Rectangle((0.21, 0.32), 0.15, 0.16, facecolor="#dbeafe", edgecolor="#2563eb", lw=1.2))
    ax.text(0.285, 0.40, "Step Embed\n32 -> 32", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#1e40af")

    # Concatenate
    ax.add_patch(patches.Rectangle((0.40, 0.42), 0.08, 0.36, facecolor="#e0e7ff", edgecolor="#4f46e5", lw=1.2))
    ax.text(0.44, 0.60, "Concat\nDim=128\n[B,32,128]", ha="center", va="center", fontsize=7, fontweight="bold", color="#3730a3")

    # LSTM
    ax.add_patch(patches.FancyBboxPatch((0.52, 0.38), 0.15, 0.44, boxstyle="round,pad=0.02", facecolor="#fae8ff", edgecolor="#c026d3", lw=1.5))
    ax.text(0.595, 0.62, "PyTorch LSTM\nLayer\nInput: 128\nHidden: 128\nLayers: 1", ha="center", va="center", fontsize=8, fontweight="bold", color="#86198f")
    ax.text(0.595, 0.43, "Dropout (p=0.1)", ha="center", va="center", fontsize=7, color="#a21caf")

    # Multi-Task Prediction Heads
    ax.add_patch(patches.Rectangle((0.74, 0.72), 0.22, 0.16, facecolor="#ecfdf5", edgecolor="#059669", lw=1.2))
    ax.text(0.85, 0.80, "head_pitch (Linear)\n128 -> 128 logits\nLoss: CrossEntropy(P)", ha="center", va="center", fontsize=7, fontweight="bold", color="#065f46")

    ax.add_patch(patches.Rectangle((0.74, 0.52), 0.22, 0.16, facecolor="#ecfdf5", edgecolor="#059669", lw=1.2))
    ax.text(0.85, 0.60, "head_duration (Linear)\n128 -> 32 logits\nLoss: CrossEntropy(D)", ha="center", va="center", fontsize=7, fontweight="bold", color="#065f46")

    ax.add_patch(patches.Rectangle((0.74, 0.32), 0.22, 0.16, facecolor="#ecfdf5", edgecolor="#059669", lw=1.2))
    ax.text(0.85, 0.40, "head_step (Linear)\n128 -> 32 logits\nLoss: CrossEntropy(S)", ha="center", va="center", fontsize=7, fontweight="bold", color="#065f46")

    # Arrows
    ax.annotate("", xy=(0.21, 0.80), xytext=(0.17, 0.72), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.annotate("", xy=(0.21, 0.60), xytext=(0.17, 0.68), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.annotate("", xy=(0.21, 0.40), xytext=(0.17, 0.64), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))

    ax.annotate("", xy=(0.40, 0.70), xytext=(0.36, 0.80), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.annotate("", xy=(0.40, 0.60), xytext=(0.36, 0.60), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.annotate("", xy=(0.40, 0.50), xytext=(0.36, 0.40), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))

    ax.annotate("", xy=(0.52, 0.60), xytext=(0.48, 0.60), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))

    ax.annotate("", xy=(0.74, 0.80), xytext=(0.67, 0.65), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.annotate("", xy=(0.74, 0.60), xytext=(0.67, 0.60), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.annotate("", xy=(0.74, 0.40), xytext=(0.67, 0.55), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))

    # Parameter count badge
    ax.text(0.5, 0.12, "Total Trainable Parameters = 167,104  |  Total Multi-Task Loss = L_pitch + L_duration + L_step",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1e40af", transform=ax.transAxes,
            bbox=dict(facecolor="#dbeafe", edgecolor="#bfdbfe", boxstyle="round,pad=0.35"))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig6_model_architecture.png", dpi=220)
    plt.close(fig)


def fig7_training_loss():
    """Figure 7: Actual Training & Validation Loss curves from training.log."""
    fig, ax = plt.subplots(figsize=(8.5, 3.2), dpi=220)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    # Real data from training.log
    epochs = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    train_loss = [7.2235, 6.7738, 6.5335, 6.3327, 6.1585, 5.9967, 5.8535, 5.7044, 5.3184]
    val_loss = [6.5465, 6.4248, 6.3122, 6.1791, 6.2725, 6.2547, 6.2663, 6.3011, 6.2623]
    val_p = [4.068, 3.983, 3.888, 3.759, 3.812, 3.812, 3.812, 3.824, 3.766]
    val_d = [0.975, 0.962, 0.968, 0.965, 0.977, 0.972, 0.973, 0.988, 0.990]
    val_s = [1.503, 1.480, 1.456, 1.455, 1.484, 1.471, 1.482, 1.488, 1.507]

    ax.plot(epochs, train_loss, "o-", color="#2563eb", linewidth=2.0, markersize=5, label="Train Loss (Multi-Task Total)")
    ax.plot(epochs, val_loss, "s-", color="#d97706", linewidth=2.0, markersize=5, label="Val Loss (Held-out MAESTRO)")
    ax.plot(epochs, val_p, "^--", color="#059669", linewidth=1.2, markersize=4, label="Val Pitch Loss ($L_{pitch}$)")
    ax.plot(epochs, val_s, "v:", color="#7c3aed", linewidth=1.2, markersize=4, label="Val Step Loss ($L_{step}$)")
    ax.plot(epochs, val_d, "x:", color="#db2777", linewidth=1.2, markersize=4, label="Val Duration Loss ($L_{dur}$)")

    # Highlight best epoch (Epoch 4)
    ax.plot(4, 6.1791, "o", color="#dc2626", markersize=9, zorder=5)
    ax.annotate("Best Model (Epoch 4)\nVal Loss: 6.1791\nSaved -> best_model.pt",
                xy=(4, 6.1791), xytext=(4.3, 6.75),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.5),
                fontsize=7.5, fontweight="bold", color="#b91c1c",
                bbox=dict(facecolor="#fee2e2", edgecolor="#fca5a5", boxstyle="round,pad=0.3"))

    # Early stopping marker
    ax.axvline(9, color="#94a3b8", linestyle="--", linewidth=1.2)
    ax.text(8.8, 7.3, "Early Stopping\n(5 Epochs Patience)", ha="right", va="top", fontsize=7, color="#64748b", fontweight="bold")

    ax.set_title("MelodyLoop Training Dynamics (from artifacts/logs/training.log)", fontsize=10, fontweight="bold", color="#0f172a", pad=8)
    ax.set_xlabel("Epoch Number", fontsize=8.5, color="#334155")
    ax.set_ylabel("Cross-Entropy Loss", fontsize=8.5, color="#334155")
    ax.set_xticks(epochs)
    ax.set_ylim(0.5, 7.8)
    ax.grid(True, linestyle="--", alpha=0.3, color="#94a3b8")
    ax.legend(loc="upper right", fontsize=7.5, facecolor="#ffffff", edgecolor="#cbd5e1")
    ax.tick_params(labelsize=8)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig7_training_loss.png", dpi=220)
    plt.close(fig)


def fig8_autoregressive_generation():
    """Figure 8: Autoregressive Sampling & Top-K Filtering."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.2), dpi=220)
    fig.patch.set_facecolor("#ffffff")

    # Left: Autoregressive Rollout Loop
    ax1.set_facecolor("#f8fafc")
    ax1.set_title("1. Autoregressive Rolling Context Loop", fontsize=9.5, fontweight="bold", color="#0f172a")

    steps = [
        "Initial Seed Buffer (32 notes)",
        "MelodyLSTM Forward Pass",
        "Sample Next Event (p, d, s)",
        "Slide Window: Pop oldest, push new",
        "Repeat N times -> Export MIDI"
    ]
    for i, s in enumerate(steps):
        y = 0.82 - i * 0.17
        fc = "#dbeafe" if i in (0, 3) else "#ecfdf5" if i == 2 else "#fae8ff" if i == 1 else "#fef3c7"
        ec = "#2563eb" if i in (0, 3) else "#059669" if i == 2 else "#c026d3" if i == 1 else "#d97706"
        ax1.add_patch(patches.FancyBboxPatch((0.08, y), 0.84, 0.12, boxstyle="round,pad=0.02", facecolor=fc, edgecolor=ec, lw=1.2))
        ax1.text(0.5, y + 0.06, s, ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0f172a")
        if i < len(steps) - 1:
            ax1.annotate("", xy=(0.5, y - 0.01), xytext=(0.5, y + 0.01), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))

    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis("off")

    # Right: Temperature & Top-K Effect
    ax2.set_facecolor("#f8fafc")
    ax2.set_title("2. Top-K Candidate Filtering & Softmax", fontsize=9.5, fontweight="bold", color="#0f172a")

    candidates = ["C4 (60)", "E4 (64)", "G4 (67)", "D4 (62)", "A4 (69)", "F4 (65)", "B4 (71)", "C#4 (61)"]
    raw_probs = [0.40, 0.25, 0.18, 0.08, 0.04, 0.03, 0.015, 0.005]
    colors = ["#2563eb", "#2563eb", "#2563eb", "#2563eb", "#2563eb", "#94a3b8", "#94a3b8", "#94a3b8"]

    bars = ax2.bar(candidates, raw_probs, color=colors, edgecolor="#0f172a", width=0.6, zorder=3)
    ax2.axvline(4.5, color="#ef4444", linestyle="--", linewidth=1.5, zorder=4)
    ax2.text(2.2, 0.35, "Top-K = 5 Candidates\n(Kept & Renormalized)", ha="center", va="center", fontsize=7.5, color="#1e40af", fontweight="bold",
             bbox=dict(facecolor="#dbeafe", edgecolor="#93c5fd", boxstyle="round,pad=0.2"))
    ax2.text(6.0, 0.28, "Tail Pruned\n(-inf logits)", ha="center", va="center", fontsize=7.5, color="#991b1b", fontweight="bold",
             bbox=dict(facecolor="#fee2e2", edgecolor="#fca5a5", boxstyle="round,pad=0.2"))

    ax2.set_ylabel("Probability $P(y)$", fontsize=8, color="#334155")
    ax2.tick_params(axis="x", rotation=35, labelsize=7)
    ax2.tick_params(axis="y", labelsize=7.5)
    ax2.grid(True, linestyle="--", alpha=0.3, color="#94a3b8", axis="y")
    ax2.set_ylim(0, 0.45)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig8_autoregressive_generation.png", dpi=220)
    plt.close(fig)


def fig9_audio_synthesis():
    """Figure 9: Additive Synthesis & ADSR Envelope Mechanics."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.2), dpi=220)
    fig.patch.set_facecolor("#ffffff")

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
    ax1.set_facecolor("#f8fafc")
    ax1.set_title("1. Additive Harmonics ($f_0 = 261.63$ Hz)", fontsize=9.5, fontweight="bold", color="#0f172a")
    ax1.plot(t[:200]*1000, f1[:200], label="Fundamental (60%)", color="#2563eb", lw=1.2)
    ax1.plot(t[:200]*1000, f2[:200], label="2nd Harmonic (25%)", color="#059669", lw=1.0, linestyle="--")
    ax1.plot(t[:200]*1000, f3[:200], label="3rd Harmonic (15%)", color="#d97706", lw=1.0, linestyle=":")
    ax1.plot(t[:200]*1000, combined[:200], label="Combined Wave", color="#0f172a", lw=1.6)
    ax1.set_xlabel("Time (milliseconds)", fontsize=8, color="#334155")
    ax1.set_ylabel("Amplitude", fontsize=8, color="#334155")
    ax1.grid(True, linestyle="--", alpha=0.3, color="#94a3b8")
    ax1.legend(loc="upper right", fontsize=6.5, facecolor="#ffffff", edgecolor="#cbd5e1")
    ax1.tick_params(labelsize=7.5)

    # Right: ADSR Envelope
    ax2.set_facecolor("#f8fafc")
    ax2.set_title("2. ADSR Decay Envelope & Resulting Audio", fontsize=9.5, fontweight="bold", color="#0f172a")

    envelope = np.exp(-3.0 * t / dur)
    attack_len = int(0.005 * sr)
    envelope[:attack_len] *= np.linspace(0.0, 1.0, attack_len)
    release_len = int(0.01 * sr)
    envelope[-release_len:] *= np.linspace(1.0, 0.0, release_len)

    audio = combined * envelope
    ax2.plot(t, envelope, color="#dc2626", linewidth=1.5, linestyle="--", label="Decay Envelope", zorder=4)
    ax2.plot(t, audio, color="#2563eb", linewidth=0.6, alpha=0.75, label="Synthesized Waveform", zorder=3)
    ax2.set_xlabel("Time (seconds)", fontsize=8, color="#334155")
    ax2.set_ylabel("Normalized Amplitude", fontsize=8, color="#334155")
    ax2.grid(True, linestyle="--", alpha=0.3, color="#94a3b8")
    ax2.legend(loc="upper right", fontsize=6.5, facecolor="#ffffff", edgecolor="#cbd5e1")
    ax2.tick_params(labelsize=7.5)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig9_audio_synthesis.png", dpi=220)
    plt.close(fig)


def fig10_end_to_end_flowchart():
    """Figure 10: Complete End-to-End Architectural Pipeline Flowchart."""
    fig, ax = plt.subplots(figsize=(9.8, 5.6), dpi=220)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    ax.text(0.5, 0.97, "MelodyLoop Complete End-to-End System Pipeline",
            ha="center", va="top", fontsize=11.5, fontweight="bold", color="#0f172a", transform=ax.transAxes)

    # Phase Columns / Containers
    col_w = 0.28
    col_h = 0.82
    y_col = 0.05

    # 1. Training Phase Container
    ax.add_patch(patches.FancyBboxPatch((0.03, y_col), col_w, col_h, boxstyle="round,pad=0.02", facecolor="#eff6ff", edgecolor="#93c5fd", lw=1.5))
    ax.text(0.03 + col_w/2, y_col + col_h - 0.03, "PHASE 1: TRAINING PIPELINE", ha="center", va="top", fontsize=8.0, fontweight="bold", color="#1e40af")

    train_boxes = [
        ("MAESTRO v3.0 Dataset", "1,276 Virtuoso MIDI Files\nCSV Metadata (10 years)"),
        ("Data Preprocessor (data.py)", "mido parse -> (p, d, s)\nQuantize 32 duration/step bins"),
        ("Sequence Generator", "Sliding Window: 32 notes\nX: [B, 32, 3], y: [B, 3]"),
        ("MelodyLSTM Model (train.py)", "PyTorch LSTM (167k params)\nAdam (lr=1e-3, CE Loss)"),
        ("Saved Checkpoint (.pt)", "best_model.pt (Val Loss: 6.1791)\nWeights + Config + Optimizer")
    ]
    for j, (tb, tc) in enumerate(train_boxes):
        by = y_col + col_h - 0.11 - j * 0.138
        ax.add_patch(patches.Rectangle((0.05, by), col_w - 0.04, 0.095, facecolor="#ffffff", edgecolor="#2563eb", lw=1.0))
        ax.text(0.05 + (col_w - 0.04)/2, by + 0.062, tb, ha="center", va="center", fontsize=7.0, fontweight="bold", color="#1e293b")
        ax.text(0.05 + (col_w - 0.04)/2, by + 0.025, tc, ha="center", va="center", fontsize=6.0, color="#475569")
        if j < len(train_boxes) - 1:
            ax.annotate("", xy=(0.05 + (col_w - 0.04)/2, by - 0.005), xytext=(0.05 + (col_w - 0.04)/2, by + 0.005),
                        arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.2))

    # Arrow from Train to Inference
    ax.annotate("", xy=(0.36, 0.48), xytext=(0.31, 0.48), arrowprops=dict(arrowstyle="->", color="#059669", lw=2.2))
    ax.text(0.335, 0.51, "Loads Weights", ha="center", va="bottom", fontsize=6.8, fontweight="bold", color="#065f46")

    # 2. Inference & Generation Container
    ax.add_patch(patches.FancyBboxPatch((0.36, y_col), col_w, col_h, boxstyle="round,pad=0.02", facecolor="#ecfdf5", edgecolor="#a7f3d0", lw=1.5))
    ax.text(0.36 + col_w/2, y_col + col_h - 0.03, "PHASE 2: MUSIC GENERATION", ha="center", va="top", fontsize=8.0, fontweight="bold", color="#065f46")

    gen_boxes = [
        ("Load Checkpoint", "torch.load('best_model.pt')\nReconstructs MelodyLSTM"),
        ("Prompt / Cadence Context", "Classical I-IV-V-I or\nReal MAESTRO seed phrase"),
        ("Autoregressive Sampling", "Temp=0.6, Top-K=5, Repetition\n& interval leap penalty"),
        ("Event Decoding", "Dequantize bin -> seconds\nTimeline assembly"),
        ("Export Standard MIDI (.mid)", "mido track with note_on,\nnote_off & delta ticks")
    ]
    for j, (gb, gc) in enumerate(gen_boxes):
        by = y_col + col_h - 0.11 - j * 0.138
        ax.add_patch(patches.Rectangle((0.38, by), col_w - 0.04, 0.095, facecolor="#ffffff", edgecolor="#059669", lw=1.0))
        ax.text(0.38 + (col_w - 0.04)/2, by + 0.062, gb, ha="center", va="center", fontsize=7.0, fontweight="bold", color="#1e293b")
        ax.text(0.38 + (col_w - 0.04)/2, by + 0.025, gc, ha="center", va="center", fontsize=6.0, color="#475569")
        if j < len(gen_boxes) - 1:
            ax.annotate("", xy=(0.38 + (col_w - 0.04)/2, by - 0.005), xytext=(0.38 + (col_w - 0.04)/2, by + 0.005),
                        arrowprops=dict(arrowstyle="->", color="#059669", lw=1.2))

    # Arrow from Generation to Delivery
    ax.annotate("", xy=(0.69, 0.48), xytext=(0.64, 0.48), arrowprops=dict(arrowstyle="->", color="#d97706", lw=2.2))
    ax.text(0.665, 0.51, "Renders", ha="center", va="bottom", fontsize=6.8, fontweight="bold", color="#b45309")

    # 3. Audio & Application Container
    ax.add_patch(patches.FancyBboxPatch((0.69, y_col), col_w, col_h, boxstyle="round,pad=0.02", facecolor="#fffbeb", edgecolor="#fde68a", lw=1.5))
    ax.text(0.69 + col_w/2, y_col + col_h - 0.03, "PHASE 3: AUDIO & STREAMLIT UI", ha="center", va="top", fontsize=8.0, fontweight="bold", color="#b45309")

    app_boxes = [
        ("Additive Synthesis (audio.py)", "Pure NumPy + SciPy\nf0 + 2f0 + 3f0 + ADSR"),
        ("16-Bit Mono WAV (.wav)", "44.1 kHz PCM standard audio\nImmediate local playback"),
        ("Interactive Streamlit App", "Tab 1: Melody Generator\nTab 2: Human vs LSTM Compare"),
        ("Piano-Roll Visualization", "Matplotlib Pitch vs Time plot\nDistinguishes prompt & gen"),
        ("Direct Downloads & Audition", "Download .mid & .wav\nSide-by-side viva proof")
    ]
    for j, (ab, ac) in enumerate(app_boxes):
        by = y_col + col_h - 0.11 - j * 0.138
        ax.add_patch(patches.Rectangle((0.71, by), col_w - 0.04, 0.095, facecolor="#ffffff", edgecolor="#d97706", lw=1.0))
        ax.text(0.71 + (col_w - 0.04)/2, by + 0.062, ab, ha="center", va="center", fontsize=7.0, fontweight="bold", color="#1e293b")
        ax.text(0.71 + (col_w - 0.04)/2, by + 0.025, ac, ha="center", va="center", fontsize=6.0, color="#475569")
        if j < len(app_boxes) - 1:
            ax.annotate("", xy=(0.71 + (col_w - 0.04)/2, by - 0.005), xytext=(0.71 + (col_w - 0.04)/2, by + 0.005),
                        arrowprops=dict(arrowstyle="->", color="#d97706", lw=1.2))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig10_end_to_end_flowchart.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    print("Generating comprehensive diagram figures...")
    fig1_piano_and_midi()
    fig2_symbolic_vs_audio()
    fig3_dataset_and_splits()
    fig4_preprocessing_pipeline()
    fig5_lstm_cell_math()
    fig6_model_architecture()
    fig7_training_loss()
    fig8_autoregressive_generation()
    fig9_audio_synthesis()
    fig10_end_to_end_flowchart()
    print("All 10 diagram figures generated successfully in artifacts/doc_figures/!")
