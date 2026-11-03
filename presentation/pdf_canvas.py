"""
MelodyLoop Full Workflow Guide PDF Generator
Produces the official academic technical documentation and viva preparation guide:
'docs/MelodyLoop_Full_Workflow_Guide.pdf'

Utilizes ReportLab with a custom NumberedCanvas, professional styling,
callout panels, tables, code blocks, and embedded figures.
"""

import os
import sys
import time
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    PageBreak,
    HRFlowable,
)
from reportlab.pdfgen import canvas

# Paths
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
PDF_OUTPUT_PATH = DOCS_DIR / "MelodyLoop_Full_Workflow_Guide.pdf"
FIG_DIR = BASE_DIR / "artifacts" / "doc_figures"


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total page count and render
    clean running headers and footers on all pages except the cover page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Do not draw on cover page (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header
        header_text = "MelodyLoop: From Piano Notes to AI-Generated Music — Technical & Viva Guide"
        self.drawString(42, 755, header_text)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(42, 748, 570, 748)

        # Running Footer
        self.line(42, 45, 570, 45)
        footer_left = "PyTorch LSTM • MAESTRO v3.0 • Educational Machine Learning"
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(42, 32, footer_left)
        self.drawRightString(570, 32, page_str)

        self.restoreState()


print("Canvas helper defined.")
