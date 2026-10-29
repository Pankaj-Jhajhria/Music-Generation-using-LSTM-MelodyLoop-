# MelodyLoop: Music Generation Using an LSTM

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA_12.6-EE4C2C.svg)](https://pytorch.org/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/Dataset_License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**MelodyLoop** is a complete, lightweight, locally running educational project that demonstrates how a custom **Long Short-Term Memory (LSTM)** neural network learns sequential musical patterns from classical piano performances and autoregressively generates new melodies.

> **Project Scope**: This project is built specifically for educational demonstration and sequential pattern analysis. The LSTM is trained **completely from scratch** without pretrained generative checkpoints. The training data comes from the MAESTRO piano dataset, so generated outputs are **LSTM-generated piano-note sequences**.

---

## Table of Contents
1. [Pipeline Overview](#pipeline-overview)
2. [What the LSTM Learns](#what-the-lstm-learns)
3. [System & Hardware Detection](#system--hardware-detection)
4. [Dataset & Representation](#dataset--representation)
5. [Model Architecture](#model-architecture)
6. [Quickstart & Commands](#quickstart--commands)
7. [Streamlit Web Interface](#streamlit-web-interface)
8. [60-90 Second Professor Presentation Script](#60-90-second-professor-presentation-script)
9. [Limitations & Common Errors](#limitations--common-errors)

---

## Pipeline Overview

```
[MAESTRO MIDI Performances]
            │
            ▼ (mido parsing & chronological event extraction)
[Note Events: Pitch, Duration, Inter-Onset Step]
            │
            ▼ (Quantization into discrete categorical tokens)
[Sliding Window Sequences: (Batch, 32, 3)]
            │
            ▼ (Embedding Layers -> 128-dim vectors)
[PyTorch LSTM Recurrent Core (128 hidden units)]
            │
            ▼ (Multi-Task Cross-Entropy Loss: Pitch + Duration + Step)
[Trained Checkpoint (best_model.pt)]
            │
            ▼ (Autoregressive Rollout with Temperature Sampling)
[Generated Note Sequence] ───┬───► [Standard MIDI File (.mid)]
                             ├───► [Piano-Roll Visualizer]
                             └───► [Zero-Dependency Audio Preview (.wav)]
```

---

## What the LSTM Learns

Standard Feed-Forward networks treat each input independently. Music, however, is fundamentally **temporal and contextual**:
1. **Pitch Transitions & Phrasing**: The probability of the next pitch depends heavily on the preceding scale, melodic contour, and tonal center.
2. **Rhythmic Structure**: Musical pacing relies on note durations and pauses (inter-onset intervals).
3. **Internal Cell State ($c_t$) & Hidden State ($h_t$)**: The LSTM's gating mechanisms (Forget gate $f_t$, Input gate $i_t$, and Output gate $o_t$) decide what musical memory to retain across bars and what notes to emphasize next.

During generation, the LSTM samples one note event $(p_{t+1}, d_{t+1}, s_{t+1})$ autoregressively, slides the window forward, and repeats.

---

## System & Hardware Detection

The training engine detects and adapts to the local system environment automatically:

| Component | Detected Specification |
|---|---|
| **OS** | Windows 11 (64-bit AMD64) |
| **Python** | 3.13.1 |
| **CPU** | 12 logical cores (8 physical) |
| **RAM** | 15.68 GB total (bounded allocations to safeguard memory) |
| **GPU** | **NVIDIA GeForce RTX 3050 Laptop GPU** (4,095 MB VRAM) |
| **PyTorch Device** | `CUDA` (PyTorch 2.13.0+cu126) |

---

## Dataset & Representation

* **Source**: MAESTRO v3.0.0 (MIDI-only dataset, ~81 MB).
* **Composition**: 1,276 virtuoso piano performances (962 train / 137 validation / 177 test).
* **License**: Creative Commons Attribution Non-Commercial Share-Alike 4.0 International ([CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)).

### Note Event Tokenization
Rather than processing raw bytes, each piano note is tokenized into 3 discrete integers:
- **Pitch**: Standard MIDI pitch 0 to 127 (128 categories).
- **Duration**: Bounded between 0.05s and 4.0s, quantized into **32 discrete bins**.
- **Step (Time-Shift)**: Time until the next note onset (0.0s to 2.0s), quantized into **32 discrete bins** (step = 0 denotes simultaneous chords).

---

## Model Architecture

The model `MelodyLSTM` is implemented in PyTorch (`melodyloop/model.py`):

* **Embedding Layers**:
  - Pitch Embedding: $128 \to 64$
  - Duration Embedding: $32 \to 32$
  - Step Embedding: $32 \to 32$
  - *Combined Input Dimension*: $64 + 32 + 32 = 128$
* **Recurrent Core**: Single-layer `nn.LSTM` with `hidden_dim = 128` (131,584 recurrent parameters).
* **Prediction Heads**:
  - `head_pitch`: `Linear(128, 128)`
  - `head_duration`: `Linear(128, 32)`
  - `head_step`: `Linear(128, 32)`
* **Total Parameters**: **167,104** (lightweight, highly explainable, trains smoothly inside 4 GB VRAM).
* **Loss Function**: Multi-task categorical cross-entropy:
  $$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{pitch}} + \mathcal{L}_{\text{duration}} + \mathcal{L}_{\text{step}}$$

---

## Quickstart & Commands

### MelodyLoop 2.0: Conditional & Prompt-Based Generation (MidiCaps)
```powershell
# 1. Run all unit tests
pytest

# 2. Train Condition-Aware LSTM from scratch on MidiCaps solo piano
python train_conditional.py --epochs 15 --batch_size 64 --max_train_seqs 50000 --max_val_seqs 5000

# 3. Generate music from a natural language text prompt via CLI
python generate_conditional.py --prompt "Generate a calm, slow piano melody with soft dynamics." --length 60 --seed 42

# 4. Evaluate condition adherence (register, dynamics, tempo, mood profiles)
python evaluate_conditional.py

# 5. Launch the interactive Streamlit web dashboard
streamlit run app.py
```

### MelodyLoop 1.0: Baseline MAESTRO Continuation
```powershell
# Train baseline MAESTRO model
python train.py --expanded

# Generate baseline continuation
python generate.py --length 60 --temperature 0.60 --top-k 5 --seed 42
```

---

## MelodyLoop 2.0: Conditional & Prompt-Based Generation

MelodyLoop 2.0 upgrades the system from unconditional generation to a **genuine condition-aware sequence generator** using the [MidiCaps](https://huggingface.co/datasets/amaai-lab/MidiCaps) dataset (CC BY-SA 4.0).

### Key Architectural Upgrades
1. **4-Feature Event Representation**: Notes are represented by 4 discrete tokens: `(Pitch, Duration, Step, Velocity)`. Note velocity is quantized into 16 bins ($0–15 \to 1–127$), giving the model direct control over dynamics.
2. **Condition Attribute Projections**: Four condition attributes are embedded and projected into the LSTM:
   - **Mood (6 categories + any)**: Calm, Happy, Sad, Energetic, Dramatic, Romantic (16-dim embedding).
   - **Speed / Tempo (3 categories + any)**: Slow ($<90$ BPM), Moderate ($90–130$ BPM), Fast ($>130$ BPM) (8-dim embedding).
   - **Pitch Register (3 categories + any)**: Low ($\le 58$), Middle ($59–71$), High ($\ge 72$) (8-dim embedding).
   - **Dynamics (3 categories + any)**: Soft ($\le 65$), Medium ($66–95$), Strong ($\ge 96$) (8-dim embedding).
3. **Total Condition Vector**: 40 dimensions, concatenated with the 144-dim event embeddings for a **184-dim input** to the LSTM (198,304 parameters).
4. **Local Prompt Parser (`melodyloop/prompt_parser.py`)**: Parses natural language text descriptions (e.g. *"Slow, peaceful piano melody with soft dynamics"*) into structured condition indices using rule-based synonym matching and TF-IDF training-set caption retrieval—zero external APIs or cloud LLMs required.
5. **Velocity-Sensitive Audio Synthesis**: Local audio synthesis renders softer harmonic attack for soft dynamics ($p$) and richer overtone content for strong dynamics ($f$).
6. **Dataset & Audit Attribution**: Trained on **15,705 solo piano performances** audited from MidiCaps (AMAAI Lab, SUTD, CC BY-SA 4.0). Full audit: [`docs/MidiCaps_Dataset_Audit.md`](docs/MidiCaps_Dataset_Audit.md). Full report: [`docs/Conditional_Generation_Report.md`](docs/Conditional_Generation_Report.md).

---

## Streamlit Web Interface

The interactive dashboard (`app.py`) provides:
- **Tab 1: LSTM Melody Generator**:
  - **Generation Modes**: Switch between **Free Generation** (starts from classical cadence) and **Continue a Real Piano Phrase** (prompts the LSTM with real Beethoven/Chopin/Mozart bars).
  - **Coherence Controls**: Adjustable **Sampling Temperature** (0.55–0.65 optimal) and **Top-K Candidate Filter** (eliminates chaotic tail jumps).
  - **Dual-Colored Piano-Roll**: Real prompt phrases are highlighted in orange/amber and LSTM continuations in bright blue.
  - **Instant Audio Playback & Downloads**: Play audio previews and download Standard MIDI (`.mid`) or WAV files.
- **Tab 2: Human vs LSTM Comparison**:
  - Randomly selects pieces from MAESTRO by split (`train`, `validation`, `test`).
  - Side-by-side audio playback, note statistics, and piano-roll visualization using the identical harmonic synthesis engine.

---

## 60-90 Second Professor Presentation Script

> *"Good morning, Professor. Today I am presenting **MelodyLoop**, an educational deep learning project demonstrating sequential music generation using an LSTM trained from scratch.*
>
> *Music is inherently temporal—a note's meaning depends on what preceded it. Rather than treating MIDI as raw bytes, we built an event-based pipeline from the MAESTRO classical piano dataset. Every note is decomposed into three discrete features: its **Pitch**, its **Quantized Duration**, and the **Time Step** until the next note.*
>
> *These tokens pass through separate embedding layers into a custom PyTorch LSTM with 128 hidden units. At each time step, the network maintains internal memory and optimizes a multi-task cross-entropy loss across three prediction heads.*
>
> *To produce musically coherent phrasing rather than random notes, we implemented **Top-K candidate filtering** and **tuned temperature sampling**, eliminating low-probability tail outliers. We also developed a **Seeded Phrase Continuation** mode, allowing the LSTM to take the opening bars of a real classical performance and predict the musical continuation.*
>
> *Everything was trained on an NVIDIA RTX 3050 Laptop GPU using PyTorch with CUDA acceleration, running 100% locally. In our Streamlit app, we can compare human performances side-by-side with LSTM compositions. Let me now play a live sample."*

---

## Limitations & Common Errors

1. **Monophonic Representation**: Chords with step=0 are played sequentially with zero time delay. Complex polyphonic voice leading can sometimes sound clustered.
2. **Audio Synthesis Preview**: The audio preview is generated by a lightweight NumPy additive synthesizer for instant local playback. For concert-quality acoustic piano rendering, import the generated `.mid` file into any Digital Audio Workstation (DAW) with a piano soundfont.
3. **Windows Console Encoding**: If terminal logging encounters encoding warnings, `train.py` automatically enforces UTF-8 streaming and clean ASCII banners.
