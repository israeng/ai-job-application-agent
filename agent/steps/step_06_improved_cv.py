"""Step 6 (Claude 4/4): improved, ATS-friendly CV generation."""
from __future__ import annotations

from agent.exceptions import AgentError
from agent.llm_client import LLMClient
from agent.prompts.improved_cv import build_system_prompt, build_user_message
from agent.schemas import ImprovedCVSchema
from agent.state import AgentState
from agent.steps.base_step import PipelineStep


class ImprovedCVStep(PipelineStep):
    name = "Improved CV generation (Claude 4/4)"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or LLMClient()

    def run(self, state: AgentState) -> AgentState:
        if state.profile is None or state.analysis is None:
            raise AgentError(
                "ImprovedCVStep requires state.profile and state.analysis to be populated first."
            )
        improved_cv, usage = self._llm.call_structured(
            system_prompt=build_system_prompt(),
            user_message=build_user_message(state.profile, state.analysis),
            response_model=ImprovedCVSchema,
        )
        state.improved_cv = improved_cv
        state.record_tokens(self.name, usage["input_tokens"], usage["output_tokens"])
        return state
