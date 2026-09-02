"""Step 5 (Claude 3/4): interview questions + final report narrative."""
from __future__ import annotations

from agent.exceptions import AgentError
from agent.llm_client import LLMClient
from agent.prompts.interview_and_report import build_system_prompt, build_user_message
from agent.schemas import InterviewAndReportSchema
from agent.state import AgentState
from agent.steps.base_step import PipelineStep


class InterviewAndReportStep(PipelineStep):
    name = "Interview & report content (Claude 3/4)"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or LLMClient()

    def run(self, state: AgentState) -> AgentState:
        if state.profile is None or state.ats_result is None or state.analysis is None:
            raise AgentError(
                "InterviewAndReportStep requires profile, ats_result, and analysis "
                "to be populated first."
            )
        result, usage = self._llm.call_structured(
            system_prompt=build_system_prompt(),
            user_message=build_user_message(state.profile, state.ats_result, state.analysis),
            response_model=InterviewAndReportSchema,
        )
        state.interview_and_report = result
        state.record_tokens(self.name, usage["input_tokens"], usage["output_tokens"])
        return state
