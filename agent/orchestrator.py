"""AgentOrchestrator: runs the full autonomous pipeline end to end.

This is the only place that defines the pipeline's shape and order —
individual steps have no knowledge of what comes before or after them.
Adding, removing, or reordering a stage is a one-line change here.

This is the single entry point the UI (or any other caller) uses; nothing
outside this module needs to know that some steps call Claude and others
are pure Python.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from agent.exceptions import AgentError
from agent.llm_client import LLMClient
from agent.state import AgentState
from agent.steps.base_step import PipelineStep
from agent.steps.step_01_preprocess import PreprocessStep
from agent.steps.step_02_extract_profile import ExtractProfileStep
from agent.steps.step_03_ats_scoring import ATSScoringStep
from agent.steps.step_04_main_analysis import MainAnalysisStep
from agent.steps.step_05_interview_and_report import InterviewAndReportStep
from agent.steps.step_06_improved_cv import ImprovedCVStep
from agent.steps.step_07_render_pdfs import RenderPDFsStep
from utils.logger import get_run_logger, new_run_id

# Called after every step (success or failure) with (step_name, current_state) —
# lets the UI render a live trace without polling internals.
ProgressCallback = Callable[[str, AgentState], None]


class AgentOrchestrator:
    """Runs the autonomous CV-analysis pipeline for a single uploaded PDF."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        # One shared LLMClient across every Claude-backed step in a run.
        self._llm_client = llm_client or LLMClient()

    def _build_pipeline(self, pdf_path: str | Path) -> list[PipelineStep]:
        return [
            PreprocessStep(pdf_path),
            ExtractProfileStep(self._llm_client),
            ATSScoringStep(pdf_path),
            MainAnalysisStep(self._llm_client),
            InterviewAndReportStep(self._llm_client),
            ImprovedCVStep(self._llm_client),
            RenderPDFsStep(),
        ]

    def run(
        self,
        pdf_path: str | Path,
        source_filename: str | None = None,
        on_step_complete: ProgressCallback | None = None,
    ) -> AgentState:
        """Executes every step in order. Stops and records state.error on failure —
        never raises, so the UI always gets a usable AgentState back."""
        run_id = new_run_id()
        log = get_run_logger(__name__, run_id)
        state = AgentState(run_id=run_id, source_filename=source_filename or Path(pdf_path).name)

        log.info(f"Pipeline started for '{state.source_filename}'")
        for step in self._build_pipeline(pdf_path):
            try:
                state = step.execute(state)
            except AgentError as exc:
                log.error(f"Pipeline stopped at '{step.name}': {exc}")
                state.error = f"{step.name}: {exc}"
                if on_step_complete:
                    on_step_complete(step.name, state)
                return state
            except Exception as exc:  # noqa: BLE001 - unexpected errors still surface cleanly
                log.exception(f"Unexpected error in '{step.name}'")
                state.error = f"{step.name}: unexpected error — {exc}"
                if on_step_complete:
                    on_step_complete(step.name, state)
                return state

            if on_step_complete:
                on_step_complete(step.name, state)

        log.info(f"Pipeline completed successfully. Total tokens used: {state.total_tokens}")
        return state
