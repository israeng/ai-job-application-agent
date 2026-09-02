"""Language detection: Arabic vs English.

Primary heuristic: ratio of Arabic-range Unicode characters among all
alphabetic characters. This is more reliable than statistical detectors
on CVs, where names, emails, and technical terms are often Latin-script
even within an otherwise-Arabic document. langdetect is used only as a
tie-breaker when the Arabic-character ratio is low but non-zero.
"""
from __future__ import annotations

import config
from utils.logger import get_logger

logger = get_logger(__name__)

_ARABIC_LOW, _ARABIC_HIGH = config.ARABIC_UNICODE_RANGE


def arabic_char_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    arabic = sum(1 for c in letters if _ARABIC_LOW <= ord(c) <= _ARABIC_HIGH)
    return arabic / len(letters)


def detect_language(text: str) -> str:
    """Return 'ar' or 'en'."""
    ratio = arabic_char_ratio(text)
    if ratio >= config.ARABIC_CHAR_RATIO_THRESHOLD:
        logger.info(f"Language detected: ar (arabic_char_ratio={ratio:.2f})")
        return "ar"

    if ratio > 0:
        try:
            from langdetect import DetectorFactory, detect

            DetectorFactory.seed = 0
            if detect(text) == "ar":
                logger.info("Language detected: ar (langdetect fallback)")
                return "ar"
        except Exception as exc:  # noqa: BLE001 - langdetect can raise on odd input
            logger.warning(f"langdetect fallback failed, defaulting to 'en': {exc}")

    logger.info(f"Language detected: en (arabic_char_ratio={ratio:.2f})")
    return "en"
