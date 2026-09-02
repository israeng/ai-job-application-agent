"""Step 3 (Python only): deterministic ATS compatibility scoring.

Runs after profile extraction (step 2) — section-completeness and
skills-coverage scoring read from the structured profile, not raw text.
"""
from __future__ import annotations

from pathlib import Path

from agent.exceptions import AgentError
from agent.state import AgentState
from agent.steps.base_step import PipelineStep
from analysis.ats_scoring import compute_ats_result
from utils.pdf_parser import extract_layout_metrics


class ATSScoringStep(PipelineStep):
    name = "ATS scoring engine"

    def __init__(self, pdf_path: str | Path) -> None:
        self._pdf_path = Path(pdf_path)

    def run(self, state: AgentState) -> AgentState:
        if state.profile is None:
            raise AgentError("ATSScoringStep requires state.profile to be populated first.")
        layout = extract_layout_metrics(self._pdf_path)
        state.ats_result = compute_ats_result(
            profile=state.profile,
            raw_text=state.raw_text,
            layout=layout,
            language=state.language,
        )
        return state
