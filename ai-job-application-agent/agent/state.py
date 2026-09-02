"""AgentState: the single object threaded through every pipeline step.

Design rule: once `profile` is populated, later steps read from the
structured fields below, not from `raw_text`. This keeps token usage
bounded regardless of how many stages the pipeline grows to.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from agent.schemas import (
    ATSResult,
    ImprovedCVSchema,
    InterviewAndReportSchema,
    MainAnalysisSchema,
    ProfileSchema,
)


@dataclass
class AgentState:
    run_id: str

    # Populated by preprocessing (Python)
    raw_text: str = ""
    language: str = "en"  # "en" | "ar"
    source_filename: str = ""

    # Populated by pipeline steps
    profile: ProfileSchema | None = None
    ats_result: ATSResult | None = None
    analysis: MainAnalysisSchema | None = None
    interview_and_report: InterviewAndReportSchema | None = None
    improved_cv: ImprovedCVSchema | None = None

    # Output artifacts
    report_pdf_path: str | None = None
    improved_cv_pdf_path: str | None = None

    # Observability
    token_usage: dict[str, int] = field(default_factory=dict)
    step_log: list[str] = field(default_factory=list)
    error: str | None = None

    def record_tokens(self, step_name: str, input_tokens: int, output_tokens: int) -> None:
        self.token_usage[step_name] = self.token_usage.get(step_name, 0) + input_tokens + output_tokens

    @property
    def total_tokens(self) -> int:
        return sum(self.token_usage.values())

    @property
    def failed(self) -> bool:
        return self.error is not None
