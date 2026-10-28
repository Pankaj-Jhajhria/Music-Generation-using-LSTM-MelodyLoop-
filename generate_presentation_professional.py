"""
Generate MelodyLoop_Presentation_Professional.pptx
Academic-grade, dark-themed, 16:9 widescreen presentation with embedded speaker notes.
"""

from pathlib import Path
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# Palette & Constants
# ==============================================================================
# Coordinated high-contrast academic palette:
NAVY_BG      = RGBColor(11, 16, 32)       # #0B1020 Deep Navy Background
CARD_BG      = RGBColor(21, 29, 54)       # #151D36 Card Surface
CARD_BORDER  = RGBColor(42, 59, 106)      # #2A3B6A Card Border
ROYAL_BLUE   = RGBColor(40, 85, 217)      # #2855D9 Primary Technical Blue
CYAN_ACCENT  = RGBColor(38, 217, 241)     # #26D9F1 High-contrast Data Flow Cyan
GOLD_ACCENT  = RGBColor(255, 200, 87)     # #FFC857 Training & Highlights Gold
CORAL_ACCENT = RGBColor(255, 107, 107)    # #FF6B6B Alert & Limitation Coral
GREEN_ACCENT = RGBColor(34, 197, 94)      # #22C55E Success Green
IVORY_TEXT   = RGBColor(244, 243, 235)    # #F4F3EB Primary Light Text
MUTED_TEXT   = RGBColor(148, 163, 184)    # #94A3B8 Secondary Subtitle Text

FONT_NAME = "Segoe UI"
FONT_TITLE = "Segoe UI"

ASSETS_DIR = Path("artifacts/presentation_assets")
OUTPUT_PPTX = Path("MelodyLoop_Presentation_Professional.pptx")
NOTES_MD_PATH = Path("docs/MelodyLoop_Presentation_Speaker_Notes.md")

# Ensure assets exist
assert (ASSETS_DIR / "fig_piano_keyboard.png").exists(), "Assets must be pre-generated."


class SlideDeckBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]
        self.all_notes = []

    def set_background(self, slide, color=NAVY_BG):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(self, slide, category: str, title: str, slide_num: int):
        # Header banner line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.45), Inches(11.733), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = CYAN_ACCENT
        line.line.fill.background()

        # Category tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(8.0), Inches(0.35))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
        p_c = tf_c.paragraphs[0]
        p_c.text = category.upper()
        p_c.font.name = FONT_NAME
        p_c.font.size = Pt(11)
        p_c.font.bold = True
        p_c.font.color.rgb = CYAN_ACCENT

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(10.5), Inches(0.65))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = IVORY_TEXT

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(11.333), Inches(0.85), Inches(1.2), Inches(0.45))
        tf_n = num_box.text_frame
        tf_n.margin_left = tf_n.margin_right = tf_n.margin_top = tf_n.margin_bottom = 0
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.text = f"{slide_num:02d} / 24"
        p_n.font.name = FONT_NAME
        p_n.font.size = Pt(13)
        p_n.font.bold = True
        p_n.font.color.rgb = GOLD_ACCENT

        # Footer
        f_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
        tf_f = f_box.text_frame
        tf_f.margin_left = tf_f.margin_right = tf_f.margin_top = tf_f.margin_bottom = 0
        p_f = tf_f.paragraphs[0]
        p_f.text = "MelodyLoop — LSTM Music Generation | Academic Project Defense & Evaluation"
        p_f.font.name = FONT_NAME
        p_f.font.size = Pt(9.5)
        p_f.font.color.rgb = MUTED_TEXT

    def add_card(self, slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    def add_metric_chip(self, slide, left, top, width, height, value: str, label: str, val_color=CYAN_ACCENT):
        self.add_card(slide, left, top, width, height)
        box = slide.shapes.add_textbox(Inches(left + 0.1), Inches(top + 0.08), Inches(width - 0.2), Inches(height - 0.16))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.text = value
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(20)
        p1.font.bold = True
        p1.font.color.rgb = val_color

        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.name = FONT_NAME
        p2.font.size = Pt(10)
        p2.font.color.rgb = MUTED_TEXT
        p2.space_before = Pt(3)

    def attach_notes(self, slide, slide_num: int, title: str, notes_text: str):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text
        self.all_notes.append({
            "slide_num": slide_num,
            "title": title,
            "notes": notes_text
        })


def build_deck():
    builder = SlideDeckBuilder()
    prs = builder.prs

    # ==============================================================================
    # SLIDE 1: TITLE SLIDE
    # ==============================================================================
    s1 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s1)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.12), Inches(3.8))
    bar.fill.solid()
    bar.fill.fore_color.rgb = CYAN_ACCENT
    bar.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(2.2))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "MelodyLoop"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(48)
    p1.font.bold = True
    p1.font.color.rgb = IVORY_TEXT

    p2 = tf1.add_paragraph()
    p2.text = "LSTM-Based Sequential Piano Music Generation"
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(24)
    p2.font.color.rgb = CYAN_ACCENT
    p2.font.bold = True
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "A Deep-Learning Framework for Discrete Symbolic Event Modeling, Multi-Task Next-Note Prediction, and Controllable Audio Synthesis"
    p3.font.name = FONT_NAME
    p3.font.size = Pt(13)
    p3.font.color.rgb = MUTED_TEXT
    p3.space_before = Pt(12)

    # 4 Key Highlights in Cards
    highlights = [
        ("962 Pieces", "MAESTRO v3.0 Corpus", CYAN_ACCENT),
        ("5.66M Notes", "Chronological Events", GOLD_ACCENT),
        ("167k Params", "Multi-Head LSTM", ROYAL_BLUE),
        ("Val: 5.9151", "Epoch 7 Best Checkpoint", GREEN_ACCENT),
    ]
    for idx, (val, lbl, col) in enumerate(highlights):
        builder.add_metric_chip(s1, 1.2 + idx * 2.8, 4.4, 2.6, 1.1, val, lbl, col)

    # Footer Metadata
    meta_box = s1.shapes.add_textbox(Inches(1.2), Inches(6.0), Inches(11.0), Inches(0.8))
    tf_m = meta_box.text_frame
    p_m1 = tf_m.paragraphs[0]
    p_m1.text = "Academic Project Defense | NLP & Deep Sequence Modeling | PyTorch Implementation"
    p_m1.font.name = FONT_NAME
    p_m1.font.size = Pt(11)
    p_m1.font.color.rgb = IVORY_TEXT

    p_m2 = tf_m.add_paragraph()
    p_m2.text = "Repository: https://github.com/Pankaj-Jhajhria/Music-Generation-using-LSTM-MelodyLoop-"
    p_m2.font.name = FONT_NAME
    p_m2.font.size = Pt(10)
    p_m2.font.color.rgb = MUTED_TEXT

    builder.attach_notes(s1, 1, "Title Slide — MelodyLoop",
        "OPENING TALK:\n"
        "Good morning, Professor and members of the evaluation committee. Today, I am presenting MelodyLoop, an end-to-end deep learning engineering project focused on symbolic piano music generation using a custom Long Short-Term Memory network.\n\n"
        "CORE IDEA:\n"
        "Rather than treating music as unstructured raw audio waveforms or static images, MelodyLoop formulates music as a discrete temporal sequence of structured musical events. The system trains an LSTM neural network from scratch on over 5.6 million note events extracted from 962 professional piano performances from Google Magenta's MAESTRO dataset.\n\n"
        "KEY ENGINEERING MILESTONES:\n"
        "- Scaled training across the entire official MAESTRO training split (962 performances, 100,000 sequences).\n"
        "- Designed a compact uint8 tensor representation reducing RAM overhead by 8x on consumer hardware.\n"
        "- Implemented multi-task prediction heads for pitch, duration, and time step, achieving a best validation loss of 5.9151 at epoch 7.\n"
        "- Built an interactive Streamlit web dashboard with local additive harmonic synthesis for immediate audio evaluation.\n\n"
        "TRANSITION:\n"
        "Let us begin with the formal problem statement and our engineering objectives."
    )

    # ==============================================================================
    # SLIDE 2: PROBLEM STATEMENT & PROJECT OBJECTIVE (Chapter 1)
    # ==============================================================================
    s2 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s2)
    builder.add_header(s2, "Chapter 01 • Introduction & Scope", "Problem Formulation & Engineering Objectives", 2)

    # Left Column: Problem Formulation Card
    builder.add_card(s2, 0.8, 1.7, 5.7, 5.1)
    b_l = s2.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.3), Inches(4.7))
    tf_l = b_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "THE SEQUENCE MODELING PROBLEM"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    items_l = [
        ("Temporal Musical Dependencies:", " Piano music consists of chronologically ordered note onsets. A note's harmonic and rhythmic meaning depends strictly on prior musical context."),
        ("Multi-Dimensional Event Complexity:", " Music cannot be modeled by pitch alone. Each note requires pitch (0–127), duration (how long it rings), and step time (interval until the next note onset)."),
        ("Discrete Symbolic vs. Waveform Audio:", " Modeling raw 44.1 kHz waveforms requires predicting 44,100 continuous samples per second. Symbolic MIDI reduces dimensionality to structured, discrete tokens."),
        ("Autoregressive Generation:", " Generating continuous coherent music requires the network to predict future tokens iteratively from its own past outputs while avoiding mode collapse and monotone loops.")
    ]
    for title, desc in items_l:
        p_t = tf_l.add_paragraph()
        p_t.space_before = Pt(8)
        run1 = p_t.add_run()
        run1.text = "• " + title
        run1.font.bold = True
        run1.font.color.rgb = IVORY_TEXT
        run1.font.size = Pt(11)
        run2 = p_t.add_run()
        run2.text = desc
        run2.font.color.rgb = MUTED_TEXT
        run2.font.size = Pt(10.5)

    # Right Column: Project Objectives Card
    builder.add_card(s2, 6.8, 1.7, 5.7, 5.1)
    b_r = s2.shapes.add_textbox(Inches(7.0), Inches(1.85), Inches(5.3), Inches(4.7))
    tf_r = b_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "ENGINEERING OBJECTIVES & CONTRIBUTIONS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    items_r = [
        ("Discrete Tokenization & Quantization:", " Implemented a robust 3-tuple tokenizer mapping continuous timing into 32 duration bins and 32 step bins, preserving musical fidelity."),
        ("Bounded-Memory Training Pipeline:", " Developed parallel multi-process MIDI parsing and uint8 memory structures, enabling training on 100,000 sequences across 962 files within 4 GB GPU VRAM."),
        ("Multi-Task LSTM Architecture:", " Built a 167,104-parameter LSTM with 3 parallel embeddings and 3 dedicated cross-entropy heads trained jointly with Adam."),
        ("Controllable Sampling Engine:", " Implemented temperature scaling (T=0.6–1.0), Top-K filtering (k=5), repetition penalties, and seeded continuation from real classical themes."),
        ("Full-Stack Audio Deployment:", " Integrated a local additive harmonic synthesizer (fundamental + 4 harmonics + ADSR envelope) and an interactive Streamlit UI.")
    ]
    for title, desc in items_r:
        p_t = tf_r.add_paragraph()
        p_t.space_before = Pt(8)
        run1 = p_t.add_run()
        run1.text = "✓ " + title
        run1.font.bold = True
        run1.font.color.rgb = IVORY_TEXT
        run1.font.size = Pt(11)
        run2 = p_t.add_run()
        run2.text = desc
        run2.font.color.rgb = MUTED_TEXT
        run2.font.size = Pt(10.5)

    builder.attach_notes(s2, 2, "Problem Formulation & Objectives",
        "SLIDE CONCEPT:\n"
        "Here we define why symbolic music generation is an ideal sequence-modeling task and specify the exact engineering goals of MelodyLoop.\n\n"
        "TECHNICAL EXPLANATION:\n"
        "Music is inherently temporal and hierarchical. Unlike natural language processing where tokens are words or subwords, musical events have simultaneous attributes: which key is pressed (pitch), how long it is sustained (duration), and the temporal gap until the next event begins (step time).\n"
        "If you predict only pitch, you lose rhythm and tempo completely. If you model raw waveform audio directly, 10 seconds of CD audio equals 441,000 samples, which creates prohibitive computational demands for educational sequence models. Symbolic event modeling provides the optimal balance of structured expressiveness and computational tractability.\n\n"
        "TRANSITION:\n"
        "Now let us examine the complete end-to-end system architecture that implements this pipeline."
    )

    # ==============================================================================
    # SLIDE 3: COMPLETE END-TO-END SYSTEM OVERVIEW (Chapters 1, 6, 9, 11, 12)
    # ==============================================================================
    s3 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s3)
    builder.add_header(s3, "Chapters 01, 06, 09, 11, 12 • End-to-End Pipeline", "Complete MelodyLoop Architectural Workflow", 3)

    # Insert dark-themed end-to-end diagram
    img_path = ASSETS_DIR / "fig_end_to_end_flowchart.png"
    s3.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(11.733), Inches(3.7))

    # Bottom 3 Cards highlighting Key Modules & Code Responsibilities
    modules = [
        ("Phase 1: Ingestion & Quantization", "melodyloop/data.py", "Parses raw MIDI via mido, enforces official train/val/test splits, quantizes continuous timing into 32 bins, builds sliding windows, and caches compact uint8 tensors.", CYAN_ACCENT),
        ("Phase 2: Recurrent Training", "melodyloop/model.py & train.py", "Passes sequence (B, 32, 3) through parallel embeddings, a 128-d LSTM, and 3 linear heads. Optimizes joint cross-entropy loss with Adam (lr=1e-3).", ROYAL_BLUE),
        ("Phase 3: Generation & Synthesis", "melodyloop/generation.py & audio.py", "Autoregressively rolls out sequences using temperature & Top-K sampling. Decodes tokens into MIDI and renders audio via additive harmonic synthesis.", GOLD_ACCENT)
    ]
    for idx, (m_title, m_file, m_desc, col) in enumerate(modules):
        builder.add_card(s3, 0.8 + idx * 4.0, 5.5, 3.733, 1.45)
        box = s3.shapes.add_textbox(Inches(0.9 + idx * 4.0), Inches(5.55), Inches(3.533), Inches(1.35))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = m_title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col

        p_f = tf.add_paragraph()
        p_f.text = f"File: {m_file}"
        p_f.font.size = Pt(9.5)
        p_f.font.color.rgb = IVORY_TEXT
        p_f.space_before = Pt(2)

        p_d = tf.add_paragraph()
        p_d.text = m_desc
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = MUTED_TEXT
        p_d.space_before = Pt(3)

    builder.attach_notes(s3, 3, "Complete End-to-End Workflow",
        "SLIDE CONCEPT:\n"
        "This slide presents the entire MelodyLoop architecture from raw dataset to final playable audio.\n\n"
        "TECHNICAL BREAKDOWN:\n"
        "The system operates in three decoupled, production-grade phases:\n"
        "1. Ingestion Phase: Handled by melodyloop/data.py. Reads MAESTRO MIDI files, extracts Note On/Off chronological events, quantizes durations and steps, and prepares bounded uint8 PyTorch Datasets.\n"
        "2. Training Phase: Handled by train.py and melodyloop/model.py. Trains the 167k-parameter LSTM across 100,000 sequence batches, monitoring validation loss after every epoch and saving the best checkpoint.\n"
        "3. Inference & Synthesis Phase: Handled by melodyloop/generation.py and audio.py. The model takes a seed buffer, iteratively samples successive notes, exports a standard MIDI file, and synthesizes a WAV preview using NumPy/SciPy.\n\n"
        "TRANSITION:\n"
        "Let us examine how acoustic piano notes are translated into numerical representations."
    )

    # ==============================================================================
    # SLIDE 4: HOW A PIANO BECOMES NUMERICAL DATA (Chapter 2)
    # ==============================================================================
    s4 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s4)
    builder.add_header(s4, "Chapter 02 • Music Data Representation", "Symbolic Musical Representation: Keyboard to MIDI", 4)

    # Diagram top
    img_path = ASSETS_DIR / "fig_piano_keyboard.png"
    s4.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(11.733), Inches(3.2))

    # Bottom 3 Cards explaining the numerical mapping
    cards = [
        ("The 128 MIDI Pitch Standard", "MIDI note numbers span integers [0, 127].\nStandard 88-key acoustic pianos cover A0 (MIDI 21, 27.5 Hz) to C8 (MIDI 108, 4186 Hz). Middle C is defined as MIDI 60 (C4, 261.63 Hz). Concert A is MIDI 69 (A4, 440.0 Hz).", CYAN_ACCENT),
        ("The 3-Tuple Event Structure", "Every note event in MelodyLoop is represented by:\n• Pitch p ∈ [0, 127] (Discrete MIDI pitch)\n• Duration d ∈ [0, 31] (Sustained ring time)\n• Step s ∈ [0, 31] (Interval to next note onset)\nEnables polyphonic overlap and pacing.", GOLD_ACCENT),
        ("Mathematical Frequency Formula", "Continuous frequency in Hertz is calculated by:\n    f = 440.0 × 2^((p - 69) / 12)\nEqual temperament divides each octave into 12 logarithmic semitones. A semitone increase multiplies frequency by 2^(1/12) ≈ 1.05946.", ROYAL_BLUE)
    ]
    for idx, (c_title, c_desc, col) in enumerate(cards):
        builder.add_card(s4, 0.8 + idx * 4.0, 5.0, 3.733, 1.9)
        box = s4.shapes.add_textbox(Inches(0.95 + idx * 4.0), Inches(5.1), Inches(3.433), Inches(1.7))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = c_desc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(4)

    builder.attach_notes(s4, 4, "Keyboard to MIDI Representation",
        "SLIDE CONCEPT:\n"
        "Explaining how a physical acoustic piano translates mathematically into discrete MIDI integers.\n\n"
        "KEY POINTS TO EMPHASIZE:\n"
        "- A physical piano has 88 keys, spanning from A0 (MIDI 21) at 27.5 Hz to C8 (MIDI 108) at 4186 Hz.\n"
        "- The MIDI protocol provides 128 discrete integer pitch values (0 through 127). Pitches 0–20 and 109–127 are beyond the physical acoustic keyboard but represent valid MIDI note numbers.\n"
        "- In Western 12-tone equal temperament, an octave represents a doubling of frequency (12 semitones). The pitch formula is f = 440 * 2^((p-69)/12).\n"
        "- In MelodyLoop, Middle C (C4) has integer index 60, and Concert A (A4) has index 69.\n\n"
        "TRANSITION:\n"
        "Now let us clarify why symbolic MIDI instructions differ fundamentally from audio waveforms."
    )

    # ==============================================================================
    # SLIDE 5: MIDI IS NOT AUDIO (Chapter 2)
    # ==============================================================================
    s5 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s5)
    builder.add_header(s5, "Chapter 02 • Representation Hierarchy", "Representation Hierarchy: Symbolic MIDI vs. Continuous Audio", 5)

    img_path = ASSETS_DIR / "fig_midi_vs_audio.png"
    s5.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(11.733), Inches(3.4))

    # Bottom Comparison Table in Cards
    col_w = 3.733
    cards_data = [
        ("1. Symbolic MIDI (.mid)", "• Representation: Event metadata (pitch, time, velocity)\n• Data Volume: Tiny (~1–5 KB per minute)\n• Content: Musical intent / sheet music instructions\n• Network Role: Perfect target for discrete sequence modeling and token embeddings.", CYAN_ACCENT),
        ("2. Synthesized Waveform (.wav)", "• Representation: 44,100 continuous 16-bit PCM samples/s\n• Data Volume: Large (~10.5 MB per minute uncompressed)\n• Content: Acoustic pressure waves in air\n• Network Role: Generated downstream via additive synthesis (melodyloop/audio.py).", GOLD_ACCENT),
        ("3. Compressed Audio (.mp3)", "• Representation: Psychoacoustic MDCT frequency lossy bins\n• Data Volume: Medium (~1 MB per minute at 128 kbps)\n• Content: Perceptually masked audio stream\n• Network Role: Delivery format; unsuitable for token-level neural sequence modeling.", CORAL_ACCENT)
    ]
    for idx, (c_title, c_desc, col) in enumerate(cards_data):
        builder.add_card(s5, 0.8 + idx * 4.0, 5.2, col_w, 1.7)
        box = s5.shapes.add_textbox(Inches(0.95 + idx * 4.0), Inches(5.3), Inches(col_w - 0.3), Inches(1.5))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = c_desc
        p_d.font.size = Pt(9.0)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(4)

    builder.attach_notes(s5, 5, "Symbolic MIDI vs. Continuous Audio",
        "SLIDE CONCEPT:\n"
        "Clarifying the fundamental technical distinction between symbolic musical tokens and continuous acoustic sound.\n\n"
        "TECHNICAL ARGUMENT:\n"
        "A common misconception among beginner evaluators is asking: 'Does your neural network generate MP3 or WAV directly?'\n"
        "The answer is NO. The neural network predicts discrete symbolic tokens (which key, what duration, what gap). A MIDI file contains only musical instructions, similar to sheet music for a computer player.\n"
        "Sound only exists when those instructions pass into an audio synthesizer. In MelodyLoop, audio is rendered by our additive synthesizer in melodyloop/audio.py, converting tokens into 44.1 kHz PCM waveforms.\n\n"
        "TRANSITION:\n"
        "Let us examine the MAESTRO dataset used to train this network."
    )

    # ==============================================================================
    # SLIDE 6: THE MAESTRO DATASET (Chapter 3)
    # ==============================================================================
    s6 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s6)
    builder.add_header(s6, "Chapter 03 • Training Corpus", "The MAESTRO Dataset: Scope, Splits & Diversity", 6)

    img_path = ASSETS_DIR / "fig_maestro_splits.png"
    s6.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(11.733), Inches(3.4))

    # Bottom 3 Cards on Data Quality, Discovered Metadata & Strict Split Discipline
    cards = [
        ("Gold-Standard Yamaha Disklavier Data", "MAESTRO v3.0.0 contains 1,276 performances (200 hours) captured live from the International Piano-e-Competition.\nYamaha Disklavier concert grand pianos recorded note onsets and releases with millisecond accuracy, capturing virtuosic human expressive nuance.", CYAN_ACCENT),
        ("Discovered Metadata Distribution", "Catalogued across 10 years of international competition:\n• 962 Training Performances (75.4%)\n• 137 Validation Performances (10.7%)\n• 177 Held-out Test Performances (13.9%)\nIncludes Chopin, Beethoven, Liszt, Bach, and Scriabin.", GOLD_ACCENT),
        ("Zero Data Leakage Protocol", "Rigorous split isolation is strictly maintained in config.py:\n• Parameter updates: Computed exclusively on 962 train files.\n• Early stopping: Monitored on 137 validation files (no gradients).\n• Final benchmark: Conducted on held-out test split (e.g. Scriabin Op. 63).", ROYAL_BLUE)
    ]
    for idx, (c_title, c_desc, col) in enumerate(cards):
        builder.add_card(s6, 0.8 + idx * 4.0, 5.2, 3.733, 1.7)
        box = s6.shapes.add_textbox(Inches(0.95 + idx * 4.0), Inches(5.3), Inches(3.433), Inches(1.5))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = c_desc
        p_d.font.size = Pt(9.0)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(4)

    builder.attach_notes(s6, 6, "The MAESTRO Dataset",
        "SLIDE CONCEPT:\n"
        "Presenting the official MAESTRO v3.0.0 dataset and proving zero data leakage across training, validation, and test splits.\n\n"
        "TECHNICAL DETAILS:\n"
        "- MAESTRO (MIDI and Audio Edited for Synchronous TRacks and Organization) was created by Google Magenta.\n"
        "- Crucially, these are live performances captured by optical sensors on Yamaha Disklavier pianos, capturing real expressive human dynamics.\n"
        "- We verified every single file against maestro-v3.0.0.csv: exactly 962 train, 137 validation, and 177 test performances.\n"
        "- Training sequences are extracted exclusively from the training split. Validation sequences are never leaked into training, and test sequences are strictly held out for final evaluation.\n\n"
        "TRANSITION:\n"
        "Let us examine the empirical scaling experiment: how we expanded from the baseline 13 files to all 962 performances."
    )

    # ==============================================================================
    # SLIDE 7: AVAILABLE DATA VS DATA USED (Chapter 3)
    # ==============================================================================
    s7 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s7)
    builder.add_header(s7, "Chapter 03 • Empirical Scaling", "Dataset Scaling: Baseline Bottleneck vs. Expanded Corpus", 7)

    # Left: Scaling Chart
    img_path = ASSETS_DIR / "fig_dataset_scaling.png"
    s7.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(6.8), Inches(3.4))

    # Right: Quantitative Comparison Table Card
    builder.add_card(s7, 7.8, 1.65, 4.733, 3.4)
    tbl_box = s7.shapes.add_textbox(Inches(8.0), Inches(1.8), Inches(4.333), Inches(3.1))
    tf_tbl = tbl_box.text_frame
    tf_tbl.word_wrap = True

    p = tf_tbl.paragraphs[0]
    p.text = "CORPUS EXPANSION COMPARISON"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    table_lines = [
        ("Training Files Processed:", "13 → 962 (74× Increase)"),
        ("Extracted Note Events:", "64,261 → 5,659,329 (88× Increase)"),
        ("Training Sequences:", "15,000 → 100,000 (6.7× Increase)"),
        ("Validation Performances:", "1 → 137 (137× Increase)"),
        ("Validation Sequences:", "3,924 → 10,000 (2.5× Increase)"),
        ("RAM Representation:", "int64 (77 MB) → uint8 (9.6 MB)"),
        ("Cached Load Time:", "10s → 1.88s (Train) / 0.26s (Val)")
    ]
    for lbl, val in table_lines:
        p_line = tf_tbl.add_paragraph()
        p_line.space_before = Pt(4)
        r1 = p_line.add_run()
        r1.text = lbl + " "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = IVORY_TEXT
        r2 = p_line.add_run()
        r2.text = val
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = CYAN_ACCENT

    # Bottom Full-width Card: The Engineering Root Cause & Solution
    builder.add_card(s7, 0.8, 5.2, 11.733, 1.7)
    box_b = s7.shapes.add_textbox(Inches(1.0), Inches(5.3), Inches(11.333), Inches(1.5))
    tf_b = box_b.text_frame
    tf_b.word_wrap = True

    p = tf_b.paragraphs[0]
    p.text = "DIAGNOSIS & RESOLUTION OF THE ORIGINAL 13-PERFORMANCE BOTTLENECK"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    bullets = [
        "Root Cause in data.py: The original pipeline hit a hard-coded break statement (if current_total >= 15000: break) on file #13, terminating loop execution and discarding the remaining 949 training performances.",
        "Proportional Sequence Balancing: Replaced the premature break with proportional piece sampling (max 16–100 sequences per piece), drawing diverse sequences evenly across all 962 performances.",
        "Bounded uint8 Tensor Memory: Storing sequences as compact uint8 tensors in RAM prevented Python memory bloat, enabling 100k sequences to load in 1.88 seconds from persistent .npz caches."
    ]
    for b in bullets:
        p_b = tf_b.add_paragraph()
        p_b.space_before = Pt(3)
        p_b.text = "• " + b
        p_b.font.size = Pt(9.0)
        p_b.font.color.rgb = IVORY_TEXT

    builder.attach_notes(s7, 7, "Corpus Scaling & Bottleneck Diagnosis",
        "SLIDE CONCEPT:\n"
        "Explaining why the initial experiment only trained on 13 files and how we engineered the expanded dataset pipeline.\n\n"
        "VIVA QUESTION READINESS:\n"
        "If a professor asks: 'Why did the earlier version stop after 13 performances?'\n"
        "Answer: In melodyloop/data.py line 231, there was an early termination condition: if current_total >= max_sequences and files_processed >= min(num_target_files, 25): break. Because max_sequences was set to 15,000, it accumulated 15,000 sequences from the first 13 files and immediately broke out of the loop, skipping the other 949 training files.\n\n"
        "OUR SOLUTION:\n"
        "We redesigned the data loader with proportional sequence balancing: each piece contributes an even budget of sequences across its duration. We also implemented multi-process parsing and uint8 compact tensor storage, allowing us to process all 5.66 million note events across 962 files within 2 minutes and load them in 1.88 seconds.\n\n"
        "TRANSITION:\n"
        "Let us examine the exact mathematical tokenization that converts MIDI into training events."
    )

    # ==============================================================================
    # SLIDE 8: DATA PREPROCESSING & 3-TUPLE QUANTIZATION (Chapter 6)
    # ==============================================================================
    s8 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s8)
    builder.add_header(s8, "Chapter 06 • Preprocessing & Tokenization", "Data Preprocessing Pipeline & 3-Tuple Quantization", 8)

    # 4 Sequential Cards for the Preprocessing Pipeline
    step_w = 2.78
    steps_data = [
        ("Step 1: mido Parsing", "Raw MIDI Bytes", "Reads binary MIDI via mido, parses note_on / note_off channel events, tracks cumulative delta times, and filters non-piano tracks.", CYAN_ACCENT),
        ("Step 2: Event Pairing", "Note Lifecycles", "Matches each note_on with its corresponding note_off to compute exact continuous start time (t_start) and duration (t_dur = t_off - t_on).", ROYAL_BLUE),
        ("Step 3: Step Interval", "Temporal Dynamics", "Sorts all notes chronologically and computes step time: s_i = max(0.0, start_(i+1) - start_i). Chords produce step = 0.0s.", GOLD_ACCENT),
        ("Step 4: Bin Quantization", "Discrete Tokens", "Maps continuous duration into 32 logarithmic/linear bins [0.05s, 4.0s] and step into 32 bins [0.0s, 2.0s]. Pitch is 0–127.", GREEN_ACCENT),
    ]
    for idx, (title, sub, desc, col) in enumerate(steps_data):
        builder.add_card(s8, 0.8 + idx * 3.0, 1.7, step_w, 2.5)
        box = s8.shapes.add_textbox(Inches(0.9 + idx * 3.0), Inches(1.8), Inches(step_w - 0.2), Inches(2.3))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        p_s = tf.add_paragraph()
        p_s.text = sub
        p_s.font.size = Pt(9.5)
        p_s.font.color.rgb = MUTED_TEXT
        p_s.space_before = Pt(2)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(9.0)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(6)

    # Bottom Card: Quantization Math & Concrete Numerical Example
    builder.add_card(s8, 0.8, 4.4, 11.733, 2.5)
    box_q = s8.shapes.add_textbox(Inches(1.0), Inches(4.5), Inches(11.333), Inches(2.3))
    tf_q = box_q.text_frame
    tf_q.word_wrap = True

    p = tf_q.paragraphs[0]
    p.text = "MATHEMATICAL QUANTIZATION FORMULATION & CONCRETE WORKED EXAMPLE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    math_desc = (
        "Quantization Formula: bin = min(max(int(((clip(v, min_v, max_v) - min_v) / (max_v - min_v)) × (N - 1) + 0.5), 0), N - 1)\n"
        "• Duration Bounds: min = 0.05s, max = 4.00s, N = 32 bins (Bin width: ~0.127s)\n"
        "• Step Interval Bounds: min = 0.00s (chords/dyads), max = 2.00s (pauses), N = 32 bins (Bin width: ~0.0645s)\n\n"
        "Concrete Note Example: Middle C (C4, 261.63 Hz), ringing for 0.45 seconds, followed by another note 0.25 seconds later:\n"
        "    Raw Musical Event: [Pitch = 60, Duration = 0.45s, Step = 0.25s]  →  Discrete Token Tuple: (p = 60, d = 3, s = 4)"
    )
    p_m = tf_q.add_paragraph()
    p_m.space_before = Pt(4)
    p_m.text = math_desc
    p_m.font.size = Pt(9.5)
    p_m.font.color.rgb = IVORY_TEXT

    builder.attach_notes(s8, 8, "Data Preprocessing & Quantization",
        "SLIDE CONCEPT:\n"
        "Explaining the 4-step preprocessing pipeline and the quantization mathematics that map continuous physical timings into discrete neural tokens.\n\n"
        "TECHNICAL DETAILS:\n"
        "Why 32 bins?\n"
        "If you use too few bins (e.g. 4 bins), the model has no rhythmic subtlety; notes sound robotic. If you use too many bins (e.g. 500 bins), data becomes sparse and the output cross-entropy loss becomes difficult to optimize.\n"
        "By setting duration_bins=32 across [0.05s, 4.0s] and step_bins=32 across [0.0s, 2.0s], we capture staccato notes (0.05s), quarter notes, whole notes, simultaneous chords (step=0.0s), and musical pauses up to 2.0s with high fidelity.\n\n"
        "TRANSITION:\n"
        "Now let us examine how these note events are framed into sliding window sequences for next-event supervised learning."
    )

    # ==============================================================================
    # SLIDE 9: SEQUENCE FORMULATION & TRAINING TARGETS (Chapter 6)
    # ==============================================================================
    s9 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s9)
    builder.add_header(s9, "Chapter 06 • Sequence Formulation", "Sequence Formulation: Sliding Windows & Multi-Task Targets", 9)

    # Top Card: Sliding Window Visualization
    builder.add_card(s9, 0.8, 1.7, 11.733, 2.4)
    box_w = s9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(2.2))
    tf_w = box_w.text_frame
    tf_w.word_wrap = True

    p = tf_w.paragraphs[0]
    p.text = "SLIDING-WINDOW SUPERVISED LEARNING FORMULATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    p_desc = tf_w.add_paragraph()
    p_desc.space_before = Pt(4)
    p_desc.text = (
        "Given a chronologically ordered piece of N quantized note events E = (e_1, e_2, ..., e_N) where e_t = (p_t, d_t, s_t):\n"
        "• Sequence Length L = 32 note events per training window | Stride S = 4 notes\n"
        "• Input Tensor X: [e_t, e_(t+1), ..., e_(t+31)] with tensor shape (Batch, 32, 3)\n"
        "• Target Next Event Y: e_(t+32) = (p_(t+32), d_(t+32), s_(t+32)) with target indices (Batch, 3)\n"
        "The model is trained strictly in a teacher-forcing framework: predicting the 33rd event given the ground-truth previous 32 events."
    )
    p_desc.font.size = Pt(10)
    p_desc.font.color.rgb = IVORY_TEXT

    # Concrete visual of the sliding window
    p_vis = tf_w.add_paragraph()
    p_vis.space_before = Pt(6)
    p_vis.text = "Sequence Window i:   [Note 1, Note 2, Note 3, ..., Note 32]  ──▶ Predict Next: Note 33\nSequence Window i+1: [Note 5, Note 6, Note 7, ..., Note 36]  ──▶ Predict Next: Note 37 (Stride = 4)"
    p_vis.font.name = "Consolas"
    p_vis.font.size = Pt(9.5)
    p_vis.font.color.rgb = GOLD_ACCENT

    # Bottom 2 Cards: Multi-Task Targets & Alignment Guarantees
    builder.add_card(s9, 0.8, 4.3, 5.7, 2.6)
    b_t = s9.shapes.add_textbox(Inches(1.0), Inches(4.4), Inches(5.3), Inches(2.4))
    tf_t = b_t.text_frame
    tf_t.word_wrap = True
    p = tf_t.paragraphs[0]
    p.text = "MULTI-TASK TARGET DECOUPLING"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT
    items = [
        ("Pitch Target (y_p):", " Discrete classification over 128 MIDI pitch classes [0, 127]."),
        ("Duration Target (y_d):", " Discrete classification over 32 quantized duration bins [0, 31]."),
        ("Step Interval Target (y_s):", " Discrete classification over 32 quantized step bins [0, 31]."),
        ("Synchronous Backprop:", " All three targets are predicted simultaneously from the final LSTM hidden state h_32.")
    ]
    for lbl, desc in items:
        p_i = tf_t.add_paragraph()
        p_i.space_before = Pt(3)
        r1 = p_i.add_run()
        r1.text = "• " + lbl + " "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = IVORY_TEXT
        r2 = p_i.add_run()
        r2.text = desc
        r2.font.size = Pt(9.0)
        r2.font.color.rgb = MUTED_TEXT

    builder.add_card(s9, 6.8, 4.3, 5.7, 2.6)
    b_a = s9.shapes.add_textbox(Inches(7.0), Inches(4.4), Inches(5.3), Inches(2.4))
    tf_a = b_a.text_frame
    tf_a.word_wrap = True
    p = tf_a.paragraphs[0]
    p.text = "TEMPORAL ALIGNMENT & DATA INTEGRITY"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ROYAL_BLUE
    items_a = [
        ("Strict Chronological Order:", " Notes are sorted by start time prior to sliding; future events never precede past events."),
        ("No Lookahead Leakage:", " Window i only contains notes 1..32; target is note 33. The recurrent state only sees past history."),
        ("Piece Boundary Isolation:", " Sequences are strictly constructed within individual performances; windows never span across different MIDI files."),
        ("Unit Tests Verified:", " test_sequence_generation_and_dataset and test_proportional_event_sequence_generation both pass.")
    ]
    for lbl, desc in items_a:
        p_i = tf_a.add_paragraph()
        p_i.space_before = Pt(3)
        r1 = p_i.add_run()
        r1.text = "✓ " + lbl + " "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = IVORY_TEXT
        r2 = p_i.add_run()
        r2.text = desc
        r2.font.size = Pt(9.0)
        r2.font.color.rgb = MUTED_TEXT

    builder.attach_notes(s9, 9, "Sequence Formulation & Training Targets",
        "SLIDE CONCEPT:\n"
        "Explaining how chronologically ordered note events are sliced into input windows and multi-task prediction targets.\n\n"
        "KEY ARCHITECTURAL DECISIONS:\n"
        "- Sequence Length = 32 notes: This corresponds to approximately 8 to 12 seconds of musical performance, giving sufficient melodic context to establish key, chord progression, and rhythmic meter.\n"
        "- Stride = 4 notes: We slide the window by 4 notes rather than 1 to prevent severe correlation between adjacent training samples and keep dataset size bounded.\n"
        "- Multi-task target: Target Y contains pitch, duration, and step. The model must learn not only which note to strike next, but how long to hold it and when the subsequent note will begin.\n\n"
        "TRANSITION:\n"
        "Now let us examine why an LSTM architecture is specifically chosen to model these sequential dependencies."
    )

    # ==============================================================================
    # SLIDE 10: WHY AN LSTM? (Chapter 7)
    # ==============================================================================
    s10 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s10)
    builder.add_header(s10, "Chapter 07 • Recurrent Architectures", "Sequence Modeling: Why LSTM Over Vanilla RNN?", 10)

    # 3 Comparison Columns
    col_w = 3.733
    archs = [
        ("1. Standard Feedforward (MLP)", "No Recurrent State", "• Structure: y = f(W x + b)\n• Flaw: Assumes all inputs are statistically independent.\n• Musical Failure: Cannot remember musical motifs, key signatures, or rhythmic cadence across time.\n• Verdict: Inapplicable for temporal music modeling.", CARD_BG, CARD_BORDER, MUTED_TEXT),
        ("2. Vanilla Recurrent Network (RNN)", "Simple Hidden Recurrence", "• Structure: h_t = tanh(W_h h_(t-1) + W_x x_t)\n• Flaw: Vanishing & exploding gradients through time.\n• Mathematical Breakdown: Repeated matrix multiplication causes gradient norm to vanish as γ^T (γ < 1).\n• Musical Failure: Forgets notes played > 5 steps ago.", CARD_BG, CARD_BORDER, CORAL_ACCENT),
        ("3. Long Short-Term Memory (LSTM)", "Gated Constant Error Carousel", "• Structure: Dedicated Cell State C_t + 3 Gates (f, i, o)\n• Solution: Additive gradient highway (C_t = f_t C_(t-1) + i_t C~_t) allows gradients to flow across 32+ time steps.\n• Musical Success: Maintains long-term tonality while capturing local ornaments.\n• Verdict: Selected core architecture for MelodyLoop.", CARD_BG, CYAN_ACCENT, CYAN_ACCENT),
    ]
    for idx, (title, sub, desc, bg, border, col) in enumerate(archs):
        builder.add_card(s10, 0.8 + idx * 4.0, 1.7, col_w, 5.1, bg, border)
        box = s10.shapes.add_textbox(Inches(0.95 + idx * 4.0), Inches(1.85), Inches(col_w - 0.3), Inches(4.7))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        p_s = tf.add_paragraph()
        p_s.text = sub
        p_s.font.size = Pt(9.5)
        p_s.font.color.rgb = MUTED_TEXT
        p_s.space_before = Pt(2)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(8)

    builder.attach_notes(s10, 10, "Why LSTM Over Vanilla RNN",
        "SLIDE CONCEPT:\n"
        "A rigorous theoretical comparison showing why an LSTM is required for musical sequence modeling over feedforward or vanilla RNN networks.\n\n"
        "VIVA QUESTION READINESS:\n"
        "If the professor asks: 'Why not use a standard RNN or a Transformer?'\n"
        "Answer:\n"
        "1. Compared to Vanilla RNN: Standard RNNs suffer from vanishing gradients. In backpropagation through time (BPTT), the derivative of h_t with respect to h_0 involves repeated matrix multiplications by W. Since the derivative of tanh is bounded by 1, the gradient exponentially shrinks to zero after 5 to 8 time steps. The RNN forgets the key and rhythm.\n"
        "2. The LSTM solution: The cell state C_t is updated additively (C_t = f_t * C_(t-1) + i_t * C~_t). The gradient can flow unimpeded backward through time without exponential decay—the 'constant error carousel'.\n"
        "3. Compared to Transformer: Transformers are state-of-the-art for massive billion-parameter models, but an educational LSTM (167k parameters) trains from scratch in minutes on a laptop GPU without requiring multi-gigabyte pretrained weights.\n\n"
        "TRANSITION:\n"
        "Now let us examine the internal anatomy of an LSTM cell and its mathematical gates."
    )

    # ==============================================================================
    # SLIDE 11: INSIDE AN LSTM CELL (Chapter 7)
    # ==============================================================================
    s11 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s11)
    builder.add_header(s11, "Chapter 07 • Mathematical Mechanics", "Inside the LSTM Cell: Gated Memory Dynamics", 11)

    img_path = ASSETS_DIR / "fig_lstm_cell.png"
    s11.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(11.733), Inches(3.7))

    # Bottom 4 Gate Description Cards
    gates = [
        ("Forget Gate (f_t)", "f_t = σ(W_f [h_(t-1), x_t] + b_f)\nOutputs values in [0, 1]. Decides what fraction of prior cell memory C_(t-1) to discard (e.g. key modulation).", CORAL_ACCENT),
        ("Input Gate (i_t)", "i_t = σ(W_i [h_(t-1), x_t] + b_i)\nOutputs values in [0, 1]. Decides which incoming musical features from candidate C~_t are worth adding to memory.", CYAN_ACCENT),
        ("Candidate State (C~_t)", "C~_t = tanh(W_c [h_(t-1), x_t] + b_c)\nGenerates candidate new memory vector in [-1, 1], scaled by input gate i_t before addition into cell state.", GREEN_ACCENT),
        ("Output Gate (o_t)", "o_t = σ(W_o [h_(t-1), x_t] + b_o)\nh_t = o_t ⊙ tanh(C_t)\nFilters cell state into the exposed hidden vector h_t passed to prediction heads.", GOLD_ACCENT)
    ]
    for idx, (g_title, g_desc, col) in enumerate(gates):
        builder.add_card(s11, 0.8 + idx * 3.0, 5.5, 2.78, 1.45)
        box = s11.shapes.add_textbox(Inches(0.9 + idx * 3.0), Inches(5.55), Inches(2.58), Inches(1.35))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = g_title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = g_desc
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(2)

    builder.attach_notes(s11, 11, "Inside the LSTM Cell",
        "SLIDE CONCEPT:\n"
        "Walking through the mathematical mechanics of the four internal operations in an LSTM cell.\n\n"
        "WALKTHROUGH OF THE DIAGRAM:\n"
        "1. Forget Gate f_t: Uses sigmoid activation. If f_t is close to 0, it tells the cell to forget previous information (such as when a musical phrase ends or modulation occurs). If f_t is close to 1, it preserves the information.\n"
        "2. Input Gate i_t & Candidate C~_t: The input gate decides whether new information is important, while the tanh candidate generates new potential values.\n"
        "3. Cell State Update C_t: C_t = f_t * C_(t-1) + i_t * C~_t. Notice this is an element-wise addition! This linear additive update is the exact mathematical reason gradients do not vanish during BPTT.\n"
        "4. Output Gate o_t: Decides which parts of the cell state C_t to expose in the hidden state h_t, which is then fed into our three prediction heads.\n\n"
        "TRANSITION:\n"
        "Now let us examine how this LSTM cell is integrated into the actual MelodyLoop network architecture."
    )

    # ==============================================================================
    # SLIDE 12: ACTUAL MODEL ARCHITECTURE (Chapter 8)
    # ==============================================================================
    s12 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s12)
    builder.add_header(s12, "Chapter 08 • PyTorch Network Implementation", "MelodyLoop Neural Architecture & Tensor Flow", 12)

    img_path = ASSETS_DIR / "fig_model_architecture.png"
    s12.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(11.733), Inches(3.6))

    # Bottom 3 Cards on Verified Parameters & Tensor Shapes
    cards = [
        ("Parallel Embedding Layer", "• nn.Embedding(128, 64) -> 8,192 params\n• nn.Embedding(32, 32) -> 1,024 params\n• nn.Embedding(32, 32) -> 1,024 params\nConcatenated into 128-d input vector with Dropout(0.1).", CYAN_ACCENT),
        ("LSTM Core Layer", "• nn.LSTM(input_size=128, hidden_size=128, num_layers=1, batch_first=True)\nWeight matrices: 4 × (128×128 + 128×128 + 2×128) = 132,096 parameters.", ROYAL_BLUE),
        ("Multi-Task Prediction Heads", "• Pitch Head: Linear(128, 128) -> 16,512 params\n• Duration Head: Linear(128, 32) -> 4,128 params\n• Step Head: Linear(128, 32) -> 4,128 params\nTotal Trainable Parameters: 167,104.", GOLD_ACCENT)
    ]
    for idx, (c_title, c_desc, col) in enumerate(cards):
        builder.add_card(s12, 0.8 + idx * 4.0, 5.35, 3.733, 1.55)
        box = s12.shapes.add_textbox(Inches(0.95 + idx * 4.0), Inches(5.4), Inches(3.433), Inches(1.45))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = c_desc
        p_d.font.size = Pt(9.0)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(3)

    builder.attach_notes(s12, 12, "Model Architecture & Parameter Breakdown",
        "SLIDE CONCEPT:\n"
        "Presenting the verified PyTorch architecture implemented in melodyloop/model.py.\n\n"
        "PARAMETER BREAKDOWN PROOF:\n"
        "Let us verify the exact 167,104 parameter count:\n"
        "1. Embeddings: 128*64 (pitch) + 32*32 (duration) + 32*32 (step) = 8,192 + 1,024 + 1,024 = 10,240 parameters.\n"
        "2. LSTM Layer: An LSTM has 4 gates (forget, input, candidate, output). Each gate has weight matrices for input x (128*128), hidden h (128*128), and 2 bias vectors (128 each). 4 * (16384 + 16384 + 256) = 132,096 parameters.\n"
        "3. Prediction Heads: Pitch head is Linear(128->128): 128*128 + 128 = 16,512. Duration head is Linear(128->32): 128*32 + 32 = 4,128. Step head is Linear(128->32): 128*32 + 32 = 4,128. Sum of heads = 24,768 parameters.\n"
        "Total Parameters = 10,240 + 132,096 + 24,768 = 167,104 trainable parameters.\n"
        "Verified by test_model_parameter_count.\n\n"
        "TRANSITION:\n"
        "Now let us examine how the network optimizes these 167k parameters during training."
    )

    # ==============================================================================
    # SLIDE 13: HOW THE LSTM IS TRAINED (Chapter 9)
    # ==============================================================================
    s13 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s13)
    builder.add_header(s13, "Chapter 09 • Training Dynamics", "Multi-Task Optimization & Training Dynamics", 13)

    # Left: Training Loop Process Flow Card
    builder.add_card(s13, 0.8, 1.7, 5.7, 5.1)
    b_l = s13.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.3), Inches(4.7))
    tf_l = b_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "THE RECURRENT TRAINING CYCLE (train.py)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    loop_steps = [
        ("1. Batch Ingestion:", " Mini-batch of 64 sequences (shape: [64, 32, 3]) transferred to GPU with non_blocking=True and pinned memory."),
        ("2. Forward Propagation:", " Inputs pass through embeddings, LSTM, and heads to produce unnormalized logits: L_p [64, 128], L_d [64, 32], L_s [64, 32]."),
        ("3. Multi-Task Loss Calculation:", " Three separate cross-entropy losses are computed against target indices and summed equally: L_total = L_p + L_d + L_s."),
        ("4. Backpropagation Through Time (BPTT):", " loss.backward() unrolls gradients backward across all 32 time steps."),
        ("5. Gradient Clipping:", " torch.nn.utils.clip_grad_norm_(max_norm=1.0) prevents exploding gradients during sudden transitions."),
        ("6. Parameter Update:", " Adam optimizer (lr=0.001, weight_decay=1e-5) updates all 167k parameters using running first & second moments.")
    ]
    for step, desc in loop_steps:
        p_s = tf_l.add_paragraph()
        p_s.space_before = Pt(5)
        r1 = p_s.add_run()
        r1.text = step + " "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = IVORY_TEXT
        r2 = p_s.add_run()
        r2.text = desc
        r2.font.size = Pt(9.0)
        r2.font.color.rgb = MUTED_TEXT

    # Right: Hyperparameters & Loss Objective Card
    builder.add_card(s13, 6.8, 1.7, 5.7, 5.1)
    b_r = s13.shapes.add_textbox(Inches(7.0), Inches(1.85), Inches(5.3), Inches(4.7))
    tf_r = b_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "HYPERPARAMETER SPECIFICATION & HARDWARE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    specs = [
        ("Compute Device:", " NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM)"),
        ("PyTorch Environment:", " PyTorch 2.13.0+cu126 (CUDA 12.6 Backend)"),
        ("Batch Size:", " 64 sequences per iteration (1,562 batches / epoch)"),
        ("Sequence Length:", " 32 note events (sliding window, stride = 4)"),
        ("Optimizer:", " Adam (Learning Rate = 1e-3, Weight Decay = 1e-5)"),
        ("Loss Function:", " Multi-Task Cross-Entropy (Pitch, Duration, Step)"),
        ("Regularization:", " Dropout(p=0.1) after embeddings + Gradient Clipping (1.0)"),
        ("Throughput:", " ~91 batches/sec (17.2 seconds per epoch)")
    ]
    for lbl, val in specs:
        p_sp = tf_r.add_paragraph()
        p_sp.space_before = Pt(5)
        r1 = p_sp.add_run()
        r1.text = "• " + lbl + " "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = IVORY_TEXT
        r2 = p_sp.add_run()
        r2.text = val
        r2.font.size = Pt(9.0)
        r2.font.color.rgb = CYAN_ACCENT

    builder.attach_notes(s13, 13, "Multi-Task Optimization & Training Loop",
        "SLIDE CONCEPT:\n"
        "Detailing the optimization cycle, gradient clipping, loss formulation, and hardware execution parameters.\n\n"
        "KEY CONCEPTS:\n"
        "- Joint Multi-Task Loss: Pitch, duration, and step time each have distinct classification distributions. Cross-entropy measures the negative log-likelihood of the ground-truth token. We sum all three equally.\n"
        "- Gradient Clipping: Because recurrent networks involve repeated matrix products, sudden large gradients can destabilize training. We enforce a hard norm clip of 1.0 using clip_grad_norm_.\n"
        "- Hardware Efficiency: On our laptop RTX 3050 GPU, the model achieves 91 batches per second, running an entire 100,000-sequence epoch in only 17.2 seconds.\n\n"
        "TRANSITION:\n"
        "Let us examine the empirical training loss curves and why early stopping selected epoch 7 as our best checkpoint."
    )

    # ==============================================================================
    # SLIDE 14: TRAINING RESULTS & CHECKPOINT SELECTION (Chapter 9)
    # ==============================================================================
    s14 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s14)
    builder.add_header(s14, "Chapter 09 • Empirical Results", "Empirical Training Curves & Early Stopping Checkpoint Selection", 14)

    # Loss curves figure
    img_path = ASSETS_DIR / "fig_training_loss.png"
    s14.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(11.733), Inches(3.6))

    # Bottom 3 Metric Cards
    metrics = [
        ("Best Validation Checkpoint", "Epoch 07 (Val Loss: 5.9151)\nPitch: 3.320 | Dur: 1.223 | Step: 1.372\nSurpasses baseline model best val loss (6.1791) by -0.2640 points.", GREEN_ACCENT),
        ("Training Loss Trajectory", "6.3280 (Epoch 1) → 4.9121 (Epoch 15)\nSteady monotonic reduction (-1.4159 points) proves effective backpropagation and gradient descent optimization.", CYAN_ACCENT),
        ("Generalization & Early Stopping", "Patience = 8 Epochs Triggered at Ep 15\nValidation loss stabilized around ~5.92–6.03 while train loss continued falling. Best checkpoint was preserved to prevent overfitting.", GOLD_ACCENT)
    ]
    for idx, (m_title, m_desc, col) in enumerate(metrics):
        builder.add_card(s14, 0.8 + idx * 4.0, 5.35, 3.733, 1.55)
        box = s14.shapes.add_textbox(Inches(0.95 + idx * 4.0), Inches(5.4), Inches(3.433), Inches(1.45))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = m_title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = m_desc
        p_d.font.size = Pt(8.8)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(3)

    builder.attach_notes(s14, 14, "Empirical Training Curves & Checkpoint Selection",
        "SLIDE CONCEPT:\n"
        "Analyzing the actual epoch-by-epoch training history recorded in artifacts/logs/training_expanded.log.\n\n"
        "SCIENTIFIC OBSERVATION:\n"
        "Notice the classic divergence between training loss and validation loss:\n"
        "- From Epoch 1 to Epoch 7, both training loss and validation loss drop rapidly (train loss from 6.328 to 5.276, validation loss from 6.239 to 5.915).\n"
        "- After Epoch 7, training loss continues to fall steadily down to 4.912 at Epoch 15. However, validation loss ceases improving and begins a slight upward drift (5.918 -> 5.957 -> 6.038).\n"
        "- This divergence demonstrates classic over-parameterization and memorization of training sequences. Because our trainer implemented early stopping with a patience of 8 epochs, training halted automatically at epoch 15.\n"
        "- The best model saved on disk is strictly the epoch 7 checkpoint (val loss 5.9151), completely preventing overfitted weights from being deployed.\n\n"
        "TRANSITION:\n"
        "Let us examine how checkpoints are serialized and preserved on disk."
    )

    # ==============================================================================
    # SLIDE 15: CHECKPOINT SERIALIZATION (Chapter 9)
    # ==============================================================================
    s15 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s15)
    builder.add_header(s15, "Chapter 09 • Model Persistence", "Checkpoint Serialization & Inference Resumption", 15)

    # Left: Checkpoint File Structure Card
    builder.add_card(s15, 0.8, 1.7, 5.7, 5.1)
    b_l = s15.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.3), Inches(4.7))
    tf_l = b_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "CHECKPOINT PAYLOAD ANATOMY (.pt)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    ckpt_items = [
        ("model_state_dict:", " Complete dictionary of all learned PyTorch tensor weight matrices (167,104 parameters)."),
        ("optimizer_state_dict:", " Running Adam first (m) and second (v) gradient momentum vectors for seamless training resumption."),
        ("epoch:", " Integer recording the exact completed epoch index (e.g. Epoch 7)."),
        ("train_loss & val_loss:", " Floating-point loss values at checkpoint creation (val_loss: 5.9151)."),
        ("metrics:", " Multi-task breakdown dictionary (loss_pitch, loss_dur, loss_step)."),
        ("config:", " Serialized dictionary of all hyperparameters (hidden_dim=128, seq_length=32) for zero-mismatch reloading.")
    ]
    for lbl, desc in ckpt_items:
        p_c = tf_l.add_paragraph()
        p_c.space_before = Pt(6)
        r1 = p_c.add_run()
        r1.text = "• " + lbl + " "
        r1.font.name = "Consolas"
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = GOLD_ACCENT
        r2 = p_c.add_run()
        r2.text = desc
        r2.font.size = Pt(9.0)
        r2.font.color.rgb = IVORY_TEXT

    # Right: Preserved Artifacts on Disk Card
    builder.add_card(s15, 6.8, 1.7, 5.7, 5.1)
    b_r = s15.shapes.add_textbox(Inches(7.0), Inches(1.85), Inches(5.3), Inches(4.7))
    tf_r = b_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "VERIFIED ARTIFACT STORAGE & VERSIONING"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    files = [
        ("best_model_expanded.pt", "Epoch 7 Best Model", "Val Loss: 5.9151 | Trained on 962 files, 100k sequences. Primary deployment checkpoint.", GREEN_ACCENT),
        ("latest_model_expanded.pt", "Epoch 15 Latest Model", "Val Loss: 6.0386 | Final epoch before early stopping. Preserved for training recovery.", ROYAL_BLUE),
        ("best_model_v1_baseline.pt", "Epoch 4 Baseline Model", "Val Loss: 6.1791 | Original 13-performance model safely preserved for comparative benchmark.", MUTED_TEXT),
        ("training_expanded.log", "Persistent Training Record", "Complete timestamped log of all batches, running averages, and validation metrics.", CYAN_ACCENT)
    ]
    for fname, sub, desc, col in files:
        p_f = tf_r.add_paragraph()
        p_f.space_before = Pt(6)
        r1 = p_f.add_run()
        r1.text = "📁 " + fname + "\n"
        r1.font.name = "Consolas"
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = col
        r2 = p_f.add_run()
        r2.text = f"{sub} — {desc}"
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = IVORY_TEXT

    builder.attach_notes(s15, 15, "Checkpoint Serialization & Persistence",
        "SLIDE CONCEPT:\n"
        "Explaining how model weights, optimizer states, and configuration metadata are serialized into PyTorch .pt binaries.\n\n"
        "KEY ENGINEERING PRACTICES:\n"
        "- Never overwrite working baselines: We explicitly backed up the original baseline checkpoint to best_model_v1_baseline.pt so we can run direct side-by-side musical comparisons.\n"
        "- Self-contained configuration: The checkpoint dictionary stores the exact hyperparameters used during training. When app.py or generate.py loads the checkpoint, it reads hidden_dim directly from the file, preventing architectural mismatch exceptions.\n"
        "- State restoration: The script train.py --resume automatically restores both model weights and the Adam optimizer's internal momentum states, enabling training to pick up exactly where it was interrupted.\n\n"
        "TRANSITION:\n"
        "Now let us examine how the trained model autoregressively generates new musical compositions."
    )

    # ==============================================================================
    # SLIDE 16: AUTOREGRESSIVE GENERATION (Chapter 11)
    # ==============================================================================
    s16 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s16)
    builder.add_header(s16, "Chapter 11 • Generation & Sampling", "Autoregressive Music Generation & Controllable Sampling", 16)

    img_path = ASSETS_DIR / "fig_autoregressive_loop.png"
    s16.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(11.733), Inches(3.6))

    # Bottom 3 Cards: Temperature, Top-K, and Seed Continuation
    cards = [
        ("Temperature Scaling (T = 0.6)", "P(y_i) = exp(z_i / T) / Σ exp(z_j / T)\n• Low Temp (T=0.4–0.6): Sharpens distribution around high-confidence notes; prevents erratic dissonance.\n• High Temp (T=1.2): Flattens distribution; encourages exploration at the cost of coherence.", CYAN_ACCENT),
        ("Top-K Candidate Truncation (k = 5)", "Sorts predicted logits, retains only top k=5 most probable candidates, sets all others to -inf, and renormalizes with Softmax.\nCompletely eliminates tail probability hallucinations and unnatural pitch jumps.", GOLD_ACCENT),
        ("Dual Generation Modes", "• Free Generation: Generates from scratch using an initial uniform middle-register seed buffer.\n• Seeded Continuation: Ingests 32 notes from real classical MIDI (e.g. Schubert, Chopin) and generates an original LSTM continuation.", ROYAL_BLUE)
    ]
    for idx, (c_title, c_desc, col) in enumerate(cards):
        builder.add_card(s16, 0.8 + idx * 4.0, 5.35, 3.733, 1.55)
        box = s16.shapes.add_textbox(Inches(0.95 + idx * 4.0), Inches(5.4), Inches(3.433), Inches(1.45))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = c_desc
        p_d.font.size = Pt(8.8)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(3)

    builder.attach_notes(s16, 16, "Autoregressive Sampling & Top-K Filtering",
        "SLIDE CONCEPT:\n"
        "Explaining the mathematical mechanics of autoregressive generation and stochastic sampling controls.\n\n"
        "TECHNICAL BREAKDOWN:\n"
        "How Autoregression Works:\n"
        "1. The model receives a rolling context window of 32 note events.\n"
        "2. The model outputs unnormalized logits for pitch, duration, and step.\n"
        "3. Sampling with Temperature: Instead of greedily picking the argmax (which causes the network to loop the exact same note repeatedly), we divide logits by temperature T and apply Softmax.\n"
        "4. Top-K Filtering: Greedily sampling from the full 128 pitch vocabulary risks picking extreme low-probability notes (e.g. jumping from pitch 60 to pitch 120). By filtering for only the Top-K=5 candidates, we guarantee that every sampled note is among the model's top 5 most confident musical hypotheses.\n"
        "5. Rolling Update: The sampled note is appended to the buffer, the oldest note is evicted, and the loop repeats for N notes.\n\n"
        "TRANSITION:\n"
        "Now let us see how these discrete tokens are rendered into playable sound."
    )

    # ==============================================================================
    # SLIDE 17: AUDIO RENDERING & SYNTHESIS (Chapter 12)
    # ==============================================================================
    s17 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s17)
    builder.add_header(s17, "Chapter 12 • Audio Synthesis", "Audio Rendering: Additive Synthesis & ADSR Enveloping", 17)

    img_path = ASSETS_DIR / "fig_audio_synthesis.png"
    s17.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(11.733), Inches(3.6))

    # Bottom 3 Cards: Additive Synthesis Formula, ADSR Envelope, and MIDI Export
    cards = [
        ("Additive Harmonic Synthesis", "Real piano tones contain harmonic overtones. melodyloop/audio.py synthesizes notes via:\n  s(t) = 0.60 sin(2π f0 t) + 0.25 sin(4π f0 t) + 0.15 sin(6π f0 t)\nFundamental f0 + 2nd harmonic (2f0) + 3rd harmonic (3f0).", CYAN_ACCENT),
        ("ADSR Amplitude Envelope", "To prevent harsh clicking artifacts at note onset and release, an exponential envelope is applied:\n  E(t) = exp(-3.0 t / duration)\nIncludes 5ms linear attack ramp and 10ms smooth release decay.", GOLD_ACCENT),
        ("Dual Export Pipeline", "• MIDI File (.mid): Built via mido, contains raw Note On/Off channel events and microsecond tempo (120 BPM).\n• WAV File (.wav): 44.1 kHz 16-bit PCM waveform rendered entirely in pure NumPy/SciPy without external soundfonts.", ROYAL_BLUE)
    ]
    for idx, (c_title, c_desc, col) in enumerate(cards):
        builder.add_card(s17, 0.8 + idx * 4.0, 5.35, 3.733, 1.55)
        box = s17.shapes.add_textbox(Inches(0.95 + idx * 4.0), Inches(5.4), Inches(3.433), Inches(1.45))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = c_desc
        p_d.font.size = Pt(8.8)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(3)

    builder.attach_notes(s17, 17, "Audio Rendering & Synthesis",
        "SLIDE CONCEPT:\n"
        "Explaining the physics and DSP mathematics behind converting discrete tokens into 44.1 kHz WAV audio.\n\n"
        "TECHNICAL DETAILS:\n"
        "- Pure sine waves sound like synthetic telephone test tones, not piano notes.\n"
        "- An acoustic piano string vibrates in multiple modes: the fundamental frequency f0, plus integer harmonics 2*f0, 3*f0, etc. In melodyloop/audio.py, we implement additive synthesis: 60% energy in the fundamental, 25% in the second harmonic (octave), and 15% in the third harmonic (fifth).\n"
        "- Amplitude Envelope: In an acoustic piano, when the hammer strikes the string, amplitude peaks instantly and decays exponentially. We multiply the composite wave by exp(-3.0 * t / duration), with a 5 millisecond attack and 10 millisecond release to eliminate boundary clicking.\n"
        "- This entire DSP pipeline is self-contained in pure NumPy and SciPy—requiring zero external soundfonts or third-party audio drivers.\n\n"
        "TRANSITION:\n"
        "Now let us see the working Streamlit web application where users can interact with this pipeline."
    )

    # ==============================================================================
    # SLIDE 18: STREAMLIT WEB APPLICATION (Chapters 11, 12)
    # ==============================================================================
    s18 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s18)
    builder.add_header(s18, "Chapters 11, 12 • Interactive Deployment", "Interactive Deployment: Streamlit Web Dashboard", 18)

    # Left: Piano Roll Visualizer
    img_path = ASSETS_DIR / "fig_piano_roll.png"
    s18.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(7.5), Inches(3.6))

    # Right: Dashboard Feature Cards
    builder.add_card(s18, 8.5, 1.65, 4.033, 3.6)
    box_r = s18.shapes.add_textbox(Inches(8.65), Inches(1.75), Inches(3.733), Inches(3.4))
    tf_r = box_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "STREAMLIT DASHBOARD (app.py)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    features = [
        ("Multi-Model Selector:", " Toggle between Expanded Model (v2: 962 Pieces, Val Loss: 5.9151) and Baseline Model (v1: 13 Pieces, Val Loss: 6.1791) in real time."),
        ("Interactive Piano-Roll:", " High-resolution Matplotlib timeline visually distinguishing human prompt notes (Gold) from LSTM continuations (Cyan)."),
        ("Live Audio Synthesis:", " Renders browser-playable HTML5 WAV previews without page reloading via st.audio."),
        ("Catalog Exploration:", " Browse and audition held-out real MAESTRO competition performances directly in the UI.")
    ]
    for lbl, desc in features:
        p_f = tf_r.add_paragraph()
        p_f.space_before = Pt(5)
        r1 = p_f.add_run()
        r1.text = "• " + lbl + " "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = IVORY_TEXT
        r2 = p_f.add_run()
        r2.text = desc
        r2.font.size = Pt(8.8)
        r2.font.color.rgb = MUTED_TEXT

    # Bottom Full-width Card: Commands & Architecture
    builder.add_card(s18, 0.8, 5.4, 11.733, 1.5)
    box_b = s18.shapes.add_textbox(Inches(1.0), Inches(5.45), Inches(11.333), Inches(1.35))
    tf_b = box_b.text_frame
    tf_b.word_wrap = True

    p = tf_b.paragraphs[0]
    p.text = "EXECUTION COMMAND & CACHED INFERENCE DESIGN"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    p_cmd = tf_b.add_paragraph()
    p_cmd.space_before = Pt(3)
    p_cmd.text = "Command: streamlit run app.py  |  Default Port: http://localhost:8501"
    p_cmd.font.name = "Consolas"
    p_cmd.font.size = Pt(10)
    p_cmd.font.color.rgb = CYAN_ACCENT

    p_arch = tf_b.add_paragraph()
    p_arch.space_before = Pt(2)
    p_arch.text = "The application implements st.cache_resource for checkpoint weight loading and st.cache_data for the MAESTRO catalog, ensuring the neural network is never redundantly retrained or reloaded upon user interactions."
    p_arch.font.size = Pt(9.0)
    p_arch.font.color.rgb = IVORY_TEXT

    builder.attach_notes(s18, 18, "Streamlit Web Dashboard",
        "SLIDE CONCEPT:\n"
        "Demonstrating the deployed user interface and real-time visualization features of app.py.\n\n"
        "KEY FEATURES TO DEMONSTRATE:\n"
        "- The application is built using Streamlit and renders a dark DAW-like interface.\n"
        "- The sidebar contains a checkpoint selector allowing immediate A/B testing: you can listen to a melody generated by the baseline 13-performance model, then immediately switch to the expanded 962-performance model.\n"
        "- The piano-roll visualizer clearly separates the human seed phrase (in gold) from the LSTM continuation (in cyan), with a vertical red boundary marker at t=6.0 seconds.\n"
        "- Audio synthesis runs in-memory: clicking 'Generate' synthesizes 80 notes into a WAV file in ~0.5 seconds and passes it directly to the browser audio player.\n\n"
        "TRANSITION:\n"
        "Now let us examine the quantitative and qualitative evaluation results: does the music actually sound better?"
    )

    # ==============================================================================
    # SLIDE 19: WHAT IMPROVED & WHAT NEEDS WORK (Chapters 1, 9, 11, 12)
    # ==============================================================================
    s19 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s19)
    builder.add_header(s19, "Chapters 01, 09, 11, 12 • Evaluation & Benchmarks", "Quantitative & Qualitative Evaluation: Baseline vs. Expanded", 19)

    # Left: Evaluation Chart
    img_path = ASSETS_DIR / "fig_evaluation_comparison.png"
    s19.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.65), Inches(6.8), Inches(3.5))

    # Right: Results Table Card
    builder.add_card(s19, 7.8, 1.65, 4.733, 3.5)
    box_r = s19.shapes.add_textbox(Inches(7.95), Inches(1.75), Inches(4.433), Inches(3.3))
    tf_r = box_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "EMPIRICAL BENCHMARK COMPARISON"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    table_data = [
        ("Metric", "Baseline (13)", "Expanded (962)", "Real Scriabin"),
        ("Val Loss:", "6.1791", "5.9151 (-0.26)", "N/A (Ground Truth)"),
        ("Repetition Rate:", "17.7%", "10.1% (-43%)", "0.0%"),
        ("Avg Pitch Jump:", "6.48 st", "1.49 st", "6.47 st"),
        ("Avg Note Duration:", "0.06s (Clicks)", "0.34s (Piano)", "0.48s"),
        ("Avg Step Interval:", "0.05s", "0.25s", "0.21s"),
        ("Auditory Coherence:", "Erratic bursts", "Singable soprano", "Virtuosic Op.63")
    ]
    for row in table_data:
        p_row = tf_r.add_paragraph()
        p_row.space_before = Pt(3)
        if row[0] == "Metric":
            p_row.text = f"{row[0]:<18} | {row[1]:<13} | {row[2]}"
            p_row.font.bold = True
            p_row.font.size = Pt(8.5)
            p_row.font.color.rgb = CYAN_ACCENT
        else:
            r1 = p_row.add_run()
            r1.text = f"{row[0]:<18} "
            r1.font.bold = True
            r1.font.size = Pt(8.5)
            r1.font.color.rgb = IVORY_TEXT
            r2 = p_row.add_run()
            r2.text = f"{row[1]} → {row[2]}"
            r2.font.size = Pt(8.5)
            r2.font.color.rgb = GOLD_ACCENT if "(-" in row[2] or "Piano" in row[2] else MUTED_TEXT

    # Bottom Card: Honest Scientific Assessment (Strengths & Remaining Limitations)
    builder.add_card(s19, 0.8, 5.3, 11.733, 1.6)
    box_b = s19.shapes.add_textbox(Inches(1.0), Inches(5.35), Inches(11.333), Inches(1.45))
    tf_b = box_b.text_frame
    tf_b.word_wrap = True

    p = tf_b.paragraphs[0]
    p.text = "HONEST SCIENTIFIC APPRAISAL: WHAT IMPROVED VS. REMAINING LIMITATIONS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    bullets = [
        "What Substantially Improved: The baseline model suffered from duration collapse (predicting 0.06s staccato clicks). The expanded model learned realistic human pacing (0.34s duration, 0.25s step time) closely matching real Scriabin ground truth (0.48s/0.21s). Monotone note repetitions decreased by 43%.",
        "Remaining Architectural Limitations: An LSTM lacks multi-track polyphonic counterpoint and global hierarchical phrase structure (A-B-A sonata form). Long generations (>150 notes) tend to wander tonally without global cadences.",
        "Crucial Insight: Lower validation loss correlates with valid local transitions, but does NOT guarantee long-term human aesthetic perfection. Domain-specific qualitative evaluation remains essential."
    ]
    for b in bullets:
        p_b = tf_b.add_paragraph()
        p_b.space_before = Pt(2)
        p_b.text = "• " + b
        p_b.font.size = Pt(8.8)
        p_b.font.color.rgb = IVORY_TEXT

    builder.attach_notes(s19, 19, "Quantitative & Qualitative Evaluation",
        "SLIDE CONCEPT:\n"
        "An honest, technically rigorous evaluation of musical output comparing baseline, expanded, and ground-truth Scriabin performances.\n\n"
        "KEY FINDINGS TO HIGHLIGHT:\n"
        "1. The Duration Fix: In the baseline model, note durations collapsed to 0.06s—sounding like rapid machine-gun clicks. The expanded model learned realistic piano note durations (0.34s) and step intervals (0.25s), aligning closely with real human performances (0.48s duration, 0.21s step).\n"
        "2. Monotone Repetition: The baseline model repeated identical pitches 17.7% of the time. The expanded model dropped repetition to 10.1%—a 43% relative reduction.\n"
        "3. Pitch Smoothness: The baseline model jumped erratically across the keyboard (average jump 6.48 semitones). The expanded model settled into smooth step-wise motion (average jump 1.49 semitones), producing lyrical singing melodies.\n"
        "4. Limitations: An LSTM with 128 hidden units cannot learn 4-part Bach counterpoint or Beethoven sonata form. After 40 to 60 notes, it wanders tonally. We do not claim human-level mastery; we demonstrate a working, verifiable sequence model.\n\n"
        "TRANSITION:\n"
        "Let us summarize our key engineering takeaways."
    )

    # ==============================================================================
    # SLIDE 20: KEY TECHNICAL TAKEAWAYS (Conclusion)
    # ==============================================================================
    s20 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s20)
    builder.add_header(s20, "Summary & Conclusion", "Key Technical Takeaways & Engineering Conclusions", 20)

    # 4 Key Takeaway Cards
    takeaways = [
        ("1. Discrete Symbolic Representation", "Tokenizing MIDI into discrete 3-tuples (Pitch, Duration, Step) reduced data dimensionality by orders of magnitude compared to continuous waveforms, enabling effective recurrent learning on standard consumer hardware.", CYAN_ACCENT),
        ("2. Memory-Bounded Data Engineering", "Transitioning from unconstrained Python lists to compact uint8 tensors and multi-process persistent caching eliminated the 13-file bottleneck, expanding training to 962 performances without exceeding 4 GB GPU VRAM.", GOLD_ACCENT),
        ("3. Gated Memory Prevents Vanishing Gradients", "The LSTM's constant error carousel additively routed gradient highways across 32 time steps, enabling the network to learn rhythmic pacing, pitch intervals, and multi-task predictions.", ROYAL_BLUE),
        ("4. Deployment & Evaluation Completeness", "A complete end-to-end artifact was delivered: PyTorch checkpoints, a Streamlit interactive web application, NumPy additive DSP synthesis, and rigorous quantitative musical benchmarks.", GREEN_ACCENT)
    ]
    for idx, (t_title, t_desc, col) in enumerate(takeaways):
        builder.add_card(s20, 0.8, 1.7 + idx * 1.25, 11.733, 1.1)
        box = s20.shapes.add_textbox(Inches(1.0), Inches(1.75 + idx * 1.25), Inches(11.333), Inches(0.95))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = t_title
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = t_desc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = IVORY_TEXT
        p_d.space_before = Pt(3)

    # Thank you / Questions Callout Card
    builder.add_card(s20, 0.8, 6.25, 11.733, 0.65, bg_color=RGBColor(24, 38, 74), border_color=CYAN_ACCENT)
    box_q = s20.shapes.add_textbox(Inches(1.0), Inches(6.32), Inches(11.333), Inches(0.5))
    tf_q = box_q.text_frame
    p_q = tf_q.paragraphs[0]
    p_q.text = "Thank you for your time. I welcome questions regarding the implementation, architecture, and evaluation."
    p_q.font.name = FONT_TITLE
    p_q.font.size = Pt(11)
    p_q.font.bold = True
    p_q.font.color.rgb = CYAN_ACCENT

    builder.attach_notes(s20, 20, "Key Technical Takeaways",
        "CLOSING TALK:\n"
        "In conclusion, MelodyLoop successfully demonstrates the entire lifecycle of a deep learning sequence-modeling system:\n"
        "1. We took raw, expressive classical piano performances and engineered a discrete 3-tuple symbolic tokenization that captures pitch, duration, and step interval.\n"
        "2. We diagnosed and resolved the early data bottleneck, scaling the pipeline across 962 MAESTRO performances (5.66M notes) using compact uint8 tensor datasets.\n"
        "3. We trained a 167k-parameter multi-head LSTM from scratch, achieving a best validation loss of 5.9151 at epoch 7.\n"
        "4. We deployed the system into an interactive Streamlit application with additive audio synthesis and proved through quantitative metrics that expanded training fixed rhythmic duration collapse.\n\n"
        "Thank you, Professor. I am now ready to take your questions."
    )

    # ==============================================================================
    # APPENDIX SLIDE 21 (VIVA A): DATA & REPRESENTATION (Chapter 19)
    # ==============================================================================
    s21 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s21)
    builder.add_header(s21, "Appendix • Viva Defense Prep A", "Viva Defense: Data Representation & Preprocessing", 21)

    qa_a = [
        ("Q: Why train on symbolic MIDI instead of raw audio waveforms like MP3 or WAV?",
         "A: Audio waveforms require predicting 44,100 continuous 16-bit floating-point samples per second, demanding massive compute and resulting in acoustic noise. MIDI abstracts music into discrete symbolic event tokens (pitch, duration, step). This allows us to frame music as a natural sequence-modeling problem using categorical Cross-Entropy loss and token embeddings.", CYAN_ACCENT),
        ("Q: Why are there 128 MIDI note numbers if a standard piano only has 88 keys?",
         "A: The physical acoustic piano keyboard spans from A0 (MIDI 21) to C8 (MIDI 108). The MIDI protocol is a 7-bit standard (2^7 = 128 integers, from 0 to 127). The extra note numbers represent sub-audio pitches (0–20) and ultra-high registers (109–127) used by organs, synthesizers, and microtonal controllers.", GOLD_ACCENT),
        ("Q: How does the model represent simultaneous chords or polyphonic notes?",
         "A: Through the step interval s. If two notes are struck simultaneously in a chord (e.g. C4 and G4), the time delta between their start times is 0.0 seconds. The quantizer maps 0.0s to step_bin = 0. The model plays the first note, immediately advances 0 steps, and triggers the second note concurrently.", GREEN_ACCENT)
    ]
    for idx, (q, a, col) in enumerate(qa_a):
        builder.add_card(s21, 0.8, 1.7 + idx * 1.7, 11.733, 1.55)
        box = s21.shapes.add_textbox(Inches(1.0), Inches(1.78 + idx * 1.7), Inches(11.333), Inches(1.4))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p_q = tf.paragraphs[0]
        p_q.text = q
        p_q.font.size = Pt(11)
        p_q.font.bold = True
        p_q.font.color.rgb = col

        p_a = tf.add_paragraph()
        p_a.space_before = Pt(3)
        p_a.text = a
        p_a.font.size = Pt(9.5)
        p_a.font.color.rgb = IVORY_TEXT

    builder.attach_notes(s21, 21, "Viva Prep A — Data & Representation",
        "VIVA QUESTION GUIDELINES:\n"
        "Focus on technical precision. If asked about quantization bounds, explain that min_duration=0.05s prevents divide-by-zero artifacts and captures the fastest 32nd notes, while max_duration=4.0s captures sustained pedal chords.\n"
        "If asked about memory bounds, explain that storing sequences as np.uint8 instead of np.int64 reduced the in-memory footprint from 77 MB to 9.6 MB, allowing all 100k sequences to live in RAM with zero garbage collection lag."
    )

    # ==============================================================================
    # APPENDIX SLIDE 22 (VIVA B): LSTM MECHANICS & TRAINING DYNAMICS (Chapter 19)
    # ==============================================================================
    s22 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s22)
    builder.add_header(s22, "Appendix • Viva Defense Prep B", "Viva Defense: LSTM Architecture & Training Dynamics", 22)

    qa_b = [
        ("Q: Why does the LSTM cell state prevent vanishing gradients while vanilla RNNs fail?",
         "A: In a vanilla RNN, backpropagation through time computes ∂h_T/∂h_0 by repeatedly multiplying by the recurrent weight matrix W, causing gradients to vanish exponentially. In an LSTM, the cell state update C_t = f_t ⊙ C_(t-1) + i_t ⊙ C~_t is additive. The gradient ∂C_t/∂C_(t-1) = f_t. If the forget gate is near 1, gradients flow indefinitely across time without exponential decay.", CYAN_ACCENT),
        ("Q: Why did early stopping select Epoch 7 rather than the final Epoch 15?",
         "A: Training loss measures performance on the training data, while validation loss measures generalization on unseen performances. As shown in our training curves, validation loss reached its minimum of 5.9151 at Epoch 7. In subsequent epochs, validation loss drifted upward to 6.0386 while train loss continued dropping, indicating over-parameterized memorization. Epoch 7 was preserved to ensure optimal generalization.", GOLD_ACCENT),
        ("Q: Why multi-task cross-entropy instead of Mean Squared Error (MSE)?",
         "A: Pitch, duration, and step bins are categorical tokens, not continuous scalars. In music, pitch 60 (Middle C) and pitch 61 (C#) are musically dissonant despite having a numerical difference of only 1. MSE assumes numerical distance equates to musical error. Cross-entropy evaluates the probability distribution over all discrete choices without imposing a false Euclidean distance metric.", ROYAL_BLUE)
    ]
    for idx, (q, a, col) in enumerate(qa_b):
        builder.add_card(s22, 0.8, 1.7 + idx * 1.7, 11.733, 1.55)
        box = s22.shapes.add_textbox(Inches(1.0), Inches(1.78 + idx * 1.7), Inches(11.333), Inches(1.4))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p_q = tf.paragraphs[0]
        p_q.text = q
        p_q.font.size = Pt(11)
        p_q.font.bold = True
        p_q.font.color.rgb = col

        p_a = tf.add_paragraph()
        p_a.space_before = Pt(3)
        p_a.text = a
        p_a.font.size = Pt(9.5)
        p_a.font.color.rgb = IVORY_TEXT

    builder.attach_notes(s22, 22, "Viva Prep B — LSTM Mechanics & Training Dynamics",
        "VIVA QUESTION GUIDELINES:\n"
        "Key point on MSE vs Cross-Entropy:\n"
        "Professors frequently ask: 'Why treat duration as a classification problem instead of regression with MSE?'\n"
        "Answer: Duration in music is rhythmic and discrete (e.g. quarter notes, eighth notes, triplets). Regression often predicts muddy average values (e.g. 0.372s) that do not correspond to musical rhythmic subdivisions. Classification with 32 bins allows the model to learn multimodal probability peaks on standard rhythmic subdivisions."
    )

    # ==============================================================================
    # APPENDIX SLIDE 23 (VIVA C): GENERATION & SYNTHESIS (Chapter 19)
    # ==============================================================================
    s23 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s23)
    builder.add_header(s23, "Appendix • Viva Defense Prep C", "Viva Defense: Autoregressive Generation & Synthesis", 23)

    qa_c = [
        ("Q: What is sampling temperature, and what happens at T -> 0 vs T -> inf?",
         "A: Temperature T scales the raw logits z before the softmax function: P(y_i) = exp(z_i / T) / Σ exp(z_j / T). As T → 0, the distribution approaches an argmax one-hot vector (greedy decoding), resulting in deterministic but repetitive loops. As T → ∞, logits become equal and the distribution approaches uniform random noise. Setting T = 0.6 balances novelty and harmonic coherence.", CYAN_ACCENT),
        ("Q: Why does Top-K filtering (k = 5) dramatically improve musical output?",
         "A: In standard temperature sampling, low-probability tail tokens still retain a small chance of being sampled. In a vocabulary of 128 pitches, sampling a random tail token causes jarring out-of-key dissonance or unnatural 4-octave jumps. Top-K filtering sets all logits outside the top 5 candidates to -inf, guaranteeing that every generated note is among the network's most musically confident predictions.", GOLD_ACCENT),
        ("Q: How does the additive synthesizer synthesize audio without an external soundfont?",
         "A: An acoustic piano note is modeled as a sum of sinusoidal harmonics: s(t) = Σ a_k sin(2π k f_0 t) where f_0 = 440 × 2^((p - 69)/12). We compute the fundamental (60%), 2nd harmonic (25%), and 3rd harmonic (15%). Multiplying by an exponential decay envelope exp(-3t / dur) creates the characteristic percussive piano timbre in pure NumPy/SciPy.", GREEN_ACCENT)
    ]
    for idx, (q, a, col) in enumerate(qa_c):
        builder.add_card(s23, 0.8, 1.7 + idx * 1.7, 11.733, 1.55)
        box = s23.shapes.add_textbox(Inches(1.0), Inches(1.78 + idx * 1.7), Inches(11.333), Inches(1.4))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p_q = tf.paragraphs[0]
        p_q.text = q
        p_q.font.size = Pt(11)
        p_q.font.bold = True
        p_q.font.color.rgb = col

        p_a = tf.add_paragraph()
        p_a.space_before = Pt(3)
        p_a.text = a
        p_a.font.size = Pt(9.5)
        p_a.font.color.rgb = IVORY_TEXT

    builder.attach_notes(s23, 23, "Viva Prep C — Generation & Audio Synthesis",
        "VIVA QUESTION GUIDELINES:\n"
        "Explain that temperature and top-k are orthogonal sampling controls:\n"
        "- Top-k filters the candidate pool (eliminates impossible notes).\n"
        "- Temperature controls how flat or sharp the probability distribution is among those valid candidates.\n"
        "- Together, they eliminate both monotone looping (from argmax) and chaotic noise (from uniform sampling)."
    )

    # ==============================================================================
    # APPENDIX SLIDE 24 (VIVA D): TECHNICAL QUICK REFERENCE & MODEL CARD (Chapter 19)
    # ==============================================================================
    s24 = prs.slides.add_slide(builder.blank_layout)
    builder.set_background(s24)
    builder.add_header(s24, "Appendix • Technical Model Card", "MelodyLoop Technical Quick Reference & Model Card", 24)

    # 4 Cards summarizing the exact technical specs
    cards_d = [
        ("MODEL & ARCHITECTURE", [
            ("Model Type:", "MelodyLSTM Multi-Head Recurrent Network"),
            ("Trainable Parameters:", "167,104 float32 parameters"),
            ("Embeddings:", "Pitch (128->64), Dur (32->32), Step (32->32)"),
            ("Hidden Core:", "1-Layer LSTM, Hidden Dimension = 128"),
            ("Prediction Heads:", "3 Linear Heads (128, 32, 32 classes)")
        ], CYAN_ACCENT),
        ("DATASET & INGESTION", [
            ("Source Dataset:", "MAESTRO v3.0.0 (Google Magenta)"),
            ("Split Breakdown:", "962 Train (75.4%), 137 Val (10.7%), 177 Test (13.9%)"),
            ("Events Extracted:", "5,659,329 chronologically verified notes"),
            ("Training Sequences:", "100,000 sliding-window sequences (uint8)"),
            ("Validation Sequences:", "10,000 held-out sequences (uint8)")
        ], GOLD_ACCENT),
        ("TRAINING METRICS", [
            ("Hardware Used:", "NVIDIA GeForce RTX 3050 Laptop GPU (4 GB)"),
            ("Batch Size & Stride:", "Batch Size: 64, Seq Len: 32, Stride: 4"),
            ("Best Epoch & Loss:", "Epoch 07 | Best Val Loss: 5.9151"),
            ("Stopping Criterion:", "Early Stopping (Patience = 8 at Epoch 15)"),
            ("Training Speed:", "17.2 seconds per epoch (~91 batches/s)")
        ], ROYAL_BLUE),
        ("PROJECT COMMANDS", [
            ("Launch Web Dashboard:", "streamlit run app.py"),
            ("CLI Generation:", "python generate.py --checkpoint ... --length 80"),
            ("Comparative Evaluation:", "python evaluate_comparison.py"),
            ("Run Full Test Suite:", "python -m pytest -v (15/15 Passed)"),
            ("Checkpoint Location:", "artifacts/checkpoints/best_model_expanded.pt")
        ], GREEN_ACCENT)
    ]
    for idx, (c_title, items, col) in enumerate(cards_d):
        left = 0.8 + (idx % 2) * 6.0
        top = 1.7 + (idx // 2) * 2.6
        builder.add_card(s24, left, top, 5.733, 2.45)
        box = s24.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.12), Inches(5.433), Inches(2.25))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        for k, v in items:
            p_i = tf.add_paragraph()
            p_i.space_before = Pt(3)
            r1 = p_i.add_run()
            r1.text = "• " + k + " "
            r1.font.bold = True
            r1.font.size = Pt(9.0)
            r1.font.color.rgb = IVORY_TEXT
            r2 = p_i.add_run()
            r2.text = v
            r2.font.size = Pt(8.5)
            r2.font.color.rgb = MUTED_TEXT

    builder.attach_notes(s24, 24, "Technical Quick Reference Card",
        "SLIDE CONCEPT:\n"
        "A final cheat-sheet model card summarizing all verified numbers, dimensions, paths, and commands in one place for rapid reference during the viva defense."
    )

    # Save PowerPoint file
    prs.save(str(OUTPUT_PPTX))
    print(f"Successfully generated PowerPoint presentation -> {OUTPUT_PPTX}")

    # Generate Markdown Speaker Notes
    with open(NOTES_MD_PATH, "w", encoding="utf-8") as f:
        f.write("# MelodyLoop: Academic Presentation Speaker Notes\n\n")
        f.write("**Project:** MelodyLoop — Music Generation Using an LSTM  \n")
        f.write("**Target Audience:** Professor & Academic Project Evaluation Committee  \n")
        f.write("**Format:** 10–15 Minute Formal Project Defense (24 Slides)  \n")
        f.write("**Repository:** `https://github.com/Pankaj-Jhajhria/Music-Generation-using-LSTM-MelodyLoop-`  \n\n")
        f.write("---\n\n")

        for item in builder.all_notes:
            f.write(f"## Slide {item['slide_num']:02d}: {item['title']}\n\n")
            f.write(item["notes"] + "\n\n")
            f.write("---\n\n")

    print(f"Successfully generated Speaker Notes Markdown -> {NOTES_MD_PATH}")


if __name__ == "__main__":
    build_deck()
