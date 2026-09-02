"""Custom exceptions used across the pipeline.

Keeping these distinct lets the orchestrator catch failures at the right
granularity and surface a clear message to the UI instead of a raw traceback.
"""


class AgentError(Exception):
    """Base class for all agent pipeline errors."""


class CVValidationError(AgentError):
    """Raised when the uploaded file is not a usable CV (empty, corrupted, too short)."""


class ExtractionError(AgentError):
    """Raised when PDF text extraction fails outright."""


class LLMCallError(AgentError):
    """Raised when a Claude API call fails after all retries."""


class LLMValidationError(AgentError):
    """Raised when a Claude response cannot be validated against its expected schema."""


class RenderingError(AgentError):
    """Raised when PDF rendering (report or improved CV) fails."""
