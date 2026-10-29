"""
MelodyLoop — Interactive Streamlit Web Application
Demonstrates LSTM next-event music generation, piano-roll visualization,
local audio playback, and side-by-side comparison with the real MAESTRO dataset.
"""

from pathlib import Path
import os
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
from melodyloop.prompt_parser import parse_text_prompt, ParsedPrompt

st.set_page_config(
    page_title="MelodyLoop — LSTM Music Generation",
    page_icon="🎵",
    layout="wide",
)


def load_model_from_checkpoint(ckpt_path: Path, cfg: Config, device: str):
    """Load model checkpoint safely."""
    if not ckpt_path.exists():
        return None, None

    checkpoint = torch.load(str(ckpt_path), map_location=torch.device(device), weights_only=False)
    saved_cfg = checkpoint.get("config", {})
    if "hidden_dim" in saved_cfg:
        cfg.hidden_dim = saved_cfg["hidden_dim"]

    model = MelodyLSTM(cfg)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(torch.device(device))
    model.eval()
    return model, checkpoint


def load_conditional_model_from_checkpoint(ckpt_path: Path, cfg: Config, device: str):
    """Load conditional model checkpoint safely."""
    if not ckpt_path.exists():
        return None, None

    checkpoint = torch.load(str(ckpt_path), map_location=torch.device(device), weights_only=False)
    model = ConditionalMelodyLSTM(
        cfg=cfg,
        velocity_bins=16,
        mood_vocab_size=len(MOOD_VOCAB),
        tempo_vocab_size=len(TEMPO_VOCAB),
        register_vocab_size=len(REGISTER_VOCAB),
        dynamics_vocab_size=len(DYNAMICS_VOCAB),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(torch.device(device))
    model.eval()
    return model, checkpoint


def plot_conditional_piano_roll(notes: list[dict], title: str = "Conditional Piano-Roll (Velocity-Colored)"):
    """Create a piano-roll visualization with notes colored and sized by velocity."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=150)
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#161b22")

    if not notes:
        ax.text(0.5, 0.5, "No notes available", color="#8b949e", ha="center", va="center")
        return fig

    for n in notes:
        start = n["start"]
        dur = max(0.05, n["duration"])
        pitch = n["pitch"]
        vel = n.get("velocity", 80)

        # Color map from soft (cyan/teal) to strong (orange/red)
        norm_vel = min(max(vel / 127.0, 0.2), 1.0)
        if vel <= 65:
            color = "#38bdf8"  # Soft sky blue
            edgecolor = "#0284c7"
        elif vel <= 95:
            color = "#fbbf24"  # Medium amber
            edgecolor = "#d97706"
        else:
            color = "#f87171"  # Strong warm red
            edgecolor = "#dc2626"

        ax.barh(
            y=pitch,
            width=dur,
            left=start,
            height=0.75,
            color=color,
            edgecolor=edgecolor,
            alpha=norm_vel,
        )

    ax.set_title(title, color="#c9d1d9", fontsize=11, pad=10)
    ax.set_xlabel("Time (seconds)", color="#c9d1d9", fontsize=10)
    ax.set_ylabel("MIDI Pitch (0-127)", color="#c9d1d9", fontsize=10)
    ax.tick_params(colors="#8b949e")
    ax.grid(True, linestyle="--", alpha=0.2, color="#8b949e")

    # Draw Register Boundaries
    ax.axhline(58, color="#a855f7", linestyle="--", alpha=0.4, label="Low / Mid Boundary (D4=58)")
    ax.axhline(60, color="#8b949e", linestyle=":", alpha=0.5, label="Middle C (60)")
    ax.axhline(72, color="#ec4899", linestyle="--", alpha=0.4, label="Mid / High Boundary (C5=72)")

    pitches = [n["pitch"] for n in notes]
    min_p = max(0, min(pitches) - 4)
    max_p = min(127, max(pitches) + 4)
    ax.set_ylim(min_p, max_p)

    max_time = max(n["start"] + n["duration"] for n in notes) + 0.5
    ax.set_xlim(0, max_time)
    ax.legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=7)

    plt.tight_layout()
    return fig


def plot_piano_roll(notes: list[dict], title: str = "Piano-Roll Visualization"):
    """Create a piano-roll scatter/bar plot of notes with prompt vs continuation distinction."""
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=150)
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#161b22")

    if not notes:
        ax.text(0.5, 0.5, "No notes available", color="#8b949e", ha="center", va="center")
        return fig

    seed_labeled = False
    gen_labeled = False

    for n in notes:
        start = n["start"]
        dur = max(0.05, n["duration"])
        pitch = n["pitch"]
        is_seed = n.get("is_seed", False)

        if is_seed:
            color = "#f0883e"
            edgecolor = "#d97706"
            label = "Real Prompt Phrase" if not seed_labeled else None
            seed_labeled = True
        else:
            color = "#58a6ff"
            edgecolor = "#1f6feb"
            label = "LSTM Continuation" if not gen_labeled else None
            gen_labeled = True

        ax.barh(
            y=pitch,
            width=dur,
            left=start,
            height=0.8,
            color=color,
            edgecolor=edgecolor,
            alpha=0.88,
            label=label,
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
    ax.axhline(60, color="#8b949e", linestyle=":", alpha=0.4, label="Middle C (60)")
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

    # Discover available checkpoints
    available_ckpts = {}
    expanded_path = cfg.artifacts_dir / "checkpoints" / "best_model_expanded.pt"
    baseline_path = cfg.artifacts_dir / "checkpoints" / "best_model_v1_baseline.pt"
    default_best = cfg.best_model_path

    if expanded_path.exists():
        available_ckpts["Expanded Model (v2: 962 Pieces, 100k Seqs)"] = expanded_path
    if default_best.exists() and default_best not in available_ckpts.values():
        available_ckpts[f"Current Best ({default_best.name})"] = default_best
    if baseline_path.exists():
        available_ckpts["Baseline Model (v1: 13 Pieces, 15k Seqs)"] = baseline_path
    if cfg.latest_model_path.exists() and cfg.latest_model_path not in available_ckpts.values():
        available_ckpts[f"Latest Checkpoint ({cfg.latest_model_path.name})"] = cfg.latest_model_path

    if available_ckpts:
        selected_model_name = st.sidebar.selectbox(
            "Model Checkpoint",
            options=list(available_ckpts.keys()),
            index=0,
            help="Select between the baseline model and the expanded dataset model to hear the difference.",
        )
        ckpt_path = available_ckpts[selected_model_name]
    else:
        ckpt_path = cfg.best_model_path

    model_loaded = False
    model = None
    ckpt_data = None

    if ckpt_path.exists():
        model, ckpt_data = load_model_from_checkpoint(ckpt_path, cfg, device)
        if model is not None:
            model_loaded = True
            st.sidebar.success(f"✓ Checkpoint Active: `{ckpt_path.name}`")
            col_ep, col_loss = st.sidebar.columns(2)
            with col_ep:
                st.metric("Trained Epoch", ckpt_data.get("epoch", "N/A"))
            with col_loss:
                val_loss = ckpt_data.get("val_loss", None)
                if val_loss is not None:
                    st.metric("Val Loss", f"{val_loss:.4f}")
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
    tab_cond, tab_gen, tab_compare = st.tabs([
        "🎛️ Conditional & Prompt Generator (v2.0)",
        "🎼 MAESTRO Baseline Generator",
        "🎹 Human vs LSTM Comparison",
    ])

    # -------------------------------------------------------------
    # TAB 1: Conditional & Prompt Generator (v2.0)
    # -------------------------------------------------------------
    with tab_cond:
        st.subheader("🎛️ Conditional & Prompt-Based Music Generation")
        st.markdown(
            """
            MelodyLoop 2.0 uses a **Condition-Aware LSTM** trained from scratch on the **MidiCaps** dataset.
            The user-selected musical conditions (mood, tempo, pitch register, dynamics) are projected into
            the network's internal recurrent state, directly influencing the next-note prediction distribution.
            """
        )

        cond_ckpt_path = cfg.checkpoints_dir / "conditional" / "best_conditional_model.pt"
        if not cond_ckpt_path.exists():
            cond_ckpt_path = cfg.checkpoints_dir / "conditional" / "latest_conditional_model.pt"

        # Safe Remote Checkpoint Auto-Download for Hosted Cloud Deployments
        if not cond_ckpt_path.exists():
            remote_url = None
            try:
                if hasattr(st, "secrets") and "MELODYLOOP_CONDITIONAL_CKPT_URL" in st.secrets:
                    remote_url = st.secrets["MELODYLOOP_CONDITIONAL_CKPT_URL"]
            except Exception:
                pass
            if not remote_url and "MELODYLOOP_CONDITIONAL_CKPT_URL" in os.environ:
                remote_url = os.environ["MELODYLOOP_CONDITIONAL_CKPT_URL"]

            if remote_url:
                try:
                    with st.spinner("Downloading MelodyLoop 2.0 conditional checkpoint (~2.4 MB)..."):
                        import urllib.request
                        cond_ckpt_path.parent.mkdir(parents=True, exist_ok=True)
                        urllib.request.urlretrieve(remote_url, str(cond_ckpt_path))
                except Exception as dl_err:
                    st.warning(f"Unable to auto-download checkpoint from `{remote_url}`: {dl_err}")

        cond_model = None
        cond_ckpt_data = None
        cond_model_loaded = False

        if cond_ckpt_path.exists():
            cond_model, cond_ckpt_data = load_conditional_model_from_checkpoint(cond_ckpt_path, cfg, device)
            if cond_model is not None:
                cond_model_loaded = True
                ep = cond_ckpt_data.get("epoch", "N/A")
                vl = cond_ckpt_data.get("val_loss", None)
                vl_str = f" | Val Loss: {vl:.4f}" if vl else ""
                st.success(f"✓ Condition-Aware LSTM Loaded: `{cond_ckpt_path.name}` (Epoch {ep}{vl_str})")
        else:
            with st.expander("⚠️ Conditional Model Checkpoint Not Found (Deployment Helper)", expanded=True):
                st.info(
                    "**MelodyLoop 2.0** uses a custom 198k-parameter LSTM (`best_conditional_model.pt`, ~2.4 MB). "
                    "In clean cloud deployments where weights are not tracked in Git, provide the checkpoint using any method below:"
                )
                col_dl1, col_dl2 = st.columns([1, 1])
                with col_dl1:
                    uploaded_pt = st.file_uploader("📥 Upload `best_conditional_model.pt` directly:", type=["pt"], key="up_cond_model")
                    if uploaded_pt is not None:
                        cond_target = cfg.checkpoints_dir / "conditional" / "best_conditional_model.pt"
                        cond_target.parent.mkdir(parents=True, exist_ok=True)
                        with open(cond_target, "wb") as f:
                            f.write(uploaded_pt.getbuffer())
                        st.success("✓ Checkpoint uploaded successfully! Reloading...")
                        st.rerun()
                with col_dl2:
                    custom_url = st.text_input(
                        "🌐 Or enter public download URL:",
                        placeholder="https://.../best_conditional_model.pt",
                        key="input_ckpt_url",
                    )
                    if st.button("⬇️ Download Checkpoint", key="btn_manual_dl") and custom_url.strip():
                        with st.spinner("Downloading checkpoint (~2.4 MB)..."):
                            try:
                                import urllib.request
                                cond_target = cfg.checkpoints_dir / "conditional" / "best_conditional_model.pt"
                                cond_target.parent.mkdir(parents=True, exist_ok=True)
                                urllib.request.urlretrieve(custom_url.strip(), str(cond_target))
                                st.success("✓ Checkpoint downloaded successfully! Reloading...")
                                st.rerun()
                            except Exception as dl_err:
                                st.error(f"Download failed: {dl_err}")
                st.caption("💡 Local development: run `python train_conditional.py` to train from scratch.")

        input_mode = st.radio(
            "Specification Method:",
            options=["💬 Mode B — Natural Language Prompt", "🎛️ Mode A — Manual Musical Controls"],
            horizontal=True,
            help="Mode B translates free text into verified musical attributes. Mode A lets you select specific mood, speed, register, and dynamic parameters directly.",
        )

        # State storage for prompt parsing
        parsed = None
        default_prompt = "Generate a calm, slow piano melody with soft dynamics in a low register."

        if input_mode.startswith("💬"):
            user_prompt = st.text_area(
                "Enter your music description prompt:",
                value=default_prompt,
                height=70,
                help="Type natural language descriptions such as 'Fast energetic piano with high register and forte dynamics'.",
            )
            parsed = parse_text_prompt(user_prompt)

            # Prompt Interpretation Preview
            with st.container():
                st.markdown("**🔍 Prompt Interpretation & Extracted Conditions:**")
                ic1, ic2, ic3, ic4 = st.columns(4)
                with ic1:
                    st.metric("Mood", parsed.mood.title())
                with ic2:
                    st.metric("Speed / Tempo", parsed.tempo.title())
                with ic3:
                    st.metric("Pitch Register", parsed.pitch_register.title())
                with ic4:
                    st.metric("Dynamics", parsed.dynamics.title())

                if parsed.warnings:
                    for w in parsed.warnings:
                        st.caption(f"⚠️ *{w}*")

        with st.expander("🛠️ Manual Overrides & Fine-tuning (Precedence over text prompt)", expanded=(input_mode.startswith("🎛️"))):
            oc1, oc2, oc3, oc4 = st.columns(4)
            mood_opts = ["Prompt / Any", "Calm", "Happy", "Sad", "Energetic", "Dramatic", "Romantic"]
            tempo_opts = ["Prompt / Any", "Slow (< 90 BPM)", "Moderate (90-130 BPM)", "Fast (> 130 BPM)"]
            reg_opts = ["Prompt / Any", "Low (<= 58)", "Middle (59-71)", "High (>= 72)"]
            dyn_opts = ["Prompt / Any", "Soft (<= 65)", "Medium (66-95)", "Strong (>= 96)"]

            with oc1:
                override_mood = st.selectbox("Mood Target", options=mood_opts, index=0)
            with oc2:
                override_tempo = st.selectbox("Speed / Tempo Target", options=tempo_opts, index=0)
            with oc3:
                override_reg = st.selectbox("Pitch Register Target", options=reg_opts, index=0)
            with oc4:
                override_dyn = st.selectbox("Dynamics Intensity", options=dyn_opts, index=0)

        # Resolve Final Effective Conditions
        def resolve_cond(override_val: str, parsed_val: Optional[str]) -> str:
            if override_val != "Prompt / Any":
                return override_val.split()[0].lower()
            if parsed_val and parsed_val != "any":
                return parsed_val
            return "any"

        final_m = resolve_cond(override_mood, parsed.mood if parsed else "any")
        final_t = resolve_cond(override_tempo, parsed.tempo if parsed else "any")
        final_r = resolve_cond(override_reg, parsed.pitch_register if parsed else "any")
        final_d = resolve_cond(override_dyn, parsed.dynamics if parsed else "any")

        # Playback BPM mapping
        if final_t == "slow":
            playback_bpm = 75
        elif final_t == "fast":
            playback_bpm = 145
        else:
            playback_bpm = 115

        st.caption(
            f"🎯 **Active Target Conditions for Model:** Mood: `{final_m.upper()}` | "
            f"Tempo: `{final_t.upper()}` ({playback_bpm} BPM) | "
            f"Register: `{final_r.upper()}` | Dynamics: `{final_d.upper()}`"
        )

        # Hyperparameters
        gc1, gc2, gc3, gc4 = st.columns(4)
        with gc1:
            cond_length = st.slider("Notes to Generate", min_value=20, max_value=150, value=70, step=10, key="cond_len")
        with gc2:
            cond_temp = st.slider("Sampling Temperature", min_value=0.1, max_value=1.4, value=0.80, step=0.05, key="cond_temp")
        with gc3:
            cond_topk = st.slider("Top-K Sampling (0 = off)", min_value=0, max_value=20, value=0, step=1, key="cond_topk")
        with gc4:
            cond_seed = st.number_input("Random Seed", min_value=0, max_value=99999, value=42, step=1, key="cond_seed")

        # Session state for conditional generation
        if "cond_notes" not in st.session_state:
            st.session_state.cond_notes = None
            st.session_state.cond_midi_bytes = None
            st.session_state.cond_wav_bytes = None
            st.session_state.cond_meta = None

        cond_gen_clicked = st.button("✨ Generate Conditional Melody", type="primary", disabled=not cond_model_loaded, key="btn_cond_gen")
        if not cond_model_loaded:
            st.caption("ℹ️ *Generation is disabled until `best_conditional_model.pt` is loaded, uploaded, or downloaded above.*")

        if cond_gen_clicked and cond_model_loaded:
            with st.spinner("Conditioning LSTM and generating musical events..."):
                t0 = time.time()
                cond_notes = generate_conditional_melody(
                    model=cond_model,
                    cfg=cfg,
                    condition={
                        "mood": final_m,
                        "tempo": final_t,
                        "pitch_register": final_r,
                        "dynamics": final_d,
                    },
                    length=cond_length,
                    temperature=cond_temp,
                    top_k=cond_topk,
                    seed=cond_seed,
                    device=torch.device(device),
                )
                gen_elapsed = time.time() - t0

                # Export to temp MIDI and WAV
                import tempfile
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_midi = Path(tmp_dir) / "conditional.mid"
                    tmp_wav = Path(tmp_dir) / "conditional.wav"

                    export_conditional_notes_to_midi(cond_notes, tmp_midi, tempo_bpm=playback_bpm)
                    synthesize_conditional_audio(cond_notes, tmp_wav)

                    with open(tmp_midi, "rb") as f:
                        midi_bytes = f.read()
                    with open(tmp_wav, "rb") as f:
                        wav_bytes = f.read()

                st.session_state.cond_notes = cond_notes
                st.session_state.cond_midi_bytes = midi_bytes
                st.session_state.cond_wav_bytes = wav_bytes
                st.session_state.cond_meta = {
                    "conditions": {"mood": final_m, "tempo": final_t, "register": final_r, "dynamics": final_d},
                    "bpm": playback_bpm,
                    "elapsed": gen_elapsed,
                    "seed": cond_seed,
                    "temperature": cond_temp,
                }

        # Display conditional results if present
        if st.session_state.cond_notes is not None:
            cnotes = st.session_state.cond_notes
            cmeta = st.session_state.cond_meta

            st.markdown("---")
            st.subheader("🎹 Generated Conditional Piece")

            # Piano Roll Plot
            fig_cond = plot_conditional_piano_roll(cnotes, title=f"MelodyLoop 2.0 — {cmeta['conditions']['mood'].title()} | {cmeta['conditions']['register'].title()} Register | {cmeta['conditions']['dynamics'].title()} Dynamics")
            st.pyplot(fig_cond)

            # Audio Player & Downloads
            ac1, ac2, ac3 = st.columns([2, 1, 1])
            with ac1:
                st.write("**🔊 Audio Playback (Velocity-Synthesized Preview):**")
                st.audio(st.session_state.cond_wav_bytes, format="audio/wav")
            with ac2:
                st.write("")
                st.write("")
                st.download_button(
                    label="⬇️ Download MIDI (.mid)",
                    data=st.session_state.cond_midi_bytes,
                    file_name=f"melodyloop_{cmeta['conditions']['mood']}_{cmeta['conditions']['tempo']}.mid",
                    mime="audio/midi",
                    key="dl_cond_mid",
                )
            with ac3:
                st.write("")
                st.write("")
                st.download_button(
                    label="⬇️ Download Audio (.wav)",
                    data=st.session_state.cond_wav_bytes,
                    file_name=f"melodyloop_{cmeta['conditions']['mood']}_{cmeta['conditions']['tempo']}.wav",
                    mime="audio/wav",
                    key="dl_cond_wav",
                )

            # Condition Adherence Verification Card
            pitches = [n["pitch"] for n in cnotes]
            vels = [n["velocity"] for n in cnotes]
            total_dur = cnotes[-1]["start"] + cnotes[-1]["duration"]

            with st.expander("📊 Condition Adherence Metrics for this Piece", expanded=True):
                mc1, mc2, mc3, mc4 = st.columns(4)
                with mc1:
                    st.metric("Total Notes", len(cnotes))
                    st.caption(f"Generation Time: `{cmeta['elapsed']:.2f}s`")
                with mc2:
                    st.metric("Total Duration", f"{total_dur:.1f} s")
                    st.caption(f"Note Density: `{len(cnotes)/max(total_dur, 0.1):.1f} notes/s`")
                with mc3:
                    med_p = int(np.median(pitches))
                    reg_label = "Low" if med_p <= 58 else ("Middle" if med_p <= 71 else "High")
                    st.metric("Median Pitch", f"{med_p} ({reg_label})")
                    st.caption(f"Range: MIDI {min(pitches)} – {max(pitches)}")
                with mc4:
                    mean_v = int(np.mean(vels))
                    dyn_label = "Soft" if mean_v <= 65 else ("Medium" if mean_v <= 95 else "Strong")
                    st.metric("Mean Velocity", f"{mean_v} ({dyn_label})")
                    st.caption(f"Velocity Range: {min(vels)} – {max(vels)}")

    # -------------------------------------------------------------
    # TAB 2: MAESTRO Baseline Generator
    # -------------------------------------------------------------
    with tab_gen:
        st.subheader("🎼 MAESTRO Baseline Melody Generator")

        mode = st.radio(
            "Generation Mode:",
            options=["🎼 Free Melody Generation", "🎹 Continue a Real Piano Phrase (Seeded Continuation)"],
            horizontal=True,
            help="Free generation starts from a classical chord cadence. Seeded continuation prompts the LSTM with a real phrase from MAESTRO and lets it predict the musical continuation.",
        )

        catalog = load_maestro_catalog(str(cfg.data_dir), cfg.csv_filename)
        seed_prompt_notes = None

        if mode == "🎹 Continue a Real Piano Phrase (Seeded Continuation)":
            st.info("💡 **Seeded Continuation Mode:** The LSTM receives the opening bars of a real classical performance as prompt context and predicts the subsequent notes.")
            p_col1, p_col2 = st.columns([2, 1])
            with p_col1:
                prompt_length = st.slider("Prompt Phrase Length (notes to provide as context)", min_value=12, max_value=32, value=20, step=4)
            with p_col2:
                st.write("")
                st.write("")
                pick_prompt_clicked = st.button("🎲 Pick Random Prompt Phrase", key="btn_pick_prompt")

            if "continuation_prompt" not in st.session_state:
                st.session_state.continuation_prompt = None

            if (pick_prompt_clicked or st.session_state.continuation_prompt is None) and catalog:
                chosen_p = random.choice(catalog)
                midi_p = Path(chosen_p["path"])
                raw_n = extract_clip_from_midi(midi_p, cfg, notes_count=prompt_length)
                st.session_state.continuation_prompt = {
                    "composer": chosen_p["composer"],
                    "title": chosen_p["title"],
                    "notes": raw_n,
                }

            if st.session_state.continuation_prompt:
                cp = st.session_state.continuation_prompt
                st.caption(f"🎼 **Active Prompt Phrase:** {cp['composer']} — *{cp['title']}* ({len(cp['notes'])} notes)")
                seed_prompt_notes = cp["notes"][:prompt_length]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            length = st.slider("Notes to Generate", min_value=20, max_value=150, value=60, step=10)
        with col2:
            temperature = st.slider(
                "Sampling Temperature",
                min_value=0.1,
                max_value=1.3,
                value=0.60,
                step=0.05,
                help="Controls diversity. 0.55–0.65 produces structured, cohesive melodic flow. Higher values (>0.9) increase randomness.",
            )
        with col3:
            top_k = st.slider(
                "Top-K Sampling",
                min_value=1,
                max_value=20,
                value=5,
                step=1,
                help="Restricts sampling to the K most probable next notes. Filters out noisy and discordant tail notes.",
            )
        with col4:
            seed = st.number_input("Random Seed", min_value=0, max_value=99999, value=42, step=1)

        btn_label = "✨ Generate Continuation" if mode.startswith("🎹") else "✨ Generate Melody"
        gen_clicked = st.button(btn_label, type="primary", disabled=not model_loaded, key="btn_gen")

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
                    pitch_top_k=top_k,
                    seed=seed,
                    seed_sequence=seed_prompt_notes,
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
            seed_count = sum(1 for n in notes if n.get("is_seed", False))
            continuation_count = len(notes) - seed_count

            # Calculate pitch jump metrics
            jumps = [abs(pitches[i+1] - pitches[i]) for i in range(len(pitches)-1)]
            avg_jump = sum(jumps) / max(1, len(jumps))

            m1, m2, m3, m4 = st.columns(4)
            if seed_count > 0:
                m1.metric("Notes (Prompt + Gen)", f"{seed_count} + {continuation_count}")
            else:
                m1.metric("Notes Generated", len(notes))
            m2.metric("Total Duration", f"{total_time:.1f} s")
            m3.metric("Pitch Range", f"{min(pitches)} - {max(pitches)}")
            m4.metric("Avg Pitch Step", f"{avg_jump:.1f} semitones")

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
