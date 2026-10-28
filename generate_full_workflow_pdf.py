"""
Master PDF Generation Script for MelodyLoop
Compiles docs/MelodyLoop_Full_Workflow_Guide.pdf
Integrates all 20 chapters, 10 figures, tables, code blocks, and 55 viva Q&As.
"""

import sys
import time
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate

from pdf_canvas import NumberedCanvas
from pdf_builder_helpers import get_custom_stylesheet
from build_chapters_1_to_5 import (
    build_cover_and_toc,
    build_chapter_1,
    build_chapter_2,
    build_chapter_3,
    build_chapter_4,
    build_chapter_5,
)
from build_chapters_6_to_10 import (
    build_chapter_6,
    build_chapter_7,
    build_chapter_8,
    build_chapter_9,
    build_chapter_10,
)
from build_chapters_11_to_15 import (
    build_chapter_11,
    build_chapter_12,
    build_chapter_13,
    build_chapter_14,
    build_chapter_15,
)
from build_chapters_16_to_20 import (
    build_chapter_16,
    build_chapter_17,
    build_chapter_18,
    build_chapter_19,
    build_chapter_20,
)

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
PDF_OUTPUT_PATH = DOCS_DIR / "MelodyLoop_Full_Workflow_Guide.pdf"


def generate_pdf():
    print("=" * 70)
    print("Building MelodyLoop Full Technical Documentation & Viva Guide PDF")
    print(f"Target Output: {PDF_OUTPUT_PATH}")
    print("=" * 70)

    t0 = time.time()
    styles = get_custom_stylesheet()

    doc = SimpleDocTemplate(
        str(PDF_OUTPUT_PATH),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46,
    )

    story = []

    print("-> Assembling Cover Page and Table of Contents...")
    build_cover_and_toc(story, styles)

    print("-> Assembling Chapters 1 to 5 (Problem, Music, MAESTRO, Hierarchy, Formats)...")
    build_chapter_1(story, styles)
    build_chapter_2(story, styles)
    build_chapter_3(story, styles)
    build_chapter_4(story, styles)
    build_chapter_5(story, styles)

    print("-> Assembling Chapters 6 to 10 (Preprocessing, LSTM Math, Architecture, Training, Checkpoints)...")
    build_chapter_6(story, styles)
    build_chapter_7(story, styles)
    build_chapter_8(story, styles)
    build_chapter_9(story, styles)
    build_chapter_10(story, styles)

    print("-> Assembling Chapters 11 to 15 (Generation, Audio Synthesis, Streamlit App, Commands, Testing)...")
    build_chapter_11(story, styles)
    build_chapter_12(story, styles)
    build_chapter_13(story, styles)
    build_chapter_14(story, styles)
    build_chapter_15(story, styles)

    print("-> Assembling Chapters 16 to 20 (Failure Analysis, Reproducibility, Flowchart, 55 Viva Q&As, Cheat Sheets)...")
    build_chapter_16(story, styles)
    build_chapter_17(story, styles)
    build_chapter_18(story, styles)
    build_chapter_19(story, styles)
    build_chapter_20(story, styles)

    print(f"Total flowables assembled: {len(story)}")
    print("Compiling PDF with NumberedCanvas (two-pass dynamic page numbering)...")

    doc.build(story, canvasmaker=NumberedCanvas)

    elapsed = time.time() - t0
    file_size_mb = PDF_OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print("=" * 70)
    print(f"SUCCESS: PDF generated successfully in {elapsed:.2f} seconds!")
    print(f"Output File: {PDF_OUTPUT_PATH.resolve()}")
    print(f"File Size: {file_size_mb:.2f} MB ({PDF_OUTPUT_PATH.stat().st_size:,} bytes)")
    print("=" * 70)


if __name__ == "__main__":
    generate_pdf()
