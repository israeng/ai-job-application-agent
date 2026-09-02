"""PDF text extraction and layout inspection.

Two responsibilities kept separate:
- extract_text(): clean text for the LLM / language detection.
- extract_layout_metrics(): structural signals (tables, bullets, page count)
  used only by the deterministic ATS structure/formatting score.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pdfplumber

import config
from agent.exceptions import CVValidationError, ExtractionError
from utils.logger import get_logger

logger = get_logger(__name__)

_BULLET_CHARS = ("•", "-", "*", "▪", "●", "◦", "‣")


@dataclass
class LayoutMetrics:
    num_pages: int
    has_tables: bool
    bullet_line_ratio: float


def _open_pdf(pdf_path: str | Path):
    path = Path(pdf_path)
    if not path.exists():
        raise ExtractionError(f"File not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise CVValidationError(f"Only PDF files are supported, got: {path.suffix}")
    try:
        return pdfplumber.open(path)
    except Exception as exc:  # noqa: BLE001
        raise ExtractionError(f"Failed to read PDF: {exc}") from exc


def extract_text(pdf_path: str | Path) -> str:
    """Extract, clean, and validate CV text from a PDF."""
    with _open_pdf(pdf_path) as pdf:
        pages_text = [page.extract_text() or "" for page in pdf.pages]

    cleaned = clean_text("\n".join(pages_text))
    validate_text(cleaned)
    return cleaned


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving line structure."""
    lines = (line.strip() for line in text.splitlines())
    lines = (" ".join(line.split()) for line in lines if line.strip())
    return "\n".join(lines)


def validate_text(text: str) -> None:
    length = len(text)
    if length < config.MIN_CV_CHARACTERS:
        raise CVValidationError(
            f"Extracted text is too short ({length} chars). The PDF may be empty, "
            f"a scanned image without a text layer, or corrupted."
        )
    if length > config.MAX_CV_CHARACTERS:
        raise CVValidationError(
            f"Extracted text is unusually long ({length} chars) for a CV."
        )


def extract_layout_metrics(pdf_path: str | Path) -> LayoutMetrics:
    """Structural signals used by the ATS structure/formatting criterion."""
    with _open_pdf(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        has_tables = any(len(page.find_tables()) > 0 for page in pdf.pages)

        raw_lines: list[str] = []
        for page in pdf.pages:
            text = page.extract_text() or ""
            raw_lines.extend(line.strip() for line in text.splitlines() if line.strip())

    if raw_lines:
        bullet_lines = sum(1 for line in raw_lines if line.startswith(_BULLET_CHARS))
        bullet_ratio = bullet_lines / len(raw_lines)
    else:
        bullet_ratio = 0.0

    return LayoutMetrics(
        num_pages=num_pages,
        has_tables=has_tables,
        bullet_line_ratio=round(bullet_ratio, 3),
    )
