"""Central configuration for the AI Job Application Agent.

All tunables live here so no other module hardcodes model names,
paths, or thresholds.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Gemini --------------------------------------------------------------
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
# Higher than a typical text-only budget on purpose: Gemini 3.x "thinking"
# tokens are drawn from this same budget before the JSON output is written,
# so a low ceiling risks truncating structured responses.
GEMINI_MAX_TOKENS: int = 8192
GEMINI_TEMPERATURE: float = 0.4
LLM_MAX_RETRIES: int = 3
LLM_RETRY_MIN_WAIT: int = 2   # seconds
LLM_RETRY_MAX_WAIT: int = 10  # seconds

# --- Language detection --------------------------------------------------
ARABIC_UNICODE_RANGE = (0x0600, 0x06FF)
ARABIC_CHAR_RATIO_THRESHOLD: float = 0.15  # fraction of chars that triggers "ar"

# --- ATS scoring weights (must sum to 1.0) --------------------------------
ATS_WEIGHTS: dict[str, float] = {
    "section_completeness": 0.20,
    "skills_coverage": 0.20,
    "structure_formatting": 0.20,
    "keyword_relevance": 0.20,
    "readability": 0.20,
}
ATS_REQUIRED_SECTIONS: list[str] = [
    "contact", "summary", "experience", "education", "skills",
]

# --- Paths ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# --- Validation ------------------------------------------------------------
MIN_CV_CHARACTERS: int = 200  # below this, treat as invalid/empty CV
MAX_CV_CHARACTERS: int = 50_000

# --- Logging ---------------------------------------------------------------
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


def validate_config() -> None:
    """Fail fast at startup if required config is missing."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
