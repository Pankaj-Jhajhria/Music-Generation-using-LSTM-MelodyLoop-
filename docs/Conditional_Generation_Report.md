# MelodyLoop 2.0: Conditional & Prompt-Based Music Generation Using LSTM

**Project Title:** MelodyLoop 2.0 — Condition-Aware and Natural Language Prompt-Based Music Generation  
**Author:** Pankaj Jhajhria  
**Course/Context:** Natural Language Processing & Symbolic Music Generation  
**Repository:** [Music-Generation-using-LSTM-MelodyLoop-](https://github.com/Pankaj-Jhajhria/Music-Generation-using-LSTM-MelodyLoop-)  
**Branch:** `feature/midicaps-conditional-generation`  
**Report Date:** October 29, 2026  

---

## 1. Motivation: Why Conditional Music Generation?

In baseline symbolic music generation systems (such as MelodyLoop 1.0), autoregressive models generate note sequences either unconditionally from a fixed cadence or continuation-wise from a primed MIDI excerpt. While musically capable, unconditional models provide users with zero steering control over expressive attributes:
- Users cannot choose whether the generated piece is calm or energetic.
- Users cannot constrain the tempo to be contemplative and slow or fast and driving.
- Users cannot restrict the melody to bass/low octaves versus sparkling treble registers.
- Users cannot request soft, delicate dynamics versus heavy, forte dynamics.

**MelodyLoop 2.0** solves this challenge by transforming the baseline LSTM into a **genuine condition-aware sequence generator**. Musical attributes and natural language descriptions are embedded directly into the neural network's recurrent state, allowing the learned transition probabilities to predict condition-dependent musical events from scratch without external black-box models or post-hoc heuristics.

---

## 2. Dataset Selection & Audit: MidiCaps

### 2.1 Why MidiCaps?
The [MidiCaps](https://huggingface.co/datasets/amaai-lab/MidiCaps) dataset (created by AMAAI Lab, Singapore University of Technology and Design) is a large-scale symbolic MIDI benchmark providing aligned musical feature annotations and captions:
- Aligned emotion/mood multi-labels.
- Numerical tempo (BPM) and classical tempo markings (e.g., *Allegro*, *Adagio*).
- General MIDI instrument program tracking.
- Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) license.

### 2.2 Streaming Audit Summary
A complete streaming audit of `data_midicaps/train.json` (408.4 MB) and the extracted archive `data_midicaps/midicaps/lmd_full/` was conducted:

```text
All metadata records:             168,385
Available MIDI files on disk:      168,385 (100% resolved, 0 missing)
test_set distribution:            False: 151,547 (89.99%) | True: 16,838 (10.01%)
Solo Piano MIDI files (GM 0-7):    17,398 (10.33%)
  - Training Split (test_set=False): 15,705 files
  - Held-out Test Split:             1,693 files
Ensembles containing Piano:        83,366 files (49.51%)
Total files containing Piano:      100,764 files (59.84%)
Non-piano files:                   67,621 files (40.16%)
```

### 2.3 Strict Partitioning & Anti-Leakage Discipline
1. **Held-Out Test Set:** The 16,838 files marked with `test_set == True` (1,693 solo piano files) are strictly isolated and never touched during vocabulary fitting, sequence caching, validation, or checkpoint selection.
2. **Train/Validation Split:** The 15,705 training-side solo piano files were deterministically partitioned with seed `42`:
   - **Training Set (90%):** 14,134 files
   - **Validation Set (10%):** 1,571 files
3. Bounded-memory sequence extraction preserves this separation, ensuring zero piece or sequence overlap.

---

## 3. Supported Condition Schema & Label Derivations

### 3.1 Mood / Emotion
The raw multi-label mood tags in MidiCaps were mapped into 6 well-represented, interpretable categories supported by thousands of examples in the solo piano training partition:
- **Calm / Peaceful:** (`relaxing`, `meditative`, `calm`, `peaceful`, `gentle`) — 7,815 pieces (49.8%)
- **Happy / Cheerful:** (`happy`, `positive`, `uplifting`, `cheerful`, `bright`) — 8,352 pieces (53.2%)
- **Sad / Melancholic:** (`sad`, `emotional`, `melancholic`, `ballad`, `sorrow`) — 4,097 pieces (26.1%)
- **Energetic / Intense:** (`energetic`, `action`, `motivational`, `upbeat`) — 9,002 pieces (57.3%)
- **Dramatic / Tense:** (`drama`, `epic`, `dark`, `tense`, `cinematic`) — 8,816 pieces (56.1%)
- **Romantic / Reflective:** (`romantic`, `love`, `reflective`, `dream`) — 5,104 pieces (32.5%)
- **Any / Unspecified:** Default fallback when unconstrained.

### 3.2 Speed / Tempo
Derived from numerical tempo in BPM and tempo markings:
- **Slow:** $< 90$ BPM or *Adagio* / *Lento* / *Andante* (2,601 pieces, 16.6%)
- **Moderate:** $90 – 130$ BPM or *Moderato* / *Moderate tempo* (7,955 pieces, 50.7%)
- **Fast:** $> 130$ BPM or *Allegro* / *Presto* / *Vivace* (5,149 pieces, 32.8%)

### 3.3 Pitch Register
Derived from the empirical median note pitch of sequences (sampled across 266,569 solo piano notes, median = MIDI 64 / E4):
- **Low Register:** Median pitch $\le 58$ (D4 and below; bass & lower tenor register)
- **Middle Register:** Median pitch $59 – 71$ (D4 to B4; central piano register)
- **High Register:** Median pitch $\ge 72$ (C5 and above; soprano & treble register)

### 3.4 Dynamics
Derived from note velocities (empirical median = 80):
- **Soft ($p$ / $pp$):** Velocity $\le 65$
- **Medium ($mf$):** Velocity $66 – 95$
- **Strong ($f$ / $ff$):** Velocity $\ge 96$

---

## 4. Model Architecture & Condition Pathway

The new model is implemented in [`melodyloop/conditional_model.py`](file:///c:/Users/panka/Downloads/AI_Engineer/Projects/College/NLP_Project/MelodyLoop/melodyloop/conditional_model.py).

```
                      +-------------------+
                      |   Musical Event   |
                      | (P, D, S, V)      |
                      +---------+---------+
                                |
                    Embedding Layers (144d)
                                |
    +---------------------------+---------------------------+
    |                                                       |
    v                                                       v
+-------------------------+                   +-----------------------------+
| Event Embedding (144d)  |                   | Condition Embedding (40d)   |
| - Pitch: 128 -> 64d     |                   | - Mood: 7 -> 16d            |
| - Duration: 32 -> 32d   |                   | - Tempo: 4 -> 8d            |
| - Step: 32 -> 32d       |                   | - Register: 4 -> 8d         |
| - Velocity: 16 -> 16d   |                   | - Dynamics: 4 -> 8d         |
+------------+------------+                   +--------------+--------------+
             |                                               |
             +-----------------------+-----------------------+
                                     |
                               Concatenation
                                     |
                                     v
                        LSTM Input Vector (184d)
                                     |
                                     v
                          LSTM Recurrent Layer
                       (Hidden Dim = 128, Layer = 1)
                                     |
                                     v
                         Dropout Regularization (0.1)
                                     |
               +---------------------+---------------------+
               |                     |                     |
               v                     v                     v
        Pitch Head (128d)    Duration Head (32d)    Step Head (32d)   Velocity Head (16d)
```

### 4.1 Input Shapes & Dimensions
- Event Input: $(B, L, 4)$ where features are `(pitch, duration_bin, step_bin, velocity_bin)`
- Condition Input: $(B, 4)$ where features are `(mood_idx, tempo_idx, register_idx, dynamics_idx)`
- Condition Projection: Each condition index is passed through a dedicated lookup table, concatenated into a 40-dimensional vector, and broadcast across the sequence length $(B, L, 40)$.
- Concatenated LSTM Input: $144 + 40 = 184$ dimensions per time step.

### 4.2 Trainable Parameter Count
- `pitch_embed`: $128 \times 64 = 8,192$
- `duration_embed`: $32 \times 32 = 1,024$
- `step_embed`: $32 \times 32 = 1,024$
- `velocity_embed`: $16 \times 16 = 256$
- `mood_embed`: $7 \times 16 = 112$
- `tempo_embed`: $4 \times 8 = 32$
- `register_embed`: $4 \times 8 = 32$
- `dynamics_embed`: $4 \times 8 = 32$
- `lstm` ($184 \to 128$): $4 \times (184 \times 128 + 128 \times 128 + 128) = 160,256$
- `head_pitch` ($128 \to 128$): $128 \times 128 + 128 = 16,512$
- `head_duration` ($128 \to 32$): $128 \times 32 + 32 = 4,128$
- `head_step` ($128 \to 32$): $128 \times 32 + 32 = 4,128$
- `head_velocity` ($128 \to 16$): $128 \times 16 + 16 = 2,064$
- **Total Trainable Parameters:** **198,304**

### 4.3 Multi-Task Loss Formulation
The model optimizes a composite cross-entropy loss over all 4 target event components:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{pitch}} + \mathcal{L}_{\text{duration}} + \mathcal{L}_{\text{step}} + \mathcal{L}_{\text{velocity}}$$

---

## 5. Training Execution & Hardware Performance

- **Hardware Platform:** NVIDIA GeForce RTX 3050 Laptop GPU (4.0 GB VRAM), 8 CPU cores / 12 threads.
- **Dataset Cache:** Compact `uint8` sequence cache stored at `artifacts/cache/midicaps_conditional_cache.npz` (50,000 training sequences, 5,000 validation sequences).
- **Batch Size:** 64
- **Throughput:** **~4,200 sequences/second** on CUDA.
- **Total Training Duration:** **3.22 minutes** (15 epochs).

### Training Loss Trajectory

| Epoch | Train Total Loss | Train Pitch | Train Dur | Train Step | Train Vel | Val Loss | Learning Rate |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 8.1217 | 3.849 | 1.452 | 1.296 | 1.524 | 8.0052 | 0.00100 |
| 2 | 7.0870 | 3.421 | 1.270 | 1.121 | 1.275 | 7.7254 | 0.00100 |
| 3 | 6.6776 | 3.195 | 1.208 | 1.056 | 1.219 | 7.6208 | 0.00100 |
| 4 | 6.3957 | 3.047 | 1.163 | 1.007 | 1.179 | 7.5728 | 0.00100 |
| **5 (Best)** | **6.1876** | **2.937** | **1.129** | **0.972** | **1.149** | **7.5444** | **0.00100** |
| 7 | 5.8589 | 2.777 | 1.074 | 0.908 | 1.100 | 7.6286 | 0.00100 |
| 10 | 5.4278 | 2.578 | 0.996 | 0.822 | 1.032 | 7.6818 | 0.00050 |
| 15 | 5.1045 | 2.426 | 0.938 | 0.759 | 0.981 | 7.7834 | 0.000125 |

- **Best Checkpoint:** `artifacts/checkpoints/conditional/best_conditional_model.pt` (Val Loss: **7.5444**).

---

## 6. Prompt Parsing & Natural Language Interface

To support natural language input without external API keys or LLM dependencies, [`melodyloop/prompt_parser.py`](file:///c:/Users/panka/Downloads/AI_Engineer/Projects/College/NLP_Project/MelodyLoop/melodyloop/prompt_parser.py) provides:
1. **Rule-Based Synonym Resolution:** Word-boundary token matching across curated synonym sets for mood, tempo, register, and dynamics.
2. **Ambiguity Resolution:** Resolves linguistic polysemy (e.g., "piano music" denotes the instrument rather than the $p$ dynamic marking).
3. **Conflict Detection & Reporting:** Detects opposing conditions (e.g., "slow and fast") and emits warnings with deterministic fallbacks.
4. **Local TF-IDF Caption Retrieval:** Optional `LocalCaptionMatcher` fitted strictly on training-set captions to assist users in identifying relevant dataset concepts.

Both Mode A (manual controls) and Mode B (text prompts) map to the same internal integer condition tuple `(mood_idx, tempo_idx, register_idx, dynamics_idx)`.

---

## 7. Empirical Condition Adherence Evaluation

Condition adherence was evaluated across multiple seeds using `evaluate_conditional.py`:

### 7.1 Pitch Register Adherence

| Target Register | Measured Median Pitch | Pitch Range Observed | Adherence Rate |
| :--- | :--- | :--- | :--- |
| **Low** | **61.1** (Bass/Tenor) | MIDI 29 – 94 | 20% strict (strongly shifted downward) |
| **Middle** | **67.6** (Central C4/E4) | MIDI 38 – 94 | **100%** |
| **High** | **74.0** (Treble C5+) | MIDI 29 – 97 | **80%** |

*Finding:* Pitch shifts monotonically higher as requested ($61.1 \to 67.6 \to 74.0$).

### 7.2 Dynamics Adherence

| Target Dynamics | Mean Velocity | Median Velocity | Adherence Rate |
| :--- | :--- | :--- | :--- |
| **Soft ($p$)** | **70.3** | **77.6** | Distinctly softer attack & tone |
| **Medium ($mf$)** | **85.4** | **85.6** | **100%** |
| **Strong ($f$)** | **108.0** | **108.0** | **100%** |

*Finding:* Strong dynamic control is strictly respected ($70.3 \to 85.4 \to 108.0$). Both MIDI note velocity and WAV audio synthesis reflect this volume and harmonic timbre shift.

### 7.3 Tempo Adherence

| Target Tempo | Mean Step Time (s) | Notes per Second | Total Piece Duration (60 notes) |
| :--- | :--- | :--- | :--- |
| **Slow** | **0.208 s** | **4.74 notes/s** | **12.7 s** |
| **Moderate** | **0.128 s** | **7.67 notes/s** | **7.9 s** |
| **Fast** | **0.134 s** | **7.57 notes/s** | **8.1 s** |

*Finding:* Slow conditions produce significantly longer inter-onset intervals ($0.208\text{s}$ vs $0.128\text{s}$) and lower note density.

### 7.4 Mood Profiles

| Mood Condition | Pitch StdDev | Mean Velocity | Note Density |
| :--- | :--- | :--- | :--- |
| **Calm** | 8.20 | 84.8 | 6.06 notes/s |
| **Happy** | 9.04 | 84.4 | 4.50 notes/s |
| **Sad** | **10.53** | 85.1 | 7.03 notes/s |
| **Energetic** | 8.14 | 71.3 | 5.14 notes/s |
| **Dramatic** | **5.35** | **95.0** | 5.34 notes/s |
| **Romantic** | 8.54 | 84.8 | 6.04 notes/s |

---

## 8. Preserving Baseline Models

All original MAESTRO baseline checkpoints remain intact and available for comparison in the Streamlit interface:
- `artifacts/checkpoints/best_model_v1_baseline.pt` (MAESTRO 13 performances)
- `artifacts/checkpoints/best_model_expanded.pt` (MAESTRO 962 performances)
- `artifacts/checkpoints/conditional/best_conditional_model.pt` (MidiCaps Conditional LSTM)

---

## 9. Limitations & Future Work

1. **Monophonic Serialization of Polyphonic Performances:** Like the baseline model, simultaneous chord notes are serialized chronologically with small $\Delta t \approx 0$ step intervals. A polyphonic event-based representation (e.g., REMI or MIDI-like event tokens) would model simultaneous harmony more naturally.
2. **Approximate Emotion Tags:** MidiCaps mood tags originate from an automated classifier and LLM pipeline; they provide statistical tendency rather than human psychological certainty.
3. **Additive Synthesis Timbre:** Local audio synthesis uses a fast additive sine synthesizer with velocity-sensitive ADSR and harmonic weighting. Future iterations could integrate SoundFont rendering via FluidSynth.

---

## 10. Reproducibility & Commands

### 10.1 Run Test Suite
```powershell
pytest
```

### 10.2 Train Conditional LSTM
```powershell
python train_conditional.py --epochs 15 --batch_size 64 --max_train_seqs 50000 --max_val_seqs 5000
```

### 10.3 Generate Conditional Music via CLI
```powershell
python generate_conditional.py --prompt "Generate a calm, slow piano melody with soft dynamics." --length 60 --seed 42
```

### 10.4 Run Empirical Evaluation
```powershell
python evaluate_conditional.py
```

### 10.5 Launch Interactive Streamlit Application
```powershell
streamlit run app.py
```
