"""Thin wrapper around the Gemini API (Google Gen AI SDK).

Every call forces a schema-constrained JSON response matching a pydantic
model, so pipeline steps never parse free-form text. Retries on transient
API errors (5xx, 429) and on schema-validation failures.

Public interface is intentionally identical to the original Claude-backed
client (`call_structured(system_prompt, user_message, response_model, max_tokens)`
returning `(validated_instance, {"input_tokens", "output_tokens"})`), so no
other module in the pipeline needs to change.
"""
from __future__ import annotations

from typing import TypeVar

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from pydantic import BaseModel, ValidationError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

import config
from agent.exceptions import LLMCallError, LLMValidationError
from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


def _is_retryable(exc: BaseException) -> bool:
    """Retry on server errors (5xx) and rate limiting (429) only."""
    if isinstance(exc, genai_errors.ServerError):
        return True
    if isinstance(exc, genai_errors.ClientError):
        return getattr(exc, "code", None) == 429
    return False


class LLMClient:
    def __init__(self) -> None:
        config.validate_config()
        self._client = genai.Client(api_key=config.GEMINI_API_KEY)

    @retry(
        stop=stop_after_attempt(config.LLM_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=config.LLM_RETRY_MIN_WAIT, max=config.LLM_RETRY_MAX_WAIT),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    )
    def _generate(self, **kwargs):
        return self._client.models.generate_content(**kwargs)

    def call_structured(
        self,
        system_prompt: str,
        user_message: str,
        response_model: type[T],
        max_tokens: int | None = None,
    ) -> tuple[T, dict[str, int]]:
        """Call Gemini and force a response matching `response_model`.

        Returns (validated_model_instance, {"input_tokens": int, "output_tokens": int}).
        Raises LLMCallError on API failure, LLMValidationError on schema mismatch.
        """
        try:
            response = self._generate(
                model=config.GEMINI_MODEL,
                contents=user_message,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=response_model,
                    max_output_tokens=max_tokens or config.GEMINI_MAX_TOKENS,
                    temperature=config.GEMINI_TEMPERATURE,
                ),
            )
        except Exception as exc:  # noqa: BLE001 - collapse all API failures into one type
            logger.error(f"Gemini API call failed: {exc}")
            raise LLMCallError(str(exc)) from exc

        raw_json = getattr(response, "text", None)
        if not raw_json:
            raise LLMValidationError(
                "Gemini returned no text content (response may have been blocked or truncated)."
            )

        try:
            validated = response_model.model_validate_json(raw_json)
        except ValidationError as exc:
            logger.error(f"Schema validation failed for {response_model.__name__}: {exc}")
            raise LLMValidationError(str(exc)) from exc

        usage = response.usage_metadata
        token_usage = {
            "input_tokens": (getattr(usage, "prompt_token_count", 0) or 0) if usage else 0,
            "output_tokens": (getattr(usage, "candidates_token_count", 0) or 0) if usage else 0,
        }
        return validated, token_usage
