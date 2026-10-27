"""
MelodyLoop — Interactive Streamlit Web Application
Demonstrates LSTM next-event music generation, piano-roll visualization,
and local audio playback for educational presentation.
"""

from pathlib import Path
import time
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import torch

from config import Config
from melodyloop.audio import synthesize_notes_to_wav
from melodyloop.generation import generate_melody, export_notes_to_midi
from melodyloop.model import MelodyLSTM

st.set_page_config(
    page_title="MelodyLoop — LSTM Music Generation",
    page_icon="🎵",
    layout="wide",
)


def load_model_from_checkpoint(ckpt_path: Path, cfg: Config, device: str):
    """Load model checkpoint safely."""
    if not ckpt_path.exists():
        return None, None

    checkpoint = torch.load(str(ckpt_path), map_location=torch.device(device))
    saved_cfg = checkpoint.get("config", {})
    if "hidden_dim" in saved_cfg:
        cfg.hidden_dim = saved_cfg["hidden_dim"]

    model = MelodyLSTM(cfg)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(torch.device(device))
    model.eval()
    return model, checkpoint


def plot_piano_roll(notes: list[dict]):
    """Create a piano-roll scatter/bar plot of generated notes."""
    fig, ax = plt.subplots(figsize=(10, 4), dpi=150)
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#161b22")

    if not notes:
        ax.text(0.5, 0.5, "No notes generated yet", color="#8b949e", ha="center", va="center")
        return fig

    # Draw each note as a horizontal bar
    for n in notes:
        start = n["start"]
        dur = max(0.05, n["duration"])
        pitch = n["pitch"]
        ax.barh(
            y=pitch,
            width=dur,
            left=start,
            height=0.8,
            color="#58a6ff",
            edgecolor="#1f6feb",
            alpha=0.85,
        )

    ax.set_xlabel("Time (seconds)", color="#c9d1d9", fontsize=11)
    ax.set_ylabel("MIDI Pitch (0-127)", color="#c9d1d9", fontsize=11)
    ax.tick_params(colors="#8b949e")
    ax.grid(True, linestyle="--", alpha=0.2, color="#8b949e")

    # Set reasonable pitch bounds around active notes
    pitches = [n["pitch"] for n in notes]
    min_p = max(0, min(pitches) - 3)
    max_p = min(127, max(pitches) + 3)
    ax.set_ylim(min_p, max_p)

    max_time = max(n["start"] + n["duration"] for n in notes) + 0.5
    ax.set_xlim(0, max_time)

    # Note references (Middle C = 60)
    ax.axhline(60, color="#f0883e", linestyle=":", alpha=0.5, label="Middle C (C4 = 60)")
    ax.legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=9)

    plt.tight_layout()
    return fig


def main():
    cfg = Config()

    # Header & educational overview
    st.title("🎵 MelodyLoop: Music Generation Using an LSTM")
    st.markdown(
        """
        **MelodyLoop** is an educational deep learning project demonstrating how a custom 
        **Long Short-Term Memory (LSTM)** neural network learns temporal musical patterns 
        from MAESTRO piano performances and generates new sequential music.
        """
    )

    # Sidebar: Model status and hardware info
    st.sidebar.header("⚙️ System & Model Status")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    st.sidebar.info(f"**Compute Device:** `{device.upper()}`")
    if device == "cuda":
        st.sidebar.caption(f"GPU: {torch.cuda.get_device_name(0)}")

    ckpt_path = cfg.best_model_path if cfg.best_model_path.exists() else cfg.latest_model_path
    model_loaded = False
    model = None
    ckpt_data = None

    if ckpt_path.exists():
        model, ckpt_data = load_model_from_checkpoint(ckpt_path, cfg, device)
        if model is not None:
            model_loaded = True
            st.sidebar.success(f"✓ Checkpoint Active: `{ckpt_path.name}`")
            st.sidebar.metric("Trained Epoch", ckpt_data.get("epoch", "N/A"))
            val_loss = ckpt_data.get("val_loss", None)
            if val_loss is not None:
                st.sidebar.metric("Validation Loss", f"{val_loss:.4f}")
            st.sidebar.caption(f"Parameters: {model.count_parameters():,}")
    else:
        st.sidebar.warning("⚠️ No trained checkpoint found.")
        st.sidebar.caption("Run `python train.py` in the terminal to train the model.")

    # Educational architecture expander
    with st.expander("📖 How the MelodyLoop Pipeline Works", expanded=False):
        st.markdown(
            """
            1. **Sequential Note Event Representation**:
               Each piano note is represented by three discrete tokens:
               - **Pitch** (MIDI 0–127)
               - **Duration** (Quantized into 32 duration bins, 0.05s to 4.0s)
               - **Step / Inter-onset Interval** (Quantized into 32 step bins, 0.0s to 2.0s)
            2. **Embeddings & LSTM Memory**:
               Each discrete token is mapped through dedicated embedding layers, concatenated, and fed into an LSTM cell.
               The recurrent hidden state maintains sequential context across notes (musical phrasing and rhythm).
            3. **Multi-Task Prediction Heads**:
               Linear heads predict the probability distribution for the next note's pitch, duration, and step.
            4. **Autoregressive Generation**:
               Starting from a musical prompt, the LSTM iteratively samples the next note event using temperature-scaled softmax, 
               appends it to the context, and generates the melody step-by-step.
            """
        )

    # Generation controls
    st.subheader("🎼 Melody Generator")
    col1, col2, col3 = st.columns(3)

    with col1:
        length = st.slider("Melody Length (number of notes)", min_value=20, max_value=200, value=80, step=10)
    with col2:
        temperature = st.slider(
            "Sampling Temperature",
            min_value=0.1,
            max_value=1.5,
            value=0.85,
            step=0.05,
            help="Higher = more exploratory/diverse; Lower = more conservative/repetitive.",
        )
    with col3:
        seed = st.number_input("Random Seed", min_value=0, max_value=99999, value=42, step=1)

    gen_clicked = st.button("✨ Generate Melody", type="primary", disabled=not model_loaded)

    if not model_loaded:
        st.info("Train a model or start background training to enable the generator.")

    # State storage for generated music
    if "generated_notes" not in st.session_state:
        st.session_state.generated_notes = None
        st.session_state.midi_bytes = None
        st.session_state.wav_bytes = None

    if gen_clicked and model_loaded:
        with st.spinner("Generating autoregressive note sequence..."):
            notes = generate_melody(
                model=model,
                cfg=cfg,
                num_notes=length,
                temperature=temperature,
                seed=seed,
                device=device,
            )

            # Export to disk and memory
            timestamp = int(time.time())
            midi_path = cfg.generated_dir / f"generated_{timestamp}.mid"
            wav_path = cfg.generated_dir / f"generated_{timestamp}.wav"

            export_notes_to_midi(notes, midi_path, bpm=cfg.tempo_bpm)
            synthesize_notes_to_wav(notes, wav_path)

            st.session_state.generated_notes = notes
            st.session_state.midi_bytes = midi_path.read_bytes()
            st.session_state.wav_bytes = wav_path.read_bytes()
            st.success(f"Generated {len(notes)} notes successfully!")

    # Display results if available
    if st.session_state.generated_notes:
        notes = st.session_state.generated_notes
        total_time = notes[-1]["start"] + notes[-1]["duration"]
        pitches = [n["pitch"] for n in notes]

        # Metric summary row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Notes Generated", len(notes))
        m2.metric("Total Duration", f"{total_time:.1f} s")
        m3.metric("Lowest Pitch", min(pitches))
        m4.metric("Highest Pitch", max(pitches))

        # Audio playback
        st.subheader("🔊 Audio Preview")
        st.caption("Rendered using lightweight local harmonic synthesis.")
        if st.session_state.wav_bytes:
            st.audio(st.session_state.wav_bytes, format="audio/wav")

        # Download buttons
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                label="⬇️ Download Standard MIDI (.mid)",
                data=st.session_state.midi_bytes,
                file_name="melodyloop_generated.mid",
                mime="audio/midi",
            )
        with d2:
            st.download_button(
                label="⬇️ Download Audio (.wav)",
                data=st.session_state.wav_bytes,
                file_name="melodyloop_preview.wav",
                mime="audio/wav",
            )

        # Piano roll plot
        st.subheader("🎹 Piano-Roll Visualization")
        fig = plot_piano_roll(notes)
        st.pyplot(fig)


if __name__ == "__main__":
    main()
