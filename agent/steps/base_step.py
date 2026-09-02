"""Common interface for all pipeline steps.

The orchestrator only knows about `PipelineStep.run`. It has no idea
whether a given step calls Claude or is pure Python — that's what keeps
adding/removing/reordering steps a one-line change in orchestrator.py.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod

from agent.state import AgentState
from utils.logger import get_run_logger


class PipelineStep(ABC):
    #: Human-readable name used in logs and the UI trace.
    name: str = "unnamed_step"

    @abstractmethod
    def run(self, state: AgentState) -> AgentState:
        """Mutate and return `state`. Must raise an AgentError subclass on failure."""

    def execute(self, state: AgentState) -> AgentState:
        """Wraps `run` with timing + logging. Called by the orchestrator."""
        log = get_run_logger(self.__class__.__module__, state.run_id)
        started = time.monotonic()
        log.info(f"START {self.name}")
        state = self.run(state)
        elapsed = time.monotonic() - started
        state.step_log.append(f"{self.name} ({elapsed:.1f}s)")
        log.info(f"DONE  {self.name} in {elapsed:.1f}s")
        return state
