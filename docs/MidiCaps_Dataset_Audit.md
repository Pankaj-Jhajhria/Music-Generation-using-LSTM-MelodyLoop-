# MidiCaps Dataset Audit Report — MelodyLoop 2.0

**Audit Date:** October 29, 2026  
**Auditor:** MelodyLoop Core Engineering Team  
**Dataset Source:** [amaai-lab/MidiCaps (Hugging Face)](https://huggingface.co/datasets/amaai-lab/MidiCaps)  
**License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)  
**Associated Paper:** *MidiCaps: A Large-scale MIDI Dataset with Captions and Audio-derived Musical Attributes* (AMAAI Lab, SUTD)

---

## 1. Executive Summary & Verification

A full streaming audit of the local MidiCaps metadata (`data_midicaps/train.json`) and extracted MIDI archive (`data_midicaps/midicaps/lmd_full/`) was completed.

- **Total Metadata Records in `train.json`:** 168,385
- **Unique Relative File Locations:** 168,385 (100% unique, zero duplicates)
- **Extracted MIDI Files on Disk:** 168,385
- **Resolved MIDI Files:** 168,385 (100% file existence rate, 0 missing files)
- **Official Split Distribution (`test_set` field):**
  - Training split (`test_set == False`): **151,547** (89.99%)
  - Held-out test split (`test_set == True`): **16,838** (10.01%)

---

## 2. Instrument & Piano Compatibility Breakdown

MelodyLoop 2.0 focuses on piano-oriented music generation to build directly upon the baseline MAESTRO piano generator. In General MIDI (GM), the piano family corresponds to program numbers 0 through 7:
- Program 0: Acoustic Grand Piano
- Program 1: Bright Acoustic Piano
- Program 2: Electric Grand Piano
- Program 3: Honky-tonk Piano
- Program 4: Electric Piano 1 (Rhodes)
- Program 5: Electric Piano 2 (Chorused)
- Program 6: Harpsichord
- Program 7: Clavinet

### Verified Counts:

| Category | Total Records | Share of Full Dataset | Training Split (`test_set=False`) | Held-out Test (`test_set=True`) |
| :--- | :--- | :--- | :--- | :--- |
| **Solo Piano** (GM Programs 0–7 only) | **17,398** | **10.33%** | **15,705** | **1,693** |
| **Ensembles with Piano** | 83,366 | 49.51% | 75,028 | 8,338 |
| **Total Containing Piano** | **100,764** | **59.84%** | **90,733** | **10,031** |
| **Non-Piano Music** | 67,621 | 40.16% | 60,814 | 6,807 |

> [!NOTE]
> For clean, authentic symbolic piano training, we utilize the **15,705 solo piano performances** in the training partition for our core candidate pool. This completely eliminates poly-instrumental interference, drum tracks, and non-piano synthesizer tracks from the baseline piano model without requiring lossy multi-track extraction heuristics.

---

## 3. Metadata Fields & Missingness Analysis

MidiCaps records contain 19 structured keys. All fields were audited for missing or null entries:

| Field Name | Type | Missing Count | Missing % | Description |
| :--- | :--- | :--- | :--- | :--- |
| `location` | string | 0 | 0.00% | Relative path inside `lmd_full/` |
| `caption` | string | 0 | 0.00% | Synthetic LLM-generated description |
| `genre` | list[str] | 0 | 0.00% | Predicted genre tags |
| `genre_prob` | list[float]| 0 | 0.00% | Genre classifier confidence probabilities |
| `mood` | list[str] | 0 | 0.00% | Multi-label mood/emotion tags |
| `mood_prob` | list[float]| 0 | 0.00% | Mood classifier confidence probabilities |
| `key` | string | 0 | 0.00% | Detected musical key and scale mode |
| `time_signature` | string | 0 | 0.00% | Meter (e.g. 4/4, 3/4) |
| `tempo` | float | 1,215 | 0.72% | Numerical tempo in BPM |
| `tempo_word` | string | 1,215 | 0.72% | Italian/descriptive tempo marking |
| `duration` | float | 0 | 0.00% | Track duration in seconds |
| `duration_word` | string | 0 | 0.00% | Descriptive length classification |
| `chord_summary` | list[str] | 0 | 0.00% | Common harmonic progressions |
| `instrument_summary` | list[str] | 0 | 0.00% | Names of detected instruments |
| `instrument_numbers_sorted` | list[int] | 0 | 0.00% | Sorted General MIDI program numbers |
| `test_set` | bool | 0 | 0.00% | Official partition flag |

---

## 4. Condition Attribute Distributions

### 4.1 Mood Coverage (Solo Piano Training Partition, N=15,705)

The raw MidiCaps mood tags stem from an automated classifier and LLM pipeline. We map the raw tags into 6 well-represented, interpretable musical categories:

| Target Condition Category | Included Raw Tags / Aliases | Solo Piano Count | Coverage % |
| :--- | :--- | :--- | :--- |
| **Energetic** | `energetic`, `action`, `motivational`, `upbeat`, `intense` | 9,002 | 57.3% |
| **Dramatic** | `drama`, `epic`, `dark`, `tense` | 8,816 | 56.1% |
| **Happy** | `happy`, `positive`, `uplifting`, `cheerful`, `bright` | 8,352 | 53.2% |
| **Calm** | `relaxing`, `meditative`, `calm`, `peaceful`, `gentle` | 7,815 | 49.8% |
| **Romantic** | `romantic`, `love`, `reflective`, `dream` | 5,104 | 32.5% |
| **Sad** | `sad`, `emotional`, `melancholic`, `ballad`, `sorrow` | 4,097 | 26.1% |

Every target mood category has at least 4,000 distinct solo piano training pieces.

### 4.2 Tempo Distributions

- **Numerical Tempo (BPM):**
  - Minimum: 6.0 BPM (outlier / rubato)
  - 25th Percentile: 94.0 BPM
  - Median: 118.0 BPM
  - 75th Percentile: 132.0 BPM
  - Maximum: 960.0 BPM (corrupted header outlier)

- **Standardized Speed Categories (Solo Piano Training):**
  - **Slow** (`< 90 BPM` or `Andante`/`Adagio`/`Slow`): **2,601 pieces (16.6%)**
  - **Moderate** (`90 – 130 BPM` or `Moderate tempo`/`Moderato`): **7,955 pieces (50.7%)**
  - **Fast** (`> 130 BPM` or `Allegro`/`Presto`/`Fast`): **5,149 pieces (32.8%)**

### 4.3 Pitch Register Boundaries

Empirical pitch distribution across 200 sample solo piano pieces (266,569 notes):
- Minimum: MIDI 21 (A0)
- 25th Percentile: MIDI 54 (F#3)
- Median: MIDI 64 (E4)
- 75th Percentile: MIDI 73 (C#5)
- Maximum: MIDI 108 (C8)

**Defined Pitch Register Classes (based on sequence median pitch):**
- **Low Register:** Median pitch $\le 58$ (below D4, occupying bass and lower tenor)
- **Middle Register:** Median pitch between $59$ and $71$ (D4 to B4, occupying middle keyboard range)
- **High Register:** Median pitch $\ge 72$ (C5 and above, occupying soprano and upper treble register)

### 4.4 Dynamics & Note Velocities

Empirical note velocities across 266,569 solo piano notes:
- Minimum: 1
- 25th Percentile: 63
- Median: 80
- 75th Percentile: 101
- Maximum: 127

**Defined Dynamics Classes (based on sequence median velocity):**
- **Soft (piano / pp):** Velocity $\le 65$
- **Medium (mezzo-forte):** Velocity $66 – 95$
- **Strong (forte / ff):** Velocity $\ge 96$

In addition to condition conditioning, the sequence event representation is upgraded to 4 tokens per step: `(pitch, duration_bin, step_bin, velocity_bin)`. This enables the LSTM to learn and generate distinct velocity distributions.

---

## 5. Dataset Partitioning & Leakage Prevention

To prevent data leakage:
1. **Held-out Test Set:** The 16,838 files marked with `test_set == True` (including 1,693 solo piano files) are strictly isolated. They are never touched during vocabulary derivation, training, validation, or checkpoint selection.
2. **Train/Validation Split:** The 15,705 training-side solo piano files (`test_set == False`) are split deterministically with fixed seed `42`:
   - **Training Set (90%):** 14,134 files
   - **Validation Set (10%):** 1,571 files
3. Sequence generation from validation files uses validation-only tracks, ensuring zero event sequence leakage across splits.

---

## 6. Licensing & Ethical Considerations

- **Dataset License:** CC BY-SA 4.0. Users are free to share and adapt the material provided appropriate credit is given and derivative works are distributed under the same license.
- **Model Checkpoints & Generated MIDI:** MelodyLoop models trained on MidiCaps learn statistical associations over symbolic MIDI representations. Generated MIDI files are novel synthetic sequences and are safe for academic, educational, and creative exploration.
- **Caption Attribution Disclaimer:** The natural-language captions and mood labels in MidiCaps were generated via an automated LLM and music-tagging pipeline. They represent approximate computational approximations rather than definitive psychological ground truth.
