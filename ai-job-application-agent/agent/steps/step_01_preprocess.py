"""Step 1 (Python only): ingest a CV PDF, extract text, detect language.

No Claude call. Prepares clean input for the reasoning steps that follow.
"""
from __future__ import annotations

from pathlib import Path

from agent.state import AgentState
from agent.steps.base_step import PipelineStep
from analysis.language_detector import detect_language
from utils.pdf_parser import extract_text


class PreprocessStep(PipelineStep):
    name = "Ingest & preprocess"

    def __init__(self, pdf_path: str | Path) -> None:
        self._pdf_path = Path(pdf_path)

    def run(self, state: AgentState) -> AgentState:
        state.source_filename = self._pdf_path.name
        state.raw_text = extract_text(self._pdf_path)
        state.language = detect_language(state.raw_text)
        return state
