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

### 1. Run Unit Tests
Verify all preprocessing, model forward passes, generation, and synthesis tests pass:
```powershell
python -m pytest tests/
```

### 2. Train the Model
Run training from the terminal:
```powershell
# Full hardware-aware training on GPU (or CPU fallback)
python train.py --epochs 6 --batch-size 32

# Or quick 1-epoch smoke test
python train.py --smoke-test
```
Checkpoints are saved to `artifacts/checkpoints/best_model.pt` and `artifacts/checkpoints/latest_model.pt`.

### 3. Resume Training
To resume training from an existing checkpoint without restarting:
```powershell
python train.py --resume
```

### 4. Generate Music (CLI)
Generate a 100-note melody from the best checkpoint:
```powershell
python generate.py --length 100 --temperature 0.85 --seed 42
```
Output files:
- MIDI: `artifacts/generated/melody_seed42_temp0.85.mid`
- WAV preview: `artifacts/generated/melody_seed42_temp0.85.wav`

### 5. Launch the Streamlit Interface
```powershell
streamlit run app.py
```

---

## Streamlit Web Interface

The interactive dashboard (`app.py`) provides:
- **Status Panel**: Displays the loaded checkpoint, epoch, validation loss, and target device (CUDA GPU).
- **Interactive Controls**: Sliders for melody length (20–200 notes), sampling temperature (0.1–1.5), and random seed.
- **Piano-Roll Plot**: Note pitch vs. time visualization with Middle C (C4=60) reference line.
- **Local Audio Playback**: Direct playback using zero-dependency additive piano synthesis.
- **One-Click Downloads**: Direct download buttons for generated Standard MIDI (`.mid`) and audio (`.wav`).

---

## 60-90 Second Professor Presentation Script

> *"Good morning, Professor. Today I am presenting **MelodyLoop**, an educational deep learning project demonstrating sequential music generation using an LSTM trained from scratch.*
>
> *Music is inherently temporal—a note's meaning depends on what preceded it. Rather than treating MIDI as raw bytes, we built an event-based pipeline from the MAESTRO classical piano dataset. Every note is decomposed into three discrete features: its **Pitch**, its **Quantized Duration**, and the **Time Step** until the next note.*
>
> *These tokens pass through separate embedding layers into a custom PyTorch LSTM with 128 hidden units. At each time step, the network maintains internal memory and optimizes a multi-task cross-entropy loss across three prediction heads.*
>
> *For generation, we sample autoregressively using temperature scaling: lower temperatures stick to familiar harmonic patterns, while higher temperatures introduce variation. The output is exported to standard MIDI and visualized on a dynamic piano roll.*
>
> *Because we detected an RTX 3050 Laptop GPU, we configured bounded sequence batching to fit comfortably within the 4 GB VRAM limit. Everything runs 100% locally with zero cloud dependencies. Let me now play a live sample generated by our trained checkpoint."*

---

## Limitations & Common Errors

1. **Monophonic Representation**: Chords with step=0 are played sequentially with zero time delay. Complex polyphonic voice leading can sometimes sound clustered.
2. **Audio Synthesis Preview**: The audio preview is generated by a lightweight NumPy additive synthesizer for instant local playback. For concert-quality acoustic piano rendering, import the generated `.mid` file into any Digital Audio Workstation (DAW) with a piano soundfont.
3. **Windows Console Encoding**: If terminal logging encounters encoding warnings, `train.py` automatically enforces UTF-8 streaming and clean ASCII banners.
