# MelodyLoop — Professional Oral Defense & Speaker Notes

> **Project:** MelodyLoop — LSTM Music Generation  
> **Repository:** `https://github.com/Pankaj-Jhajhria/Music-Generation-using-LSTM-MelodyLoop-`  
> **Audience:** Academic Faculty Evaluation Panel & Technical Defense  
> **Theme:** Professional Academic Light/White Presentation Deck  
> **Scope:** 17-Slide Technical Walkthrough (In-depth oral presentation scripts, architectural proofs, and anticipated viva defense questions).

---

## Slide 01: Title Slide — MelodyLoop

```text
OPENING TALK:
Good morning, Professor and members of the evaluation committee. Today, I am presenting MelodyLoop, an end-to-end deep learning engineering project focused on symbolic piano music generation using a custom Long Short-Term Memory network.

CORE IDEA:
Rather than treating music as unstructured raw audio waveforms or static images, MelodyLoop formulates music as a discrete temporal sequence of structured musical events. The system trains an LSTM neural network from scratch on over 5.6 million note events extracted from 962 professional piano performances from Google Magenta's MAESTRO dataset.

KEY ENGINEERING MILESTONES:
- Scaled training across the entire official MAESTRO training split (962 performances, 100,000 sequences).
- Designed a compact uint8 tensor representation reducing RAM overhead by 8x on consumer hardware.
- Implemented multi-task prediction heads for pitch, duration, and time step, achieving a best validation loss of 5.9151 at epoch 7.
- Built an interactive Streamlit web dashboard with local additive harmonic synthesis for immediate audio evaluation.

TRANSITION:
Let us begin with the formal problem statement and our engineering objectives.
```

---

## Slide 02: Problem Formulation & Objectives

```text
SLIDE CONCEPT:
Here we define why symbolic music generation is an ideal sequence-modeling task and specify the exact engineering goals of MelodyLoop.

TECHNICAL EXPLANATION:
Music is inherently temporal and hierarchical. Unlike natural language processing where tokens are words or subwords, musical events have simultaneous attributes: which key is pressed (pitch), how long it is sustained (duration), and the temporal gap until the next event begins (step time).
If you predict only pitch, you lose rhythm and tempo completely. If you model raw waveform audio directly, 10 seconds of CD audio equals 441,000 samples, which creates prohibitive computational demands for educational sequence models. Symbolic event modeling provides the optimal balance of structured expressiveness and computational tractability.

TRANSITION:
Now let us examine the complete end-to-end system architecture that implements this pipeline.
```

---

## Slide 03: Complete End-to-End Workflow

```text
SLIDE CONCEPT:
This slide presents the entire MelodyLoop architecture from raw dataset to final playable audio.

TECHNICAL BREAKDOWN:
The system operates in three decoupled, production-grade phases:
1. Ingestion Phase: Handled by melodyloop/data.py. Reads MAESTRO MIDI files, extracts Note On/Off chronological events, quantizes durations and steps, and prepares bounded uint8 PyTorch Datasets.
2. Training Phase: Handled by train.py and melodyloop/model.py. Trains the 167k-parameter LSTM across 100,000 sequence batches, monitoring validation loss after every epoch and saving the best checkpoint.
3. Inference & Synthesis Phase: Handled by melodyloop/generation.py and audio.py. The model takes a seed buffer, iteratively samples successive notes, exports a standard MIDI file, and synthesizes a WAV preview using NumPy/SciPy.

TRANSITION:
Let us examine how acoustic piano notes are translated into numerical representations.
```

---

## Slide 04: Keyboard to MIDI Representation

```text
SLIDE CONCEPT:
Explaining how a physical acoustic piano translates mathematically into discrete MIDI integers.

KEY POINTS TO EMPHASIZE:
- A physical piano has 88 keys, spanning from A0 (MIDI 21) at 27.5 Hz to C8 (MIDI 108) at 4186 Hz.
- The MIDI protocol provides 128 discrete integer pitch values (0 through 127). Pitches 0–20 and 109–127 are beyond the physical acoustic keyboard but represent valid MIDI note numbers.
- In Western 12-tone equal temperament, an octave represents a doubling of frequency (12 semitones). The pitch formula is f = 440 * 2^((p-69)/12).
- In MelodyLoop, Middle C (C4) has integer index 60, and Concert A (A4) has index 69.

TRANSITION:
Now let us clarify why symbolic MIDI instructions differ fundamentally from audio waveforms.
```

---

## Slide 05: Symbolic MIDI vs. Continuous Audio

```text
SLIDE CONCEPT:
Clarifying the fundamental technical distinction between symbolic musical tokens and continuous acoustic sound.

TECHNICAL ARGUMENT:
A common misconception among beginner evaluators is asking: 'Does your neural network generate MP3 or WAV directly?'
The answer is NO. The neural network predicts discrete symbolic tokens (which key, what duration, what gap). A MIDI file contains only musical instructions, similar to sheet music for a computer player.
Sound only exists when those instructions pass into an audio synthesizer. In MelodyLoop, audio is rendered by our additive synthesizer in melodyloop/audio.py, converting tokens into 44.1 kHz PCM waveforms.

TRANSITION:
Let us examine the MAESTRO dataset used to train this network.
```

---

## Slide 06: The MAESTRO Dataset

```text
SLIDE CONCEPT:
Presenting the official MAESTRO v3.0.0 dataset and proving zero data leakage across training, validation, and test splits.

TECHNICAL DETAILS:
- MAESTRO (MIDI and Audio Edited for Synchronous TRacks and Organization) was created by Google Magenta.
- Crucially, these are live performances captured by optical sensors on Yamaha Disklavier pianos, capturing real expressive human dynamics.
- We verified every single file against maestro-v3.0.0.csv: exactly 962 train, 137 validation, and 177 test performances.
- Training sequences are extracted exclusively from the training split. Validation sequences are never leaked into training, and test sequences are strictly held out for final evaluation.

TRANSITION:
Let us examine the empirical scaling experiment: how we expanded from the baseline 13 files to all 962 performances.
```

---

## Slide 07: Corpus Scaling & Bottleneck Diagnosis

```text
SLIDE CONCEPT:
Explaining why the baseline model only trained on 13 files and detailing the architectural fix that scaled training across all 962 performances.

VIVA QUESTION READINESS:
Professor: 'Why did your baseline only train on 13 files?'
Answer:
In the original data.py, there was a break statement: 'if total_sequences >= 15000: break'. Because long virtuosic classical performances yield over 1,500 sequences per file, the threshold was triggered after just 13 performances. The model memorized a tiny subset of composers.
We completely restructured data.py to proportionally extract sequences from all 962 performances, scaling note events from 64k to 5.66 million while keeping RAM footprint compact via uint8 tensors.

TRANSITION:
Now let us examine the data preprocessing pipeline from raw MIDI to training tensors.
```

---

## Slide 08: Data Preprocessing & Quantization

```text
SLIDE CONCEPT:
Explaining the 4-step preprocessing pipeline and the quantization mathematics that map continuous physical timings into discrete neural tokens.

TECHNICAL DETAILS:
Why 32 bins?
If you use continuous floating-point numbers directly in an RNN, the network struggles with regression loss landscape instability and error compounding.
By quantizing continuous time into 32 discrete bins, we convert regression into classification. Softmax over 32 bins allows the model to capture multi-modal timing patterns (e.g., either an eighth note or a quarter note, never an arbitrary irrational duration).

TRANSITION:
Now let us see how these token tuples are assembled into sliding sequence windows.
```

---

## Slide 09: Sequence Formulation & Training Targets

```text
SLIDE CONCEPT:
Explaining how chronologically ordered note events are sliced into input windows and multi-task prediction targets.

KEY ARCHITECTURAL DECISIONS:
- Sequence Length = 32 notes: This corresponds to approximately 8 to 12 seconds of musical performance, giving sufficient melodic context to establish key, chord progression, and rhythmic meter.
- Stride = 4 notes: We slide the window by 4 notes rather than 1 to prevent severe correlation between adjacent training samples and keep dataset size bounded.
- Multi-task target: Target Y contains pitch, duration, and step. The model must learn not only which note to strike next, but how long to hold it and when the subsequent note will begin.

TRANSITION:
Now let us examine why an LSTM architecture is specifically chosen to model these sequential dependencies.
```

---

## Slide 10: Why LSTM Over Vanilla RNN

```text
SLIDE CONCEPT:
A rigorous theoretical comparison showing why an LSTM is required for musical sequence modeling over feedforward or vanilla RNN networks.

VIVA QUESTION READINESS:
If the professor asks: 'Why not use a standard RNN or a Transformer?'
Answer:
1. Compared to Vanilla RNN: Standard RNNs suffer from vanishing gradients. In backpropagation through time (BPTT), the derivative of h_t with respect to h_0 involves repeated matrix multiplications by W. Since the derivative of tanh is bounded by 1, the gradient exponentially shrinks to zero after 5 to 8 time steps. The RNN forgets the key and rhythm.
2. The LSTM solution: The cell state C_t is updated additively (C_t = f_t * C_(t-1) + i_t * C~_t). The gradient can flow unimpeded backward through time without exponential decay—the 'constant error carousel'.
3. Compared to Transformer: Transformers are state-of-the-art for massive billion-parameter models, but an educational LSTM (167k parameters) trains from scratch in minutes on a laptop GPU without requiring multi-gigabyte pretrained weights.

TRANSITION:
Now let us examine the internal anatomy of an LSTM cell and its mathematical gates.
```

---

## Slide 11: Inside the LSTM Cell

```text
SLIDE CONCEPT:
Walking through the mathematical mechanics of the four internal operations in an LSTM cell.

WALKTHROUGH OF THE DIAGRAM:
1. Forget Gate f_t: Uses sigmoid activation. If f_t is close to 0, it tells the cell to forget previous information (such as when a musical phrase ends or modulation occurs). If f_t is close to 1, it preserves the information.
2. Input Gate i_t & Candidate C~_t: The input gate decides whether new information is important, while the tanh candidate generates new potential values.
3. Cell State Update C_t: C_t = f_t * C_(t-1) + i_t * C~_t. Notice this is an element-wise addition! This linear additive update is the exact mathematical reason gradients do not vanish during BPTT.
4. Output Gate o_t: Decides which parts of the cell state C_t to expose in the hidden state h_t, which is then fed into our three prediction heads.

TRANSITION:
Now let us examine how this LSTM cell is integrated into the actual MelodyLoop network architecture.
```

---

## Slide 12: Model Architecture & Parameter Breakdown

```text
SLIDE CONCEPT:
Presenting the verified PyTorch architecture implemented in melodyloop/model.py.

PARAMETER BREAKDOWN PROOF:
Let us verify the exact 167,104 parameter count:
1. Embeddings: 128*64 (pitch) + 32*32 (duration) + 32*32 (step) = 8,192 + 1,024 + 1,024 = 10,240 parameters.
2. LSTM Layer: An LSTM has 4 gates (forget, input, candidate, output). Each gate has weight matrices for input x (128*128), hidden h (128*128), and 2 bias vectors (128 each). 4 * (16384 + 16384 + 256) = 132,096 parameters.
3. Prediction Heads: Pitch head is Linear(128->128): 128*128 + 128 = 16,512. Duration head is Linear(128->32): 128*32 + 32 = 4,128. Step head is Linear(128->32): 128*32 + 32 = 4,128. Sum of heads = 24,768 parameters.
Total Parameters = 10,240 + 132,096 + 24,768 = 167,104 trainable parameters.
Verified by test_model_parameter_count.

TRANSITION:
Now let us examine how the network optimizes these 167k parameters during training.
```

---

## Slide 13: Multi-Task Optimization & Training Loop

```text
SLIDE CONCEPT:
Detailing the optimization cycle, gradient clipping, loss formulation, and hardware execution parameters.

KEY CONCEPTS:
- Joint Multi-Task Loss: Pitch, duration, and step time each have distinct classification distributions. Cross-entropy measures the negative log-likelihood of the ground-truth token. We sum all three equally.
- Gradient Clipping: Because recurrent networks involve repeated matrix products, sudden large gradients can destabilize training. We enforce a hard norm clip of 1.0 using clip_grad_norm_.
- Hardware Efficiency: On our laptop RTX 3050 GPU, the model achieves 91 batches per second, running an entire 100,000-sequence epoch in only 17.2 seconds.

TRANSITION:
Let us examine the empirical training loss curves and why early stopping selected epoch 7 as our best checkpoint.
```

---

## Slide 14: Empirical Training Curves & Checkpoint Selection

```text
SLIDE CONCEPT:
Analyzing the actual epoch-by-epoch training history recorded in artifacts/logs/training_expanded.log.

SCIENTIFIC OBSERVATION:
Notice the classic divergence between training loss and validation loss:
- From Epoch 1 to Epoch 7, both training loss and validation loss drop rapidly (train loss from 6.328 to 5.276, validation loss from 6.239 to 5.915).
- After Epoch 7, training loss continues to fall steadily down to 4.912 at Epoch 15. However, validation loss ceases improving and begins a slight upward drift (5.918 -> 5.957 -> 6.038).
- This divergence demonstrates classic over-parameterization and memorization of training sequences. Because our trainer implemented early stopping with a patience of 8 epochs, training halted automatically at epoch 15.
- The best model saved on disk is strictly the epoch 7 checkpoint (val loss 5.9151), completely preventing overfitted weights from being deployed.

TRANSITION:
Let us examine how checkpoints are serialized and preserved on disk.
```

---

## Slide 15: Checkpoint Serialization & Persistence

```text
SLIDE CONCEPT:
Explaining how model weights, optimizer states, and configuration metadata are serialized into PyTorch .pt binaries.

KEY ENGINEERING PRACTICES:
- Never overwrite working baselines: We explicitly backed up the original baseline checkpoint to best_model_v1_baseline.pt so we can run direct side-by-side musical comparisons.
- Self-contained configuration: The checkpoint dictionary stores the exact hyperparameters used during training. When app.py or generate.py loads the checkpoint, it reads hidden_dim directly from the file, preventing architectural mismatch exceptions.
- State restoration: The script train.py --resume automatically restores both model weights and the Adam optimizer's internal momentum states, enabling training to pick up exactly where it was interrupted.

TRANSITION:
Now let us examine how the trained model autoregressively generates new musical compositions.
```

---

## Slide 16: Autoregressive Sampling & Top-K Filtering

```text
SLIDE CONCEPT:
Explaining the mathematical mechanics of autoregressive generation and stochastic sampling controls.

TECHNICAL BREAKDOWN:
How Autoregression Works:
1. The model receives a rolling context window of 32 note events.
2. The model outputs unnormalized logits for pitch, duration, and step.
3. Sampling with Temperature: Instead of greedily picking the argmax (which causes the network to loop the exact same note repeatedly), we divide logits by temperature T and apply Softmax.
4. Top-K Filtering: Greedily sampling from the full 128 pitch vocabulary risks picking extreme low-probability notes (e.g. jumping from pitch 60 to pitch 120). By filtering for only the Top-K=5 candidates, we guarantee that every sampled note is among the model's top 5 most confident musical hypotheses.
5. Rolling Update: The sampled note is appended to the buffer, the oldest note is evicted, and the loop repeats for N notes.

TRANSITION:
Now let us see how these discrete tokens are rendered into playable sound.
```

---

## Slide 17: Audio Rendering & Synthesis

```text
SLIDE CONCEPT:
Explaining the physics and DSP mathematics behind converting discrete tokens into 44.1 kHz WAV audio.

TECHNICAL DETAILS:
- Pure sine waves sound like synthetic telephone test tones, not piano notes.
- An acoustic piano string vibrates in multiple modes: the fundamental frequency f0, plus integer harmonics 2*f0, 3*f0, etc. In melodyloop/audio.py, we implement additive synthesis: 60% energy in the fundamental, 25% in the second harmonic (octave), and 15% in the third harmonic (fifth).
- Amplitude Envelope: In an acoustic piano, when the hammer strikes the string, amplitude peaks instantly and decays exponentially. We multiply the composite wave by exp(-3.0 * t / duration), with a 5 millisecond attack and 10 millisecond release to eliminate boundary clicking.
- This entire DSP pipeline is self-contained in pure NumPy and SciPy—requiring zero external soundfonts or third-party audio drivers.

CLOSING SUMMARY:
MelodyLoop demonstrates how an LSTM trained on symbolic performance data learns rhythmic and melodic patterns, serialized into verifiable checkpoints, and synthesized into playable music in real time.
```

---
