"""Step 2 (Claude 1/4): structured profile extraction."""
from __future__ import annotations

from agent.llm_client import LLMClient
from agent.prompts.extract_profile import build_system_prompt, build_user_message
from agent.schemas import ProfileSchema
from agent.state import AgentState
from agent.steps.base_step import PipelineStep


class ExtractProfileStep(PipelineStep):
    name = "Profile extraction (Claude 1/4)"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or LLMClient()

    def run(self, state: AgentState) -> AgentState:
        profile, usage = self._llm.call_structured(
            system_prompt=build_system_prompt(state.language),
            user_message=build_user_message(state.raw_text),
            response_model=ProfileSchema,
        )
        state.profile = profile
        state.record_tokens(self.name, usage["input_tokens"], usage["output_tokens"])
        return state
