"""Prompt for Claude call 1/4: structured profile extraction."""
from __future__ import annotations

_BASE_INSTRUCTIONS = """You are an expert CV/resume analyst. Extract a structured candidate \
profile from the CV text the user provides.

Rules:
- Extract only what is stated or clearly implied in the CV. Never invent companies, \
dates, degrees, or skills that are not present.
- If a field is not present, omit it or use an empty list — do not guess.
- total_years_experience: estimate numerically from the dates/durations of listed \
experience entries. Use null if it cannot be reasonably estimated.
- seniority_level: infer from years of experience and job titles \
(e.g. Entry-level, Mid-level, Senior, Lead/Principal).
- Preserve job titles, company names, and degree names as written in the CV.
- Call the submit_result tool with the structured profile."""

_LANGUAGE_NOTE = {
    "en": "The CV is written in English.",
    "ar": (
        "The CV is written in Arabic. Read and interpret it in Arabic, but return "
        "all extracted field values translated into English, so downstream analysis "
        "and the final English-language report and CV stay consistent. Translate "
        "faithfully — do not add or drop information in the process."
    ),
}


def build_system_prompt(language: str) -> str:
    note = _LANGUAGE_NOTE.get(language, _LANGUAGE_NOTE["en"])
    return f"{_BASE_INSTRUCTIONS}\n\n{note}"


def build_user_message(raw_text: str) -> str:
    return f"CV TEXT:\n---\n{raw_text}\n---"
