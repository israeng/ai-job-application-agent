"""Shared visual design system for every generated PDF.

Both the analysis report and the improved CV are built from these same
colors, fonts, spacing, and page decoration, so they present one
consistent, professional identity. ReportLab only — pure Python, no
system-level dependencies, works out of the box on Windows.
"""
from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate

# --- Palette -----------------------------------------------------------
PRIMARY = colors.HexColor("#1F3A5F")   # document title, section headings
ACCENT = colors.HexColor("#2E86AB")    # sub-headings, rules, highlights
TEXT = colors.HexColor("#2B2B2B")      # body text
MUTED = colors.HexColor("#6B7280")     # meta text, footer
LIGHT_BG = colors.HexColor("#F2F4F7")  # table header backgrounds
BORDER = colors.HexColor("#D8DEE6")

SCORE_GOOD = colors.HexColor("#1E8E5A")
SCORE_WARN = colors.HexColor("#B7791F")
SCORE_POOR = colors.HexColor("#C0392B")


def score_color(score: float) -> colors.Color:
    if score >= 80:
        return SCORE_GOOD
    if score >= 60:
        return SCORE_WARN
    return SCORE_POOR


# --- Layout ----------------------------------------------------------------
PAGE_SIZE = LETTER
MARGIN = 0.7 * inch

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"


def build_styles() -> dict[str, ParagraphStyle]:
    return {
        "doc_title": ParagraphStyle(
            "doc_title", fontName=FONT_BOLD, fontSize=22, textColor=PRIMARY,
            spaceAfter=4, leading=26,
        ),
        "doc_subtitle": ParagraphStyle(
            "doc_subtitle", fontName=FONT_REGULAR, fontSize=11, textColor=MUTED,
            spaceAfter=18, leading=14,
        ),
        "h1": ParagraphStyle(
            "h1", fontName=FONT_BOLD, fontSize=14, textColor=PRIMARY,
            spaceBefore=16, spaceAfter=8, leading=17,
        ),
        "h2": ParagraphStyle(
            "h2", fontName=FONT_BOLD, fontSize=11.5, textColor=ACCENT,
            spaceBefore=10, spaceAfter=4, leading=14,
        ),
        "body": ParagraphStyle(
            "body", fontName=FONT_REGULAR, fontSize=10, textColor=TEXT,
            leading=14, spaceAfter=6,
        ),
        "body_muted": ParagraphStyle(
            "body_muted", fontName=FONT_ITALIC, fontSize=9.5, textColor=MUTED,
            leading=13, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName=FONT_REGULAR, fontSize=10, textColor=TEXT,
            leading=14, spaceAfter=3, leftIndent=14, bulletIndent=2,
        ),
        "meta": ParagraphStyle(
            "meta", fontName=FONT_ITALIC, fontSize=9, textColor=MUTED,
            leading=12, spaceAfter=2,
        ),
    }


def _page_decoration(document_label: str):
    """onPage callback: consistent top accent bar + footer, shared by all PDFs."""

    def _draw(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(PRIMARY)
        canvas.rect(0, PAGE_SIZE[1] - 0.12 * inch, PAGE_SIZE[0], 0.12 * inch, stroke=0, fill=1)

        canvas.setFont(FONT_REGULAR, 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN, 0.35 * inch, document_label)
        canvas.drawRightString(PAGE_SIZE[0] - MARGIN, 0.35 * inch, f"Page {doc.page}")
        canvas.setStrokeColor(BORDER)
        canvas.line(MARGIN, 0.5 * inch, PAGE_SIZE[0] - MARGIN, 0.5 * inch)
        canvas.restoreState()

    return _draw


def build_doc(filepath: str, document_label: str):
    """Returns (SimpleDocTemplate, page_decoration_callback) sharing one identity."""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN + 0.05 * inch, bottomMargin=MARGIN,
        title=document_label,
    )
    return doc, _page_decoration(document_label)
