"""
MelodyLoop Documentation Guide — Chapters 6 to 10 Builder
Contains:
- Chapter 6: The Complete Data Preprocessing Pipeline (data.py)
- Chapter 7: Why an LSTM, and How It Works Mathematically
- Chapter 8: The Actual Model Architecture in model.py
- Chapter 9: Training the Model (train.py, config.py, real log audit)
- Chapter 10: Understanding .pt Checkpoints
"""

from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, PageBreak, HRFlowable, KeepTogether, Table, TableStyle
from pdf_builder_helpers import make_callout, make_code_panel, make_styled_table, make_figure

BLUE_ACCENT = colors.HexColor("#1e40af")


def build_chapter_6(story, styles):
    story.append(Paragraph("Chapter 6 — The Complete Data Preprocessing Pipeline", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph("6.1 Architectural Execution Order in melodyloop/data.py", styles["SectionHeading"]))
    story.append(Paragraph(
        "Data preprocessing is the foundational pillar of the MelodyLoop system. The implementation in "
        "<font face='Courier'>melodyloop/data.py</font> transforms raw, unconstrained Standard MIDI files into clean, "
        "quantized, fixed-dimension PyTorch tensors ready for recurrent sequence modeling. The pipeline executes in "
        "a strict 5-stage chronological order:",
        styles["BodyDark"]
    ))

    story.append(make_figure("fig4_preprocessing_pipeline.png", "Step-by-Step Data Preprocessing, Quantization, and Sliding Window Sequence Assembly", width=510, height=170, styles=styles))

    story.append(Paragraph("6.2 Stage 1: Dataset Ingestion and Discovery", styles["SectionHeading"]))
    story.append(Paragraph(
        "The process begins in <font face='Courier'>load_maestro_split(split_name, cfg)</font> (<font face='Courier'>data.py:177</font>). "
        "The function loads the metadata catalog from <font face='Courier'>cfg.csv_path</font> via Pandas, filters rows matching the requested "
        "split partition ('train' or 'validation'), and caps the file count using <font face='Courier'>cfg.max_train_files</font> (defaults to 25 "
        "or CLI override). If a target MIDI file is missing or unreadable, it is logged and gracefully skipped without terminating execution.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("6.3 Stage 2: Robust MIDI Parsing with Mido", styles["SectionHeading"]))
    story.append(Paragraph(
        "Individual MIDI performances are parsed in <font face='Courier'>parse_midi_file(filepath, cfg)</font> (<font face='Courier'>data.py:60</font>). "
        "The parser instantiates <font face='Courier'>mido.MidiFile(str(path), clip=True)</font>. The <font face='Courier'>clip=True</font> flag "
        "guarantees that any out-of-range MIDI byte values caused by corrupted files are clipped into valid ranges. "
        "The parser maintains a cumulative timer (<font face='Courier'>current_time += msg.time</font>) and an active notes dictionary:",
        styles["BodyDark"]
    ))
    story.append(make_code_panel("""active_notes: Dict[int, List[float]] = {}
for msg in mid:
    current_time += getattr(msg, "time", 0.0)
    if msg.type == "note_on" and msg.velocity > 0:
        active_notes.setdefault(msg.note, []).append(current_time)
    elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
        if msg.note in active_notes and active_notes[msg.note]:
            start_time = active_notes[msg.note].pop(0)
            dur = max(cfg.min_duration, current_time - start_time)
            raw_notes.append({"pitch": msg.note, "start": start_time, "duration": dur})""", styles=styles))
    story.append(Paragraph(
        "<b>Handling Dangling Notes:</b> In imperfect MIDI recordings, a pianist may hold a pedal or release a key after the track ends. "
        "MelodyLoop includes an explicit safety sweep (<font face='Courier'>data.py:98-107</font>) that iterates through any unclosed notes in "
        "<font face='Courier'>active_notes</font> and closes them safely, ensuring zero dropped note events.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("6.4 Stage 3: Chronological Sorting and Step Calculation", styles["SectionHeading"]))
    story.append(Paragraph(
        "A piano piece can contain multiple simultaneous voices (left-hand accompaniment and right-hand melody). "
        "To enforce a consistent sequential order, all extracted notes are sorted chronologically by start time, breaking ties by pitch:<br/>"
        "<font face='Courier'>raw_notes.sort(key=lambda n: (n['start'], n['pitch']))</font><br/>"
        "Once sorted, the <b>Step (Inter-Onset Interval)</b> to the subsequent note is computed:<br/>"
        "<font face='Courier'>step = max(0.0, raw_notes[i + 1]['start'] - n['start'])</font><br/>"
        "For simultaneous notes (chords), <font face='Courier'>step = 0.0</font> seconds. For the final note of a performance, a default "
        "cadence step of 0.25 seconds is appended.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("6.5 Stage 4: Mathematical Quantization into Categorical Bins", styles["SectionHeading"]))
    story.append(Paragraph(
        "Continuous physical time values (e.g. 0.38472 seconds) cannot be directly classified by categorical cross-entropy. "
        "MelodyLoop quantizes continuous duration and step values into <b>32 discrete integer bins</b> using linear binning:",
        styles["BodyDark"]
    ))
    story.append(make_code_panel("""def quantize_value(val: float, min_val: float, max_val: float, num_bins: int) -> int:
    clipped = min(max(val, min_val), max_val)
    normalized = (clipped - min_val) / max(max_val - min_val, 1e-6)
    idx = int(normalized * (num_bins - 1) + 0.5)
    return min(max(idx, 0), num_bins - 1)""", styles=styles))
    story.append(Paragraph(
        "• <b>Duration Range:</b> <font face='Courier'>min_duration = 0.05s</font> (thirty-second note) to <font face='Courier'>max_duration = 4.0s</font> (whole note) $\\to$ 32 bins.<br/>"
        "• <b>Step Range:</b> <font face='Courier'>min_step = 0.0s</font> (chord) to <font face='Courier'>max_step = 2.0s</font> (inter-phrase pause) $\\to$ 32 bins.<br/>"
        "• <b>Pitch Range:</b> Kept as discrete integers in $[0, 127]$ (128 categories).<br/>"
        "Every note is thus compressed into a compact 3-tuple: <font face='Courier'>(pitch_idx, duration_bin, step_bin)</font>.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("6.6 Stage 5: Sliding-Window Sequence and Target Generation", styles["SectionHeading"]))
    story.append(Paragraph(
        "In <font face='Courier'>create_sequences_from_events()</font> (<font face='Courier'>data.py:132</font>), the chronological list "
        "of note tuples is converted into supervised training pairs using a sliding window of length 32 and stride 4:",
        styles["BodyDark"]
    ))
    story.append(make_code_panel("""for i in range(0, len(events) - seq_length, stride):
    xs.append(events[i : i + seq_length])    # Shape: (32, 3)
    ys.append(events[i + seq_length])        # Shape: (3,) -- Next Note!""", styles=styles))
    story.append(Paragraph(
        "<b>Sequence Balancing:</b> To prevent a single 40-minute Liszt transcendental etude from monopolizing the entire dataset buffer, "
        "<font face='Courier'>load_maestro_split()</font> computes <font face='Courier'>max_per_file</font> and evenly samples sequences across "
        "the performance using <font face='Courier'>np.linspace()</font> (<font face='Courier'>data.py:224</font>).",
        styles["BodyDark"]
    ))

    story.append(PageBreak())


def build_chapter_7(story, styles):
    story.append(Paragraph("Chapter 7 — Why an LSTM, and How It Works Mathematically", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph("7.1 The Fundamental Challenge of Sequential Modeling", styles["SectionHeading"]))
    story.append(Paragraph(
        "Standard feedforward neural networks possess no internal state; they process each input vector in complete isolation. "
        "A basic Recurrent Neural Network (RNN) introduces a recurrent loop: at each step $t$, the network computes a new hidden state "
        "$h_t$ as a function of the current input $x_t$ and the previous hidden state $h_{t-1}$:",
        styles["BodyDark"]
    ))
    story.append(make_code_panel("h_t = tanh(W_hh * h_{t-1} + W_xh * x_t + b_h)", styles=styles))

    story.append(Paragraph("7.2 The Vanishing and Exploding Gradient Problem", styles["SectionHeading"]))
    story.append(Paragraph(
        "When training a standard RNN over sequences of length 32 via <b>Backpropagation Through Time (BPTT)</b>, calculating the gradient "
        "of the loss $L$ with respect to the initial hidden state $h_0$ requires computing the product of 32 Jacobian matrices: "
        "$\\prod_{j=1}^{32} \\frac{\\partial h_j}{\\partial h_{j-1}} = \\prod_{j=1}^{32} W_{hh}^T \\text{diag}(1 - \\tanh^2(\\dots))$. "
        "If the eigenvalues of $W_{hh}$ are smaller than 1.0, the gradient exponentially decays to zero ($0.8^{32} \\approx 0.00079$), "
        "causing the network to completely fail to learn dependencies beyond 5 or 6 notes. Conversely, if eigenvalues exceed 1.0, "
        "gradients explode, destabilizing training.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("7.3 The LSTM Solution: The Constant Error Carousel", styles["SectionHeading"]))
    story.append(Paragraph(
        "Invented by Hochreiter and Schmidhuber (1997), the <b>Long Short-Term Memory (LSTM)</b> network overcomes the vanishing gradient "
        "by separating the internal state into two distinct vectors: the <b>Hidden State $h_t$</b> (working memory) and the "
        "<b>Cell State $C_t$</b> (long-term memory highway). The cell state operates with <i>additive linear updates</i>, allowing gradients "
        "to flow backward through time with virtually zero exponential decay.",
        styles["BodyDark"]
    ))

    story.append(make_figure("fig5_lstm_cell_math.png", "Detailed LSTM Cell Gate Formulations and Linear Cell State Highway", width=510, height=190, styles=styles))

    story.append(Paragraph("7.4 Step-by-Step Mathematical Formulations of the Four Gates", styles["SectionHeading"]))
    story.append(Paragraph(
        "At each discrete musical time step $t$, the LSTM executes the following 6 mathematical operations:",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "<b>1. Forget Gate ($f_t$):</b> Decides what fraction of existing musical context to erase.<br/>"
        "$$f_t = \\sigma(W_f \\cdot [h_{t-1}, x_t] + b_f)$$<br/>"
        "The logistic sigmoid function $\\sigma(z) = \\frac{1}{1 + e^{-z}}$ squashes values between 0.0 (completely forget) and 1.0 (completely remember). "
        "For example, at the end of a musical cadence, $f_t$ drops close to 0 to flush out the old harmonic key.",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "<b>2. Input Gate ($i_t$):</b> Decides which new musical information to write into memory.<br/>"
        "$$i_t = \\sigma(W_i \\cdot [h_{t-1}, x_t] + b_i)$$",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "<b>3. Candidate Cell State ($\\tilde{C}_t$):</b> Generates candidate musical facts.<br/>"
        "$$\\tilde{C}_t = \\tanh(W_c \\cdot [h_{t-1}, x_t] + b_c)$$<br/>"
        "The hyperbolic tangent $\\tanh(z) = \\frac{e^z - e^{-z}}{e^z + e^{-z}}$ bounds values in $[-1.0, +1.0]$.",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "<b>4. Cell State Update ($C_t$):</b> The core linear highway update.<br/>"
        "$$C_t = f_t \\odot C_{t-1} + i_t \\odot \\tilde{C}_t$$<br/>"
        "where $\\odot$ represents the <b>Hadamard (element-wise) product</b>. Notice that $C_{t-1}$ is altered via addition, not matrix multiplication!",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "<b>5. Output Gate ($o_t$):</b> Decides which parts of the cell state to reveal as output.<br/>"
        "$$o_t = \\sigma(W_o \\cdot [h_{t-1}, x_t] + b_o)$$",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "<b>6. Hidden State Vector ($h_t$):</b> The resulting output passed to the next layer and prediction heads.<br/>"
        "$$h_t = o_t \\odot \\tanh(C_t)$$",
        styles["BodyDark"]
    ))

    story.append(PageBreak())


def build_chapter_8(story, styles):
    story.append(Paragraph("Chapter 8 — The Actual Model Architecture in model.py", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph("8.1 Full Dissection of the MelodyLSTM Class", styles["SectionHeading"]))
    story.append(Paragraph(
        "The neural architecture is implemented in <font face='Courier'>melodyloop/model.py</font> as a multi-task recurrent network. "
        "It takes a sequence of quantized 3-tuples and outputs three independent probability distributions for the next event's "
        "pitch, duration, and step.",
        styles["BodyDark"]
    ))

    story.append(make_figure("fig6_model_architecture.png", "MelodyLSTM Multi-Task Neural Network Architecture and Layer Dimensionality", width=510, height=180, styles=styles))

    story.append(Paragraph("8.2 Dedicated Embedding Layers", styles["SectionHeading"]))
    story.append(Paragraph(
        "Rather than treating pitch, duration, and step as arbitrary raw integers, MelodyLoop maps each discrete token into a continuous, "
        "learnable geometric vector space via <font face='Courier'>nn.Embedding</font> layers (<font face='Courier'>model.py:24-26</font>):<br/>"
        "• <font face='Courier'>pitch_embed = nn.Embedding(128, 64)</font>: Maps 128 MIDI pitches to 64-dimensional vectors.<br/>"
        "• <font face='Courier'>duration_embed = nn.Embedding(32, 32)</font>: Maps 32 duration bins to 32-dimensional vectors.<br/>"
        "• <font face='Courier'>step_embed = nn.Embedding(32, 32)</font>: Maps 32 step bins to 32-dimensional vectors.<br/>"
        "The three embeddings are concatenated along the feature axis: $64 + 32 + 32 = \\mathbf{128}$ total input dimensions.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("8.3 Recurrent Core and Multi-Task Linear Heads", styles["SectionHeading"]))
    story.append(Paragraph(
        "The concatenated vector sequence $[B, 32, 128]$ enters the recurrent core:<br/>"
        "• <font face='Courier'>self.lstm = nn.LSTM(input_size=128, hidden_size=128, num_layers=1, batch_first=True)</font><br/>"
        "The output of the final time step ($t=32$) is extracted: <font face='Courier'>last_out = dropout(out[:, -1, :])</font>. "
        "This 128-dimensional context vector branches into three parallel linear classification heads:<br/>"
        "1. <font face='Courier'>head_pitch = nn.Linear(128, 128)</font> $\\to$ 128 raw pitch logits.<br/>"
        "2. <font face='Courier'>head_duration = nn.Linear(128, 32)</font> $\\to$ 32 duration logits.<br/>"
        "3. <font face='Courier'>head_step = nn.Linear(128, 32)</font> $\\to$ 32 step logits.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("8.4 Rigorous Mathematical Parameter Count Breakdown", styles["SectionHeading"]))
    story.append(Paragraph(
        "Examiners frequently ask: <i>'Prove how your model has exactly 167,104 parameters.'</i> "
        "Here is the line-by-line algebraic proof:",
        styles["BodyDark"]
    ))

    param_table_data = [
        ["Sub-Module / Layer", "Layer Dimensions", "Formula", "Weight Params", "Bias Params", "Total Parameters"],
        ["pitch_embed", "Embedding(128, 64)", "128 * 64", "8,192", "0", "8,192"],
        ["duration_embed", "Embedding(32, 32)", "32 * 32", "1,024", "0", "1,024"],
        ["step_embed", "Embedding(32, 32)", "32 * 32", "1,024", "0", "1,024"],
        ["lstm (1 layer)", "Input=128, Hidden=128", "4 * (W_ih + W_hh + b_ih + b_hh)", "131,072", "1,024", "132,096"],
        ["head_pitch", "Linear(128, 128)", "128 * 128 + 128", "16,384", "128", "16,512"],
        ["head_duration", "Linear(128, 32)", "128 * 32 + 32", "4,096", "32", "4,128"],
        ["head_step", "Linear(128, 32)", "128 * 32 + 32", "4,096", "32", "4,128"],
        ["Grand Total", "All Trainable Parameters", "Sum of all weights + biases", "165,888", "1,216", "167,104"],
    ]
    story.append(make_styled_table(param_table_data, [95, 95, 120, 70, 65, 75], styles=styles))

    story.append(Paragraph("8.5 Multi-Task Loss Formulation", styles["SectionHeading"]))
    story.append(Paragraph(
        "In <font face='Courier'>model.compute_loss()</font> (<font face='Courier'>model.py:82</font>), the network calculates the sum of three "
        "independent categorical cross-entropy losses:<br/>"
        "$$\\mathcal{L}_{total} = \\mathcal{L}_{pitch}(z_p, y_p) + \\mathcal{L}_{duration}(z_d, y_d) + \\mathcal{L}_{step}(z_s, y_s)$$<br/>"
        "where each cross-entropy loss is given by $\\mathcal{L}_{CE} = -\\log \\left( \\frac{e^{z_{target}}}{\\sum_j e^{z_j}} \\right)$. "
        "This forces the shared LSTM backbone to jointly optimize musical pitch transitions and rhythmic timing simultaneously.",
        styles["BodyDark"]
    ))

    story.append(PageBreak())


def build_chapter_9(story, styles):
    story.append(Paragraph("Chapter 9 — Training the Model", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph("9.1 The Training Loop in train.py", styles["SectionHeading"]))
    story.append(Paragraph(
        "Model training is managed by <font face='Courier'>train.py</font>. The script initializes the configuration, checks device availability "
        "(CUDA if available, else CPU), instantiates DataLoaders with <font face='Courier'>pin_memory=True</font> for fast GPU transfer, "
        "and optimizes model weights using the <b>Adam optimizer</b> with gradient norm clipping to prevent gradient explosion:",
        styles["BodyDark"]
    ))
    story.append(make_code_panel("""optimizer.zero_grad()
logits_p, logits_d, logits_s, _ = model(x)
loss, _ = model.compute_loss(logits_p, logits_d, logits_s, t_p, t_d, t_s)
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()""", styles=styles))

    story.append(Paragraph("9.2 Verified Live Training Run Audit (training.log)", styles["SectionHeading"]))
    story.append(Paragraph(
        "An inspection of the workspace training log (<font face='Courier'>artifacts/logs/training.log</font>) confirms the exact training "
        "run that produced the active production checkpoints:",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "• <b>Hardware Device:</b> NVIDIA GeForce RTX 3050 Laptop GPU (CUDA).<br/>"
        "• <b>Optimizer:</b> Adam (<font face='Courier'>learning_rate = 0.001, weight_decay = 1e-5</font>).<br/>"
        "• <b>Batch Size:</b> 32 | <b>Sequence Length:</b> 32 events.<br/>"
        "• <b>Data Volume:</b> 13 MAESTRO files processed (64,261 notes), 15,000 training sequences, 3,924 validation sequences.<br/>"
        "• <b>Execution:</b> Ran for 9 epochs (average 16-29 seconds per epoch).<br/>"
        "• <b>Early Stopping:</b> Triggered at Epoch 9 after validation loss failed to improve for 5 consecutive epochs.",
        styles["BodyDark"]
    ))

    story.append(make_figure("fig7_training_loss.png", "Empirical Multi-Task Training and Validation Loss Curves Across 9 Epochs", width=510, height=170, styles=styles))

    story.append(Paragraph("9.3 Epoch-by-Epoch Empirical Loss Trajectory Table", styles["SectionHeading"]))
    story.append(Paragraph(
        "The following table records the exact, verified loss metrics extracted directly from <font face='Courier'>training.log</font>:",
        styles["BodyDark"]
    ))

    epoch_log_data = [
        ["Epoch", "Train Loss", "Val Loss Total", "Val Pitch Loss", "Val Duration Loss", "Val Step Loss", "Status / Checkpoint Event"],
        ["Epoch 01", "7.2235", "6.5465", "4.068", "0.975", "1.503", "New Best Model Saved -> best_model.pt"],
        ["Epoch 02", "6.7738", "6.4248", "3.983", "0.962", "1.480", "New Best Model Saved -> best_model.pt"],
        ["Epoch 03", "6.5335", "6.3122", "3.888", "0.968", "1.456", "New Best Model Saved -> best_model.pt"],
        ["Epoch 04", "6.3327", "6.1791", "3.759", "0.965", "1.455", "★ OPTIMAL BEST MODEL ACHIEVED (Saved)"],
        ["Epoch 05", "6.1585", "6.2725", "3.812", "0.977", "1.484", "Patience Counter = 1 (No val improvement)"],
        ["Epoch 06", "5.9967", "6.2547", "3.812", "0.972", "1.471", "Patience Counter = 2"],
        ["Epoch 07", "5.8535", "6.2663", "3.812", "0.973", "1.482", "Patience Counter = 3"],
        ["Epoch 08", "5.7044", "6.3011", "3.824", "0.988", "1.488", "Patience Counter = 4"],
        ["Epoch 09", "5.3184", "6.2623", "3.766", "0.990", "1.507", "! Early Stopping Triggered (Patience = 5)"],
    ]
    story.append(make_styled_table(epoch_log_data, [45, 60, 70, 70, 80, 70, 125], styles=styles))

    story.append(Paragraph("9.4 Overfitting Analysis: What the Numbers Tell Us", styles["SectionHeading"]))
    story.append(Paragraph(
        "Notice the divergence after Epoch 4: the training loss continued to decrease sharply from <b>6.3327 down to 5.3184</b>, "
        "demonstrating that the model was memorizing subtle idiosyncrasies of the training pieces. However, the held-out validation loss "
        "stagnated around <b>6.25 - 6.30</b>. By implementing early stopping with a patience of 5 epochs, <font face='Courier'>train.py</font> "
        "prevented severe overfitting and successfully preserved the optimal generalized checkpoint from <b>Epoch 4</b>.",
        styles["BodyDark"]
    ))

    story.append(PageBreak())


def build_chapter_10(story, styles):
    story.append(Paragraph("Chapter 10 — Understanding .pt Checkpoints", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=BLUE_ACCENT, spaceAfter=8))

    story.append(Paragraph("10.1 Why Model Checkpoints Are Essential", styles["SectionHeading"]))
    story.append(Paragraph(
        "Training a neural network is computationally intensive. In production machine learning, training is decoupled from inference: "
        "the model is trained once, and its learned parameters are serialized to disk as a <b>checkpoint file</b>. When an end-user launches "
        "the Streamlit web app (<font face='Courier'>app.py</font>) or the generation CLI (<font face='Courier'>generate.py</font>), the system "
        "does not retrain the network. Instead, it reads the saved weights from disk in a few milliseconds and begins generating music immediately.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("10.2 Dissecting the Checkpoint Files in artifacts/checkpoints/", styles["SectionHeading"]))
    story.append(Paragraph(
        "The workspace contains two verified checkpoint files in <font face='Courier'>artifacts/checkpoints/</font>:",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "• <font face='Courier'>best_model.pt</font> (2,023,093 bytes): Saved at <b>Epoch 4</b>, representing the peak generalization performance "
        "with the lowest validation loss (<b>6.1791</b>). This is the checkpoint loaded by default in the web app.",
        styles["BulletText"]
    ))
    story.append(Paragraph(
        "• <font face='Courier'>latest_model.pt</font> (2,023,203 bytes): Saved at <b>Epoch 9</b>, capturing the state of the model and optimizer "
        "at the moment training terminated. This file enables seamless training resumption via <font face='Courier'>python train.py --resume</font>.",
        styles["BulletText"]
    ))

    story.append(Paragraph("10.3 Inspecting the Checkpoint Dictionary Payload", styles["SectionHeading"]))
    story.append(Paragraph(
        "Direct inspection of <font face='Courier'>best_model.pt</font> using PyTorch reveals the exact top-level keys stored inside:",
        styles["BodyDark"]
    ))
    story.append(make_code_panel("""# Checkpoint structure verified in artifacts/checkpoints/best_model.pt:
{
    'epoch': 4,
    'train_loss': 6.04455504322052,
    'val_loss': 6.1790929962606995,
    'metrics': {
        'val_loss': 6.1790929962606995,
        'val_loss_pitch': 3.7590411651034317,
        'val_loss_dur': 0.9647628733215212,
        'val_loss_step': 1.4552889481312086
    },
    'config': {
        'hidden_dim': 128, 'num_layers': 1, 'seq_length': 32,
        'pitch_vocab_size': 128, 'duration_bins': 32, 'step_bins': 32,
        'pitch_embed_dim': 64, 'duration_embed_dim': 32, 'step_embed_dim': 32,
        'dropout': 0.1, 'learning_rate': 0.001, 'batch_size': 32, ...
    },
    'model_state_dict': { ... 167,104 weight tensors ... },
    'optimizer_state_dict': { ... Adam momentum buffers ... },
    'timestamp': 1793116928.45
}""", styles=styles))

    story.append(Paragraph("10.4 Safe Loading and Architectural Consistency", styles["SectionHeading"]))
    story.append(Paragraph(
        "When loading a checkpoint, the code in <font face='Courier'>generate.py:46-55</font> executes a safe reconstruction pattern:",
        styles["BodyDark"]
    ))
    story.append(make_code_panel("""device = torch.device(cfg.device)
checkpoint = torch.load(str(ckpt_path), map_location=device)
saved_cfg = checkpoint.get("config", {})
if "hidden_dim" in saved_cfg:
    cfg.hidden_dim = saved_cfg["hidden_dim"]

model = MelodyLSTM(cfg).to(device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()""", styles=styles))
    story.append(Paragraph(
        "<b>Architectural Compatibility Rule:</b> PyTorch requires an exact match between the model class definition and the saved weights. "
        "If a developer alters <font face='Courier'>hidden_dim</font> from 128 to 256 in the code and attempts to load <font face='Courier'>best_model.pt</font>, "
        "PyTorch will throw a fatal <font face='Courier'>RuntimeError: Error(s) in loading state_dict: size mismatch</font>. "
        "MelodyLoop guarantees consistency by serializing the exact configuration inside the checkpoint dictionary itself.",
        styles["BodyDark"]
    ))

    story.append(PageBreak())

print("Chapters 6-10 module compiled.")
