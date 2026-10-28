"""
MelodyLoop Documentation Guide — Chapters 16 to 20 Builder
Contains:
- Chapter 16: Why the Generated Music May Sound Random (Critical Failure Analysis)
- Chapter 17: Git, Dependencies, and Reproducibility
- Chapter 18: Full End-to-End Workflow Diagram
- Chapter 19: Difficult Viva Questions and Answers (55 Comprehensive Q&As)
- Chapter 20: Presentation and Revision Material (Scripts, Formulas, Traps, Glossary)
"""

from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, PageBreak, HRFlowable, KeepTogether, Table, TableStyle
from pdf_builder_helpers import make_callout, make_code_panel, make_styled_table, make_figure

BLUE_ACCENT = colors.HexColor("#1e40af")


def build_chapter_16(story, styles):
    story.append(Paragraph("Chapter 16 — Why the Generated Music May Sound Random", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph("16.1 Critical Academic Self-Evaluation", styles["SectionHeading"]))
    story.append(Paragraph(
        "A standout quality of an exceptional engineering viva is the willingness to critically dissect the limitations of one's own model. "
        "While MelodyLoop successfully generates syntactically valid MIDI and coherent rhythmic patterns, an attentive listener will notice "
        "that in free generation mode, the music can wander aimlessly rather than developing structured themes like a human composer. "
        "Here is the rigorous technical post-mortem distinguishing <b>empirically proven facts</b> from <b>hypotheses</b>:",
        styles["BodyDark"]
    ))

    story.append(Paragraph("16.2 Factor 1: The Cross-Entropy Objective vs. Musical Structure (Fact)", styles["SectionHeading"]))
    story.append(Paragraph(
        "Cross-entropy loss measures only <i>one-step-ahead prediction accuracy</i>. If the model predicts that the next note has a 40% probability "
        "of being D4 and a 35% probability of being E4, both predictions incur low loss. However, in musical composition, choosing D4 versus E4 "
        "changes the entire harmonic progression (e.g., minor second clash vs. major third consonance). The loss function has zero awareness of "
        "cadential resolution, voice leading, or 8-bar phrase symmetry.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("16.3 Factor 2: Polyphony Flattening into a 1D Stream (Fact)", styles["SectionHeading"]))
    story.append(Paragraph(
        "A classical piano piece has two hands playing up to 10 notes simultaneously across bass and treble clefs. "
        "MelodyLoop sorts all notes into a single chronological stream. When a pianist plays a chord (e.g., C-E-G), the notes are serialized as "
        "three consecutive events with step=0.0. The LSTM is forced to model a 2-dimensional polyphonic matrix as an alternating 1-dimensional "
        "string, which creates unnatural pitch leaps between the left-hand bass accompaniment and right-hand melody.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("16.4 Factor 3: Context Horizon and Memory Limits (Fact)", styles["SectionHeading"]))
    story.append(Paragraph(
        "The model's input context is strictly <b>32 note events</b>. At an average tempo of 120 BPM with sixteenth notes, 32 notes correspond "
        "to only <b>4 to 8 seconds of music</b>. Classical music develops themes over 30 to 60 seconds (Sonata-Allegro form). "
        "Because the LSTM cannot remember what happened 50 notes ago, it cannot resolve an opening theme or return to the tonic key.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("16.5 Factor 4: Sampling Temperature and Tail Chaos (Fact)", styles["SectionHeading"]))
    story.append(Paragraph(
        "At high temperatures ($T > 0.8$), the softmax probability distribution flattens, giving low-probability, dissonant notes "
        "a substantial chance of being selected. Once an out-of-key note is sampled, it enters the input context for the next 32 steps, "
        "compounding error propagation. MelodyLoop mitigated this by introducing <b>top-k candidate filtering ($K=5$)</b> and "
        "<b>seeded phrase continuation</b>.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("16.6 Future Architectural Roadmap", styles["SectionHeading"]))
    story.append(Paragraph(
        "To achieve professional compositional coherence in future iterations, the following architectural upgrades are recommended:<br/>"
        "1. <b>Music Transformer / Self-Attention:</b> Replace the single-layer LSTM with a Transformer architecture (Vaswani et al.) "
        "using relative positional embeddings (Huang et al.), extending the context window from 32 to 2,048 notes.<br/>"
        "2. <b>REMI (Rich Event-based MIDI) Tokenization:</b> Explicitly encode Bar, Position, Pitch, and Velocity tokens to preserve musical meter.<br/>"
        "3. <b>Multi-Track Polyphony:</b> Separate left-hand and right-hand streams into independent recurrent channels.<br/>"
        "4. <b>Reinforcement Learning with Musical Rewards:</b> Fine-tune the network using RL (PPO) with reward functions based on "
        "scale adherence, harmonic cadence, and rhythmic groove.",
        styles["BodyDark"]
    ))

    story.append(PageBreak())


def build_chapter_17(story, styles):
    story.append(Paragraph("Chapter 17 — Git, Dependencies, and Reproducibility", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph("17.1 Repository Architecture and Version Control", styles["SectionHeading"]))
    story.append(Paragraph(
        "The project is hosted publicly on GitHub at:<br/>"
        "<font face='Courier'>https://github.com/Pankaj-Jhajhria/Music-Generation-using-LSTM-MelodyLoop-</font><br/>"
        "Git version control is utilized to maintain an immutable audit trail of feature additions, bug fixes, and documentation milestones. "
        "Recent repository commit history reveals disciplined software engineering practices:",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "• <font face='Courier'>c31e0b9</font>: feat: Add academic PowerPoint presentation generator and generated slide deck.<br/>"
        "• <font face='Courier'>272525b</font>: docs: Update README with top-k sampling, seeded continuation, and presentation guide.<br/>"
        "• <font face='Courier'>83df25c</font>: Improve musical coherence: Add top-k sampling, temperature tuning, repetition penalties, and seeded phrase continuation.<br/>"
        "• <font face='Courier'>9781e2c</font>: Add Human vs LSTM dataset comparison tab to Streamlit app.<br/>"
        "• <font face='Courier'>3c1f5cf</font>: Fix event tuple unpacking in play_sample.py.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("17.2 The .gitignore Policy: Why Binary Files Are Excluded", styles["SectionHeading"]))
    story.append(Paragraph(
        "In collaborative AI engineering, pushing gigabytes of datasets or binary checkpoints directly into Git repositories "
        "bloats repository size and violates Git best practices. MelodyLoop's <font face='Courier'>.gitignore</font> strictly excludes:<br/>"
        "• <font face='Courier'>data_maestrov3.0.0-midi/</font>: Multi-gigabyte raw dataset.<br/>"
        "• <font face='Courier'>artifacts/checkpoints/*.pt</font>: Heavy neural weight binaries.<br/>"
        "• <font face='Courier'>artifacts/generated/*.wav</font>: Generated audio waveforms.<br/>"
        "• <font face='Courier'>__pycache__/ & .pytest_cache/</font>: Ephemeral execution caches.<br/>"
        "This ensures that cloning the repository takes seconds while maintaining 100% reproducibility via code.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("17.3 Minimal Dependencies (requirements.txt)", styles["SectionHeading"]))
    story.append(Paragraph(
        "MelodyLoop deliberately avoids bloated external libraries, requiring only standard scientific packages:",
        styles["BodyDark"]
    ))
    story.append(make_code_panel("""torch>=2.0.0        # PyTorch deep learning framework
numpy>=1.24.0       # Numerical matrix operations & signal processing
pandas>=2.0.0       # CSV metadata ingestion & filtering
mido>=1.3.0         # Pure Python MIDI file parsing and event export
streamlit>=1.30.0   # Reactive web application interface
matplotlib>=3.7.0   # Piano-roll and loss curve visualizations
scipy>=1.10.0       # 16-bit PCM WAV audio file export""", styles=styles))

    story.append(PageBreak())


def build_chapter_18(story, styles):
    story.append(Paragraph("Chapter 18 — Full End-to-End Workflow Diagram", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph("18.1 Master System Pipeline Architecture", styles["SectionHeading"]))
    story.append(Paragraph(
        "The diagram below illustrates the complete lifecycle of musical information inside MelodyLoop, tracing the path from "
        "raw acoustic performances in the MAESTRO dataset through neural training, checkpoint serialization, autoregressive inference, "
        "additive harmonic synthesis, and final web application delivery:",
        styles["BodyDark"]
    ))

    story.append(make_figure("fig10_end_to_end_flowchart.png", "Complete End-to-End Architectural Pipeline Flowchart for MelodyLoop", width=515, height=270, styles=styles))

    story.append(Paragraph("18.2 Phase Identification and Module Mapping", styles["SectionHeading"]))
    story.append(Paragraph(
        "The end-to-end architecture is partitioned into three distinct operational phases:",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "• <b>Phase 1: Training Pipeline (Offline):</b> Executed exclusively by <font face='Courier'>train.py</font> using <font face='Courier'>melodyloop/data.py</font> "
        "and <font face='Courier'>melodyloop/model.py</font>. Learns multi-task weights and serializes <font face='Courier'>best_model.pt</font> to disk.",
        styles["BulletText"]
    ))
    story.append(Paragraph(
        "• <b>Phase 2: Music Generation (Online Inference):</b> Executed by <font face='Courier'>melodyloop/generation.py</font> and <font face='Courier'>generate.py</font>. "
        "Loads checkpoint weights, charges context buffer, performs autoregressive top-k sampling, and exports Standard MIDI files.",
        styles["BulletText"]
    ))
    story.append(Paragraph(
        "• <b>Phase 3: Acoustic Rendering and Delivery:</b> Executed by <font face='Courier'>melodyloop/audio.py</font> and <font face='Courier'>app.py</font>. "
        "Converts symbolic MIDI notes into audible 16-bit PCM WAV audio via additive synthesis and serves interactive controls to the user.",
        styles["BulletText"]
    ))

    story.append(PageBreak())


def build_chapter_19(story, styles):
    story.append(Paragraph("Chapter 19 — Difficult Viva Questions and Answers", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph(
        "This chapter provides <b>55 high-caliber, examiner-grade viva questions</b> organized across 6 core technical domains. "
        "Each answer is structured with an immediate direct answer, deep technical justification, and exact code references.",
        styles["BodyDark"]
    ))

    viva_qas = [
        # --- Topic 1: Project Fundamentals ---
        ("Q1: What is MelodyLoop in one sentence?",
         "MelodyLoop is an educational deep learning system that trains a multi-task PyTorch LSTM from scratch on symbolic MIDI piano performances to autoregressively compose and synthesize new music.",
         "It models music symbolically rather than acoustically, using categorical cross-entropy loss to predict the next note's pitch, duration, and time step.",
         "Implemented in melodyloop/model.py and train.py."),

        ("Q2: Why did you choose symbolic MIDI over raw audio waveforms?",
         "Computational feasibility and note-level interpretability.",
         "Raw audio requires processing 44,100 floating-point samples per second, demanding high-end multi-GPU clusters. Symbolic MIDI reduces music to discrete note tuples (~5 events/second), allowing full training in 4 minutes on a 4 GB laptop GPU.",
         "See Chapter 1 and Table 1.1."),

        ("Q3: Is MelodyLoop supervised, unsupervised, or self-supervised learning?",
         "It is self-supervised autoregressive sequence learning.",
         "No human manually labeled the data. The training targets are naturally derived from the sequential data itself: given notes 0 to 31, the target label is note 32.",
         "Implemented in create_sequences_from_events() in melodyloop/data.py:132."),

        ("Q4: What are the three properties predicted for every note?",
         "Pitch, Duration, and Step (Inter-Onset Interval).",
         "Pitch specifies key frequency (0-127), Duration specifies how long the note sustains (quantized to 32 bins), and Step specifies the time to the subsequent note (quantized to 32 bins).",
         "Defined in config.py:55-57 and model.py:43-45."),

        ("Q5: Did you use a pre-trained foundation model?",
         "No. The model was trained entirely from scratch with randomly initialized weights.",
         "This was chosen to ensure complete educational transparency and avoid hidden training biases or licensing violations.",
         "Verified by model initialization in train.py:268."),

        ("Q6: How many parameters does the model have?",
         "Exactly 167,104 trainable parameters.",
         "Embeddings contribute 10,240 parameters, the single-layer LSTM contributes 132,096 parameters, and the three linear prediction heads contribute 24,768 parameters.",
         "Verified via model.count_parameters() in melodyloop/model.py:106 and Chapter 8."),

        ("Q7: What is the primary baseline you compare your generated music against?",
         "Real human virtuoso piano performances from the MAESTRO dataset.",
         "The Streamlit app and play_sample.py tool provide side-by-side auditory and piano-roll comparisons rendered through the exact same additive synthesis engine.",
         "Implemented in app.py:214 and play_sample.py:162."),

        ("Q8: Why does the system use additive synthesis instead of an external soundfont?",
         "To guarantee 100% portability and eliminate external software dependencies.",
         "Soundfont engines like FluidSynth require external system binaries and large .sf2 files. MelodyLoop synthesizes 16-bit WAVs using pure NumPy and SciPy.",
         "Implemented in melodyloop/audio.py:13."),

        ("Q9: What happens if an end-user runs the app without training a model?",
         "The app detects missing checkpoints and displays an informative warning banner.",
         "The Generate button is disabled until a valid checkpoint is placed in artifacts/checkpoints/.",
         "Implemented in app.py:288."),

        ("Q10: What is the license of your codebase and dataset?",
         "The project code is open-source; the MAESTRO dataset is licensed under Creative Commons CC BY-NC-SA 4.0.",
         "This permits academic non-commercial research with attribution.",
         "Verified in data_maestrov3.0.0-midi/maestro-v3.0.0/LICENSE."),

        # --- Topic 2: Music Theory & MIDI Data ---
        ("Q11: How many keys does a standard piano have, and what is its MIDI range?",
         "A standard piano has 88 keys, spanning MIDI pitches 21 (A0) to 108 (C8).",
         "The full MIDI protocol supports 128 note numbers (0-127) because it uses a 7-bit unsigned integer.",
         "See Chapter 2 and Figure 1."),

        ("Q12: What is Middle C in MIDI?",
         "Middle C is designated as C4, corresponding to MIDI pitch number 60 (261.63 Hz).",
         "Concert A (A4) is pitch 69 (440.00 Hz).",
         "See Chapter 2.2."),

        ("Q13: How do you mathematically convert MIDI pitch to frequency in Hertz?",
         "Using the formula: f = 440.0 * 2^((p - 69) / 12).",
         "Because Western tuning uses 12-tone equal temperament, each semitone represents a frequency ratio of 2^(1/12).",
         "Implemented in melodyloop/audio.py:44."),

        ("Q14: What is an Inter-Onset Interval (Step), and why is it crucial?",
         "Step is the time duration between the start of the current note and the start of the next note.",
         "It separates note duration from note onset timing. A step of 0.0 seconds represents a chord (simultaneous notes).",
         "Implemented in melodyloop/data.py:120."),

        ("Q15: How does your system handle chords and polyphony?",
         "Notes are sorted by start time, and simultaneous notes are serialized with step = 0.0s.",
         "During playback or MIDI export, notes with step=0.0 sound simultaneously, producing polyphonic harmony.",
         "Implemented in melodyloop/data.py:112 and generation.py:245."),

        ("Q16: Why did you quantize duration and step into 32 bins?",
         "To frame duration and timing prediction as discrete classification rather than continuous regression.",
         "Classification with cross-entropy avoids assuming a Gaussian error distribution and models multi-modal rhythmic distributions effectively.",
         "Defined in config.py:56-57 and data.py:30."),

        ("Q17: What are the bounds for duration and step quantization?",
         "Duration spans 0.05s to 4.0s; Step spans 0.0s to 2.0s.",
         "Values outside these bounds are strictly clamped prior to linear binning.",
         "Defined in config.py:58-61."),

        ("Q18: What is the ticks_per_beat setting in your MIDI export?",
         "480 ticks per beat (quarter note).",
         "This standard resolution allows precise representation of sixteenth notes (120 ticks) and triplets (160 ticks).",
         "Defined in melodyloop/generation.py:219."),

        ("Q19: How do you prevent corrupt MIDI files from crashing your preprocessor?",
         "Using mido.MidiFile(clip=True) inside a try-except block.",
         "Invalid files log a warning and return an empty list, allowing dataset loading to continue uninterrupted.",
         "Implemented in melodyloop/data.py:72-76."),

        ("Q20: What is velocity in MIDI, and how is it used in your synthesizer?",
         "Velocity represents key strike force (0-127).",
         "In our MIDI export, notes use a default musical velocity of 85 for note_on and 64 for note_off.",
         "Implemented in melodyloop/generation.py:249-250."),

        # --- Topic 3: Deep Learning & LSTM Math ---
        ("Q21: Why not use a standard feedforward neural network?",
         "Feedforward networks have no memory and assume all inputs are independent.",
         "Music requires temporal context: the meaning of a note depends entirely on preceding harmonic and melodic context.",
         "See Chapter 1.3 and Chapter 7.1."),

        ("Q22: Why not use a basic RNN?",
         "Basic RNNs suffer from vanishing and exploding gradients during backpropagation through time.",
         "Repeated matrix multiplication causes gradients over 32 time steps to decay to zero, preventing the network from learning dependencies beyond a few notes.",
         "See Chapter 7.2."),

        ("Q23: How does the LSTM overcome the vanishing gradient problem?",
         "Through the Cell State highway, which uses additive linear updates rather than repeated matrix multiplication.",
         "Because C_t = f_t * C_{t-1} + i_t * C_tilde, gradients flow backward through time without exponential decay.",
         "See Chapter 7.3 and Figure 5."),

        ("Q24: What are the four gates inside an LSTM cell?",
         "The Forget Gate (f_t), Input Gate (i_t), Candidate Cell State (C_tilde), and Output Gate (o_t).",
         "f_t controls what to erase; i_t and C_tilde control what to write; o_t controls what to output to h_t.",
         "Formulas detailed in Chapter 7.4."),

        ("Q25: What activation functions are used in the LSTM gates, and why?",
         "Sigmoid for gates; Tanh for states.",
         "Sigmoid bounds values between 0.0 and 1.0, acting as a soft binary switch. Tanh bounds values in [-1.0, +1.0], regulating state magnitude.",
         "See Chapter 7.4."),

        ("Q26: What is the Hadamard product (odot)?",
         "Element-wise vector multiplication.",
         "In C_t = f_t odot C_{t-1}, each memory unit is scaled individually by its corresponding forget gate value.",
         "See Chapter 7.4."),

        ("Q27: What is the dimension of the input tensor entering the LSTM layer?",
         "[Batch_Size, Sequence_Length, Input_Dim] = [32, 32, 128].",
         "128 comes from concatenating pitch embedding (64), duration embedding (32), and step embedding (32).",
         "Implemented in melodyloop/model.py:68."),

        ("Q28: Why use learned embeddings instead of one-hot vectors?",
         "Embeddings compress sparse dimensions into dense, continuous representations that learn musical relationships.",
         "One-hot vectors are orthogonal and cannot represent harmonic proximity. Embeddings allow pitch 60 and pitch 64 to learn proximity in latent space.",
         "Implemented in melodyloop/model.py:24-26."),

        ("Q29: What is dropout, and where is it applied in your model?",
         "Dropout randomly zeroes neural activations during training to prevent co-adaptation and overfitting.",
         "It is applied with p=0.1 to the final LSTM output before the prediction heads.",
         "Implemented in melodyloop/model.py:40, 74."),

        ("Q30: How many layers does your LSTM have, and why?",
         "One recurrent layer.",
         "This keeps the model lightweight (167k params), prevents rapid overfitting on small sequence budgets, and allows fast training on laptop GPUs.",
         "Defined in config.py:68."),

        # --- Topic 4: Training Dynamics & Optimization ---
        ("Q31: What loss function is used, and how are multi-task losses combined?",
         "Categorical Cross-Entropy, combined via unweighted sum: L_total = L_pitch + L_duration + L_step.",
         "Each head computes standard cross-entropy loss against its respective target token.",
         "Implemented in melodyloop/model.py:97."),

        ("Q32: What optimizer was used, and what were its hyperparameters?",
         "Adam optimizer with learning rate = 1e-3 and weight decay = 1e-5.",
         "Adam adapts individual learning rates per parameter using running estimates of gradient first and second moments.",
         "Implemented in train.py:271-273."),

        ("Q33: What is gradient norm clipping, and what threshold did you use?",
         "It scales gradients if their L2 norm exceeds a threshold, preventing gradient explosion.",
         "We used max_norm = 1.0.",
         "Implemented in train.py:114."),

        ("Q34: What was your batch size and sequence length?",
         "Batch size = 32 (CUDA); Sequence length = 32 events.",
         "Sequence length 32 provides sufficient local context (~8 seconds of music) while maintaining manageable memory usage.",
         "Defined in config.py:72, 81."),

        ("Q35: What hardware was used for training, and how long did it take?",
         "An NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM) using CUDA.",
         "The full 9-epoch training run executed in approximately 3.5 minutes (~16-29 seconds per epoch).",
         "Verified in artifacts/logs/training.log."),

        ("Q36: What was your best validation loss, and at which epoch did it occur?",
         "Best validation loss was 6.1791, achieved at Epoch 4.",
         "Validation pitch loss was 3.759, duration loss was 0.965, and step loss was 1.455.",
         "Verified in best_model.pt and training.log."),

        ("Q37: Why did training stop at Epoch 9 if 20 epochs were planned?",
         "Early stopping was triggered after 5 consecutive epochs without validation loss improvement.",
         "Epochs 5 through 9 exhibited rising validation loss (6.20-6.30) despite falling training loss, indicating onset of overfitting.",
         "Verified in train.py:355 and training.log:594."),

        ("Q38: What is the difference between best_model.pt and latest_model.pt?",
         "best_model.pt stores weights from Epoch 4 (lowest val loss); latest_model.pt stores weights from Epoch 9 (final state).",
         "best_model.pt is used for inference; latest_model.pt is used for resuming training.",
         "Verified in artifacts/checkpoints/ and train.py:326-351."),

        ("Q39: What is sequence balancing, and why was it necessary?",
         "Capping the number of training sequences extracted from any single MIDI file.",
         "Without balancing, a single lengthy piece would dominate the dataset. Balancing ensures broad exposure across diverse composers.",
         "Implemented in melodyloop/data.py:205-226."),

        ("Q40: How did you enforce train/validation separation?",
         "By strictly filtering on MAESTRO's official 'split' column in the metadata CSV.",
         "No performances from the validation split were ever exposed during the training phase.",
         "Implemented in melodyloop/data.py:192."),

        # --- Topic 5: Generation & Sound Synthesis ---
        ("Q41: What is autoregressive generation?",
         "Generating a sequence step-by-step, where each newly predicted token is appended to the context to predict the next.",
         "The output of step t becomes part of the input for step t+1.",
         "Implemented in melodyloop/generation.py:160-210."),

        ("Q42: What is sampling temperature, and what value is optimal?",
         "A hyperparameter T that scales logits prior to softmax: P_i = exp(z_i / T) / sum(exp(z_j / T)).",
         "T=0.6 is optimal for MelodyLoop: it preserves melodic structure while allowing creative variation.",
         "Implemented in melodyloop/generation.py:70."),

        ("Q43: What is top-k sampling, and why did you add it?",
         "Restricting candidate selection to the K highest-probability tokens, setting all other logits to -infinity.",
         "It eliminates chaotic, disharmonious tail selections (e.g. random 3-octave leaps). We use K=5 for pitch.",
         "Implemented in melodyloop/generation.py:61-67."),

        ("Q44: What is the repetition penalty?",
         "Subtracting a penalty from the logits of tokens that appeared in the last 3 time steps.",
         "It prevents the LSTM from getting trapped in repetitive 2-note stutters.",
         "Implemented in melodyloop/generation.py:46-50."),

        ("Q45: What is seeded phrase continuation?",
         "Prompting the model with the opening notes of a real MAESTRO performance instead of an artificial cadence.",
         "The model preserves the prompt notes and predicts a stylistically aligned continuation.",
         "Implemented in melodyloop/generation.py:117-138."),

        ("Q46: How does your additive synthesizer produce a piano-like sound?",
         "By combining the fundamental frequency with 2nd and 3rd harmonics: 0.60*f0 + 0.25*2f0 + 0.15*3f0.",
         "Real piano strings vibrate in harmonic modes. Combining harmonics creates acoustic warmth rather than a flat electronic beep.",
         "Implemented in melodyloop/audio.py:57-61."),

        ("Q47: Why is peak normalization applied to the audio waveform?",
         "To prevent digital clipping distortion when multiple notes sound simultaneously.",
         "The master audio buffer is scaled so its maximum absolute value equals 0.90 (-0.9 dBFS).",
         "Implemented in melodyloop/audio.py:77-79."),

        ("Q48: What is 16-bit PCM audio?",
         "Pulse Code Modulation where each audio sample is a signed 16-bit integer (-32,768 to +32,767).",
         "It is the universal standard for uncompressed CD-quality digital audio.",
         "Implemented in melodyloop/audio.py:82."),

        # --- Topic 6: System Design, Testing & Viva Traps ---
        ("Q49: Why is the project split into separate modules (audio, data, model, generation)?",
         "To enforce separation of concerns, modular testability, and clean code maintainability.",
         "Model architecture is decoupled from data ingestion, enabling unit tests to verify components independently.",
         "See Chapter 4 and Chapter 14."),

        ("Q50: What unit tests did you implement, and what do they verify?",
         "12 unit tests across test_data.py, test_generation.py, and test_model.py.",
         "They verify quantization roundtrips, synthetic MIDI parsing, tensor dimensions, finite loss, top-k sampling, and audio synthesis.",
         "Verified via pytest in Chapter 15."),

        ("Q51: What is a smoke test?",
         "A fast, 1-epoch execution on minimal data (2 files) to verify that code runs end-to-end without crashing.",
         "MelodyLoop includes a --smoke-test flag in train.py.",
         "Implemented in train.py:202-209."),

        ("Q52: What happens if a saved checkpoint is corrupted?",
         "torch.load() raises an exception, which generate.py and app.py catch, falling back gracefully to latest_model.pt or notifying the user.",
         "Trained weights are decoupled from the code, preventing system-level crashes.",
         "Implemented in generate.py:34-40."),

        ("Q53: Why does Streamlit cache the MAESTRO catalog?",
         "To prevent scanning 1,276 CSV rows on every UI button click.",
         "@st.cache_data memoizes the catalog in RAM, keeping UI interactions instant.",
         "Implemented in app.py:110."),

        ("Q54: If you had another month, what would you improve?",
         "Implement relative positional self-attention (Music Transformer) and REMI tokenization.",
         "This would expand the context window to 2,048 tokens and enable multi-track polyphony.",
         "See Chapter 16.6."),

        ("Q55: What is the single biggest lesson you learned from this project?",
         "That low cross-entropy loss does not automatically equate to good musical composition.",
         "Local probability optimization must be paired with constrained sampling strategies (temperature, top-k, interval penalties) to produce human-pleasing art.",
         "See Chapter 1.7 and Chapter 16.2.")
    ]

    for q, direct_ans, detailed_ans, code_ref in viva_qas:
        q_p = Paragraph(f"<b>{q}</b>", styles["SubSectionHeading"])
        a1_p = Paragraph(f"<b>Direct Answer:</b> {direct_ans}", styles["BodyDarkBold"])
        a2_p = Paragraph(f"<b>Technical Explanation:</b> {detailed_ans}", styles["BodyDark"])
        a3_p = Paragraph(f"<b>Code & Reference:</b> <font face='Courier'>{code_ref}</font>", styles["TableCell"])
        story.append(KeepTogether([q_p, a1_p, a2_p, a3_p, Spacer(1, 4)]))

    story.append(PageBreak())


def build_chapter_20(story, styles):
    story.append(Paragraph("Chapter 20 — Presentation and Revision Material", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph("20.1 Presentation Scripts for Examiners", styles["SectionHeading"]))

    story.append(Paragraph("A. Two-Minute Viva Presentation Script", styles["SubSectionHeading"]))
    story.append(make_callout(
        "<i>'Good morning, respected examiners. My project is MelodyLoop, an educational machine-learning system for AI music generation.<br/><br/>"
        "The core problem we address is sequence modeling in creative domains. While modern commercial models use massive audio transformers, "
        "MelodyLoop demonstrates that transparent symbolic music generation can be trained from scratch on consumer hardware.<br/><br/>"
        "We utilize Google Magenta's MAESTRO dataset—a collection of 1,276 virtuoso classical piano performances recorded on Yamaha Disklavier pianos. "
        "Our preprocessing pipeline parses Standard MIDI files, sorts notes chronologically, and quantizes continuous duration and timing values "
        "into 32 discrete bins. Each note is represented as a 3-tuple: pitch, duration, and step to next note.<br/><br/>"
        "Our model, MelodyLSTM, has 167,104 parameters. It passes sequences through three learned embedding layers, a 128-unit recurrent LSTM layer, "
        "and three parallel linear heads that predict the next note's pitch, duration, and step. We trained it on an NVIDIA RTX 3050 GPU for 9 epochs "
        "using Adam and multi-task cross-entropy loss. Our optimal checkpoint achieved a validation loss of 6.1791 at Epoch 4.<br/><br/>"
        "To generate music, we implemented autoregressive rollout with temperature scaling, top-k filtering, and repetition penalties. "
        "Finally, we built a zero-dependency additive synthesizer that combines fundamental frequencies with piano harmonics to produce 16-bit WAV audio, "
        "served through an interactive Streamlit web application. All 12 unit tests pass cleanly. I welcome your questions.'</i>",
        title="2-MINUTE VIVA PRESENTATION SCRIPT",
        alert_type="tip",
        styles=styles
    ))

    story.append(Paragraph("B. Five-Minute Deep Technical Walkthrough", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "When examiners request an in-depth chronological technical walkthrough, follow this ordered 5-stage narrative:",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "1. <b>Data Ingestion:</b> 'We ingest MAESTRO v3.0 via <font face='Courier'>melodyloop/data.py</font>. We read <font face='Courier'>maestro-v3.0.0.csv</font>, "
        "filter for official train splits, and parse MIDI messages using Mido with safe hanging note resolution.'<br/>"
        "2. <b>Representation & Quantization:</b> 'Notes are sorted by onset time. Continuous durations ($0.05-4.0s$) and steps ($0.0-2.0s$) are mapped into 32 bins. "
        "We slide a window of 32 notes with stride 4, constructing input tensors $X \\in \\mathbb{R}^{B \\times 32 \\times 3}$ and targets $y \\in \\mathbb{R}^{B \\times 3}$.'<br/>"
        "3. <b>Neural Computation:</b> 'In <font face='Courier'>melodyloop/model.py</font>, tokens pass through embedding layers ($64+32+32=128$), "
        "enter a PyTorch LSTM cell with 128 hidden units, and branch into 3 linear heads. Multi-task cross-entropy loss is computed and backpropagated.'<br/>"
        "4. <b>Training Dynamics:</b> 'In <font face='Courier'>train.py</font>, we optimize using Adam with gradient clipping at 1.0. Our RTX 3050 trained across "
        "15,000 sequences, achieving peak validation loss of 6.1791 at Epoch 4 before early stopping at Epoch 9.'<br/>"
        "5. <b>Inference & Synthesis:</b> 'In <font face='Courier'>melodyloop/generation.py</font> and <font face='Courier'>audio.py</font>, we load <font face='Courier'>best_model.pt</font>, "
        "prompt with classical cadence or real seeds, apply top-k ($K=5$) and temperature ($T=0.6$) sampling, export standard MIDI, and synthesize 16-bit 44.1 kHz PCM audio.'",
        styles["BodyDark"]
    ))

    story.append(Paragraph("20.2 Important Formulas Cheat Sheet", styles["SectionHeading"]))
    formulas_data = [
        ["Formula Name", "Mathematical Expression", "MelodyLoop Code Location"],
        ["Pitch to Frequency", "f(p) = 440.0 * 2^((p - 69.0) / 12.0)", "melodyloop/audio.py:44"],
        ["Linear Quantization", "idx = round( ((val - min) / (max - min)) * (bins - 1) )", "melodyloop/data.py:34"],
        ["Forget Gate", "f_t = sigma( W_f * [h_{t-1}, x_t] + b_f )", "PyTorch LSTM Core"],
        ["Cell State Update", "C_t = f_t odot C_{t-1} + i_t odot C_tilde", "PyTorch LSTM Core"],
        ["Hidden State Output", "h_t = o_t odot tanh( C_t )", "PyTorch LSTM Core"],
        ["Multi-Task Loss", "L_total = L_pitch + L_duration + L_step", "melodyloop/model.py:97"],
        ["Softmax Temperature", "P_i = exp(z_i / T) / sum_j( exp(z_j / T) )", "melodyloop/generation.py:70"],
        ["Additive Harmonics", "wave = 0.60*sin(2*pi*f*t) + 0.25*sin(4*pi*f*t) + 0.15*sin(6*pi*f*t)", "melodyloop/audio.py:57-61"],
        ["ADSR Exponential Decay", "env(t) = exp( -3.0 * t / duration )", "melodyloop/audio.py:65"],
    ]
    story.append(make_styled_table(formulas_data, [110, 240, 170], styles=styles))

    story.append(Paragraph("20.3 Verified Hyperparameter and Constants Quick Reference", styles["SectionHeading"]))
    hyper_data = [
        ["Hyperparameter / Constant", "Verified Value", "Architectural Rationale"],
        ["Pitch Vocabulary Size", "128", "Full 7-bit MIDI specification compass (0-127)."],
        ["Duration Bins", "32", "Logarithmic resolution from thirty-second notes (0.05s) to whole notes (4.0s)."],
        ["Step (IOI) Bins", "32", "Captures chords (0.0s) up to inter-phrase rests (2.0s)."],
        ["Input Sequence Length", "32 note events", "Balances temporal context horizon (~8s) with GPU memory limits."],
        ["Sliding Window Stride", "4 events", "Augments sequence diversity while bounding total memory allocation."],
        ["Pitch Embedding Dimension", "64", "Sufficient latent capacity to encode 12-tone chromatic harmonic relationships."],
        ["Duration / Step Embed Dim", "32 each", "Compact latent projections matching the 32 discrete categorical bins."],
        ["LSTM Hidden Dimension", "128 units", "Single-layer recurrent capacity yielding exactly 167,104 total parameters."],
        ["Dropout Probability", "0.1 (10%)", "Prevents co-adaptation on the dense recurrent output vector."],
        ["Batch Size", "32 (CUDA) / 16 (CPU)", "Optimized for 4 GB VRAM GPU throughput without out-of-memory errors."],
        ["Learning Rate / Weight Decay", "1e-3 / 1e-5", "Adam optimizer standard convergence parameters with L2 regularization."],
        ["Default Sampling Temp", "0.60", "Empirically determined sweet-spot for melodic coherence."],
        ["Top-K Candidate Pool", "K = 5", "Strictly eliminates discordant, out-of-key tail selections."],
        ["Audio Sampling Rate", "44,100 Hz (16-bit)", "Standard CD-quality PCM audio meeting the Nyquist-Shannon criterion."],
    ]
    story.append(make_styled_table(hyper_data, [130, 110, 280], styles=styles))

    story.append(Paragraph("20.4 Ten Critical Viva Traps and How to Avoid Them", styles["SectionHeading"]))
    traps_data = [
        ["Viva Trap", "The Danger / Misconception", "How to Answer Correctly Without Losing Marks"],
        ["Calling MIDI 'Audio'", "Claiming MIDI files contain recorded sound.", "State firmly: 'MIDI contains zero audio. It is symbolic digital choreography that must be rendered via a synthesizer.'"],
        ["Exaggerating Training Size", "Claiming you trained on all 1,276 MAESTRO files.", "State accurately: 'We trained across a balanced sample of 13 files and 15,000 sequences to respect RAM and laptop compute limits.'"],
        ["Equating Low Loss to Quality", "Assuming validation loss proves music sounds great.", "Clarify: 'Cross-entropy measures next-step accuracy, not global harmonic aesthetics or phrase symmetry.'"],
        ["88 Keys vs. 128 MIDI Notes", "Confusing piano compass with MIDI range.", "Explain: 'A piano has 88 keys (pitches 21-108); MIDI has 128 numbers (0-127) due to its 7-bit protocol.'"],
        ["Claiming Pretrained Models", "Claiming transfer learning from HuggingFace.", "State clearly: 'MelodyLoop is trained from scratch with randomly initialized weights for full educational transparency.'"],
        ["Confusing Training & Generation", "Mixing up model training with autoregression.", "Explain: 'Training is parallelized next-token prediction; generation is sequential autoregressive rollout with sampling.'"],
        ["Unverified Transformer Claims", "Claiming the model uses attention or transformers.", "Affirm: 'MelodyLoop uses a classical PyTorch LSTM recurrent cell; transformers are part of our future roadmap.'"],
        ["Checkpoints as 'Models'", "Claiming .pt is a pickled Python class.", "Explain: 'It is a state_dict dictionary containing tensor weights, optimizer state, and hyperparameter configuration.'"],
        ["Passing Tests as Aesthetics", "Claiming passing tests mean the music is beautiful.", "Clarify: 'Unit tests prove numerical stability, shape integrity, and format adherence, not human artistic quality.'"],
        ["Inventing Unknown Facts", "Guessing parameters not present in the code.", "Demonstrate integrity: 'State clearly if a parameter is an empirical default versus a measured ground truth.'"],
    ]
    story.append(make_styled_table(traps_data, [95, 150, 275], styles=styles))

    story.append(Paragraph("20.5 Comprehensive Technical Glossary (35 Terms Defined)", styles["SectionHeading"]))
    glossary_data = [
        ["Technical Term", "Formal Definition in MelodyLoop Context"],
        ["Additive Synthesis", "Constructing sound waveforms by summing fundamental sine waves and harmonic partials."],
        ["ADSR Envelope", "Attack-Decay-Sustain-Release profile shaping amplitude over physical time."],
        ["Autoregressive Rollout", "Iterative generation where previously predicted tokens are fed back as future inputs."],
        ["Backpropagation Through Time", "Unrolling an RNN across time steps to compute parameter loss gradients."],
        ["Cell State (C_t)", "The internal linear highway of an LSTM that preserves memory without vanishing gradients."],
        ["Categorical Cross-Entropy", "Loss function measuring difference between predicted probability distributions and target classes."],
        ["Concert A (A4)", "The international pitch standard (440.0 Hz), corresponding to MIDI pitch 69."],
        ["Delta Time", "The number of MIDI clock ticks to wait before executing the next musical event."],
        ["Dequantization", "Converting discrete integer bin indices back into continuous physical seconds."],
        ["Dropout", "Regularization technique randomly zeroing tensor activations to prevent neural co-adaptation."],
        ["Embedding Layer", "A lookup table mapping high-cardinality discrete tokens into dense continuous vector spaces."],
        ["Forget Gate (f_t)", "Sigmoidal gate in an LSTM cell controlling the proportion of prior cell memory to erase."],
        ["Fundamental Frequency (f_0)", "The lowest frequency vibration of a periodic waveform, determining perceived pitch."],
        ["Hadamard Product (odot)", "Element-wise multiplication of two matrices or vectors of identical shape."],
        ["Harmonics / Overtones", "Integer multiples of the fundamental frequency (2f_0, 3f_0) creating acoustic timbre."],
        ["Hidden State (h_t)", "The working memory vector output by an LSTM cell at time step t."],
        ["Inter-Onset Interval (Step)", "The physical time elapsed between the start of one note and the start of the next."],
        ["Linear Quantization", "Discretizing continuous floating-point ranges into fixed-width integer bins."],
        ["Logits", "Unnormalized raw real-valued output scores emitted by linear prediction heads."],
        ["MAESTRO", "MIDI and Audio Edited for Synchronous TRacks and Organization (benchmark piano dataset)."],
        ["Middle C (C4)", "The central musical pitch reference point, corresponding to MIDI note number 60 (261.63 Hz)."],
        ["MIDI", "Musical Instrument Digital Interface (7-bit symbolic musical event communication standard)."],
        ["Mido", "Pure Python library for reading, manipulating, and writing Standard MIDI files."],
        ["Multi-Task Learning", "Jointly training a shared neural representation to predict multiple targets simultaneously."],
        ["Nyquist-Shannon Theorem", "Sampling theorem requiring a sample rate > 2x highest frequency to prevent aliasing."],
        ["Octave", "Musical interval representing an exact doubling (2:1) of sound frequency."],
        ["PCM (Pulse Code Modulation)", "Uncompressed digital representation of analog audio via discrete amplitude samples."],
        ["Pitch", "Perceived sound frequency, mapped in MIDI to integers from 0 to 127."],
        ["Repetition Penalty", "Dampening logits of recently generated tokens to avoid repetitive note looping."],
        ["Seeded Continuation", "Prompting an autoregressive model with human opening bars to predict continuation."],
        ["Sequence Stride", "The step displacement when sliding a temporal window across sequential data."],
        ["Standard MIDI File (.mid)", "Binary file format containing timed MIDI tracks, tempo maps, and note events."],
        ["Temperature", "Scalar hyperparameter dividing logits to control entropy/randomness during softmax sampling."],
        ["Top-K Sampling", "Restricting sampling exclusively to the K most probable candidate tokens."],
        ["Velocity", "MIDI parameter (0-127) indicating key strike speed, perceived as acoustic loudness."],
    ]
    story.append(make_styled_table(glossary_data, [130, 390], styles=styles))

    story.append(Spacer(1, 10))
    story.append(make_callout(
        "<b>DOCUMENTATION CONCLUDED:</b> This document serves as the complete, authoritative technical guide and viva defense "
        "dossier for <b>MelodyLoop — Music Generation Using an LSTM</b>. All code, data representations, parameter counts, "
        "and training trajectories reflect the live, working repository audited on October 28, 2026.",
        title="FINAL VIVA VERIFICATION CERTIFICATE",
        alert_type="note",
        styles=styles
    ))

print("Chapters 16-20 module compiled.")
