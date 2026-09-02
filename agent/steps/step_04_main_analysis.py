"""Step 4 (Claude 2/4): career path, skill gaps, CV improvement suggestions."""
from __future__ import annotations

from agent.exceptions import AgentError
from agent.llm_client import LLMClient
from agent.prompts.main_analysis import build_system_prompt, build_user_message
from agent.schemas import MainAnalysisSchema
from agent.state import AgentState
from agent.steps.base_step import PipelineStep


class MainAnalysisStep(PipelineStep):
    name = "Main analysis (Claude 2/4)"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or LLMClient()

    def run(self, state: AgentState) -> AgentState:
        if state.profile is None or state.ats_result is None:
            raise AgentError(
                "MainAnalysisStep requires state.profile and state.ats_result to be populated first."
            )
        analysis, usage = self._llm.call_structured(
            system_prompt=build_system_prompt(),
            user_message=build_user_message(state.profile, state.ats_result),
            response_model=MainAnalysisSchema,
        )
        state.analysis = analysis
        state.record_tokens(self.name, usage["input_tokens"], usage["output_tokens"])
        return state
