"""Step 7 (Python only): render the analysis report and improved CV as PDFs."""
from __future__ import annotations

import config
from agent.exceptions import AgentError
from agent.state import AgentState
from agent.steps.base_step import PipelineStep
from utils.cv_renderer import render_improved_cv
from utils.report_renderer import render_report


class RenderPDFsStep(PipelineStep):
    name = "Render PDFs"

    def run(self, state: AgentState) -> AgentState:
        if not all([state.profile, state.ats_result, state.analysis, state.interview_and_report, state.improved_cv]):
            raise AgentError("RenderPDFsStep requires all prior pipeline outputs to be populated.")

        report_path = config.OUTPUT_DIR / f"report_{state.run_id}.pdf"
        cv_path = config.OUTPUT_DIR / f"improved_cv_{state.run_id}.pdf"

        state.report_pdf_path = render_report(state, str(report_path))
        state.improved_cv_pdf_path = render_improved_cv(state, str(cv_path))
        return state
