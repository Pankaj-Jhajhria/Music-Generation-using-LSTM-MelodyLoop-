"""
MelodyLoop — Interactive Streamlit Web Application
Demonstrates LSTM next-event music generation, piano-roll visualization,
local audio playback, and side-by-side comparison with the real MAESTRO dataset.
"""

from pathlib import Path
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import torch

from config import Config
from melodyloop.audio import synthesize_notes_to_wav
from melodyloop.data import parse_midi_file, dequantize_duration, dequantize_step
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


def plot_piano_roll(notes: list[dict], title: str = "Piano-Roll Visualization"):
    """Create a piano-roll scatter/bar plot of notes."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=150)
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#161b22")

    if not notes:
        ax.text(0.5, 0.5, "No notes available", color="#8b949e", ha="center", va="center")
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

    ax.set_title(title, color="#c9d1d9", fontsize=11, pad=10)
    ax.set_xlabel("Time (seconds)", color="#c9d1d9", fontsize=10)
    ax.set_ylabel("MIDI Pitch (0-127)", color="#c9d1d9", fontsize=10)
    ax.tick_params(colors="#8b949e")
    ax.grid(True, linestyle="--", alpha=0.2, color="#8b949e")

    # Set pitch bounds
    pitches = [n["pitch"] for n in notes]
    min_p = max(0, min(pitches) - 3)
    max_p = min(127, max(pitches) + 3)
    ax.set_ylim(min_p, max_p)

    max_time = max(n["start"] + n["duration"] for n in notes) + 0.5
    ax.set_xlim(0, max_time)

    # Reference Middle C (60)
    ax.axhline(60, color="#f0883e", linestyle=":", alpha=0.5, label="Middle C (60)")
    ax.legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=8)

    plt.tight_layout()
    return fig


@st.cache_data
def load_maestro_catalog(data_dir_str: str, csv_filename: str):
    """Cache MAESTRO metadata catalog for quick sampling."""
    csv_path = Path(data_dir_str) / csv_filename
    if not csv_path.exists():
        return []
    df = pd.read_csv(csv_path)
    pieces = []
    for _, row in df.iterrows():
        p = Path(data_dir_str) / row["midi_filename"]
        if p.exists():
            pieces.append({
                "composer": row.get("canonical_composer", "Unknown"),
                "title": row.get("canonical_title", "Unknown Piece"),
                "year": str(row.get("year", "N/A")),
                "split": str(row.get("split", "N/A")),
                "midi_filename": row["midi_filename"],
                "path": str(p),
            })
    return pieces


def extract_clip_from_midi(midi_path: Path, cfg: Config, notes_count: int = 80):
    """Extract and dequantize first N notes from a MIDI file into standard note dicts."""
    events = parse_midi_file(midi_path, cfg)
    if not events:
        return []

    notes = []
    current_time = 0.0
    for p_idx, d_idx, s_idx in events[:notes_count]:
        dur = dequantize_duration(d_idx, cfg)
        step = dequantize_step(s_idx, cfg)
        notes.append({
            "pitch": p_idx,
            "start": current_time,
            "duration": dur,
            "step": step,
        })
        current_time += step

    return notes


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

    # Top-level Tabs
    tab_gen, tab_compare = st.tabs(["🎼 LSTM Melody Generator", "🎹 Human vs LSTM Comparison"])

    # -------------------------------------------------------------
    # TAB 1: LSTM Melody Generator
    # -------------------------------------------------------------
    with tab_gen:
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

        gen_clicked = st.button("✨ Generate Melody", type="primary", disabled=not model_loaded, key="btn_gen")

        if not model_loaded:
            st.info("Train a model or check checkpoints to enable the generator.")

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

                timestamp = int(time.time())
                midi_path = cfg.generated_dir / f"generated_{timestamp}.mid"
                wav_path = cfg.generated_dir / f"generated_{timestamp}.wav"

                export_notes_to_midi(notes, midi_path, bpm=cfg.tempo_bpm)
                synthesize_notes_to_wav(notes, wav_path)

                st.session_state.generated_notes = notes
                st.session_state.midi_bytes = midi_path.read_bytes()
                st.session_state.wav_bytes = wav_path.read_bytes()
                st.success(f"Generated {len(notes)} notes successfully!")

        if st.session_state.generated_notes:
            notes = st.session_state.generated_notes
            total_time = notes[-1]["start"] + notes[-1]["duration"]
            pitches = [n["pitch"] for n in notes]

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Notes Generated", len(notes))
            m2.metric("Total Duration", f"{total_time:.1f} s")
            m3.metric("Lowest Pitch", min(pitches))
            m4.metric("Highest Pitch", max(pitches))

            st.subheader("🔊 Audio Preview")
            st.caption("Rendered using lightweight local harmonic synthesis.")
            if st.session_state.wav_bytes:
                st.audio(st.session_state.wav_bytes, format="audio/wav")

            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    label="⬇️ Download Standard MIDI (.mid)",
                    data=st.session_state.midi_bytes,
                    file_name="melodyloop_generated.mid",
                    mime="audio/midi",
                    key="dl_midi_gen",
                )
            with d2:
                st.download_button(
                    label="⬇️ Download Audio (.wav)",
                    data=st.session_state.wav_bytes,
                    file_name="melodyloop_preview.wav",
                    mime="audio/wav",
                    key="dl_wav_gen",
                )

            st.subheader("🎹 Piano-Roll Visualization")
            fig = plot_piano_roll(notes, title="LSTM Generated Melody")
            st.pyplot(fig)

    # -------------------------------------------------------------
    # TAB 2: Compare Human Dataset vs LSTM Generator
    # -------------------------------------------------------------
    with tab_compare:
        st.subheader("🎹 Compare Real Dataset Music vs LSTM Generated Music")
        st.markdown(
            """
            Compare human piano performances from the **MAESTRO dataset** directly against the 
            **LSTM-generated music**. Both are rendered using the identical harmonic synthesis engine 
            for a fair, 1:1 auditory and visual comparison.
            """
        )

        catalog = load_maestro_catalog(str(cfg.data_dir), cfg.csv_filename)

        col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
        with col_c1:
            split_choice = st.selectbox(
                "Filter by Dataset Split:",
                options=["Any Split", "train", "validation", "test"],
                index=0,
            )
        with col_c2:
            comp_notes_count = st.slider("Note Clip Length:", min_value=30, max_value=150, value=80, step=10)
        with col_c3:
            st.write("")
            st.write("")
            pick_random_clicked = st.button("🎲 Pick Random Real Performance", type="primary")

        if "dataset_sample" not in st.session_state:
            st.session_state.dataset_sample = None

        if pick_random_clicked and catalog:
            matching = catalog
            if split_choice != "Any Split":
                matching = [p for p in catalog if p["split"].lower() == split_choice.lower()]

            if not matching:
                st.warning(f"No pieces found for split '{split_choice}'.")
            else:
                chosen = random.choice(matching)
                with st.spinner(f"Extracting & synthesizing excerpt from {chosen['title']}..."):
                    midi_p = Path(chosen["path"])
                    raw_notes = extract_clip_from_midi(midi_p, cfg, notes_count=comp_notes_count)

                    if raw_notes:
                        out_sample_wav = cfg.generated_dir / "app_dataset_sample.wav"
                        synthesize_notes_to_wav(raw_notes, out_sample_wav)

                        st.session_state.dataset_sample = {
                            "composer": chosen["composer"],
                            "title": chosen["title"],
                            "year": chosen["year"],
                            "split": chosen["split"],
                            "notes": raw_notes,
                            "wav_bytes": out_sample_wav.read_bytes(),
                            "midi_bytes": midi_p.read_bytes(),
                            "filename": midi_p.name,
                        }
                        st.success(f"Loaded: {chosen['composer']} — {chosen['title']}")

        # Side-by-side comparison view
        col_human, col_lstm = st.columns(2)

        with col_human:
            st.markdown("### 🎼 1. Real Human Performance (MAESTRO)")
            if st.session_state.dataset_sample:
                ds = st.session_state.dataset_sample
                st.info(f"**Composer:** {ds['composer']}\n\n**Piece:** {ds['title']} ({ds['year']}) | *Split: {ds['split']}*")
                
                pitches_h = [n["pitch"] for n in ds["notes"]]
                dur_h = ds["notes"][-1]["start"] + ds["notes"][-1]["duration"]
                
                m1, m2 = st.columns(2)
                m1.metric("Human Notes", len(ds["notes"]))
                m2.metric("Duration", f"{dur_h:.1f} s")

                st.write("**🔊 Audio Playback (Human Performance Clip):**")
                st.audio(ds["wav_bytes"], format="audio/wav")

                st.download_button(
                    label="⬇️ Download Real Sample WAV",
                    data=ds["wav_bytes"],
                    file_name="maestro_human_sample.wav",
                    mime="audio/wav",
                    key="dl_human_wav",
                )

                fig_h = plot_piano_roll(ds["notes"], title=f"Real Performance: {ds['composer']} - {ds['title'][:25]}")
                st.pyplot(fig_h)
            else:
                st.info("Click **'🎲 Pick Random Real Performance'** above to load a real performance clip from MAESTRO.")

        with col_lstm:
            st.markdown("### 🤖 2. LSTM Generated Composition")
            if st.session_state.generated_notes and st.session_state.wav_bytes:
                notes_gen = st.session_state.generated_notes
                pitches_l = [n["pitch"] for n in notes_gen]
                dur_l = notes_gen[-1]["start"] + notes_gen[-1]["duration"]

                st.success("**Source:** MelodyLSTM Checkpoint (`best_model.pt`)\n\n*Learned next-note prediction from scratch*")

                m1, m2 = st.columns(2)
                m1.metric("LSTM Notes", len(notes_gen))
                m2.metric("Duration", f"{dur_l:.1f} s")

                st.write("**🔊 Audio Playback (LSTM Model Output):**")
                st.audio(st.session_state.wav_bytes, format="audio/wav")

                st.download_button(
                    label="⬇️ Download LSTM Generated WAV",
                    data=st.session_state.wav_bytes,
                    file_name="lstm_generated_sample.wav",
                    mime="audio/wav",
                    key="dl_lstm_wav",
                )

                fig_l = plot_piano_roll(notes_gen, title="LSTM Generated Melody")
                st.pyplot(fig_l)
            else:
                st.info("Generate a melody in Tab 1 first to display it here side-by-side.")

        # Educational takeaway table
        st.markdown("---")
        st.subheader("🔍 Educational Comparison & Discussion")
        st.markdown(
            """
            | Feature | Human Performance (MAESTRO Dataset) | LSTM Generated Output (`MelodyLoop`) |
            |---|---|---|
            | **Pitch Variety & Range** | Spans 5–7 octaves with complex polyphony, arpeggios, and chord progressions. | Stays within a focused melodic register (2–3 octaves), maintaining musical center of gravity. |
            | **Timing & Rhythm** | Natural *rubato* (subtle human tempo fluctuations, expressive dynamic phrasing). | Quantized time steps with clear beat division, learning consistent note groupings. |
            | **Structural Coherence** | Long-range exposition, key changes, and thematic motifs spanning minutes. | Short-term sequential transitions (~15–30 notes), learning authentic note-to-note transitions. |
            """
        )


if __name__ == "__main__":
    main()
