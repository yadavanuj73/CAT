"""
Google Gemini AI Provider Implementation.
Uses the official Google Gen AI SDK (`google-genai`).
Features:
- Full async support via `client.aio`.
- Structured JSON output constrained with Pydantic schemas.
- Granular error handling for rate limits, quota exhaustion, timeouts, and auth failures.
- Strict anti-downgrade/anti-paid-switching guarantees.
- Secret redaction on all error messages.
"""

import json
import logging
import os
import re
from typing import Any, Dict, Optional, Type, TypeVar
from google import genai
from google.genai import errors, types
from pydantic import BaseModel
from app.config import settings
from app.security.redaction import redact_secrets
from .base import BaseAIProvider
from .exceptions import (
    AIAuthenticationError,
    AIProviderError,
    AIQuotaExhaustedError,
    AIRateLimitError,
    AIServiceUnavailableError,
    AITimeoutError,
)

logger = logging.getLogger("uvicorn.error")
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseAIProvider):
    """Google Gemini Provider using official google-genai SDK."""

    provider_name: str = "gemini"
    default_model: str = "gemini-2.5-flash"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = (
            api_key
            or getattr(settings, "GEMINI_API_KEY", "")
            or os.environ.get("GEMINI_API_KEY", "")
        ).strip()

        configured_model = getattr(settings, "GEMINI_MODEL", "") or os.environ.get(
            "GEMINI_MODEL", ""
        )
        self.default_model = model or configured_model or "gemini-2.5-flash"
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        """Initialize or return the cached genai.Client."""
        if not self.api_key:
            raise AIAuthenticationError(
                "Google Gemini API key not configured. Please supply via GEMINI_API_KEY or BYOK session.",
                provider=self.provider_name,
            )
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _map_error(self, err: Exception) -> AIProviderError:
        """Map raw GenAI/HTTP errors to strongly-typed domain errors with secret redaction."""
        raw_msg = str(err)
        safe_msg = redact_secrets(raw_msg)

        if isinstance(err, errors.APIError):
            code = getattr(err, "code", None) or 500
            msg_lower = safe_msg.lower()

            # Quota exhaustion vs Rate Limit
            if code == 429 or "resource_exhausted" in msg_lower or "quota" in msg_lower:
                if "quota" in msg_lower or "exceeded your current quota" in msg_lower:
                    return AIQuotaExhaustedError(
                        message="Google Gemini API quota has been exhausted. Automatic fallback to paid models is strictly disabled per cost controls.",
                        provider=self.provider_name,
                    )
                return AIRateLimitError(
                    message="Google Gemini API rate limit reached. Please wait a moment before sending more requests.",
                    provider=self.provider_name,
                )

            # Authentication / Key errors
            if code in (401, 403) or "api_key_invalid" in msg_lower or "permission" in msg_lower:
                return AIAuthenticationError(
                    message=f"Google Gemini authentication failed: {safe_msg}",
                    provider=self.provider_name,
                )

            # Service availability
            if code >= 500:
                return AIServiceUnavailableError(
                    message=f"Google Gemini API service unavailable (status {code}): {safe_msg}",
                    provider=self.provider_name,
                )

            return AIProviderError(
                message=f"Google Gemini API error ({code}): {safe_msg}",
                provider=self.provider_name,
                status_code=code,
            )

        if "timeout" in safe_msg.lower() or isinstance(err, TimeoutError):
            return AITimeoutError(
                message=f"Google Gemini request timed out: {safe_msg}",
                provider=self.provider_name,
            )

        return AIProviderError(
            message=f"Unexpected error communicating with Google Gemini: {safe_msg}",
            provider=self.provider_name,
        )

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: Optional[int] = None,
    ) -> str:
        """Execute text generation against Gemini model."""
        target_model = model or self.default_model
        client = self._get_client()

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction,
            max_output_tokens=max_output_tokens,
        )

        try:
            response = await client.aio.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            raise self._map_error(e)

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        """
        Generate structured output guaranteed to match the Pydantic response_schema.
        Uses native JSON schema enforcement in the Gemini API.
        """
        target_model = model or self.default_model
        client = self._get_client()

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema,
        )

        try:
            response = await client.aio.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config,
            )
            raw_text = response.text or "{}"
            # Clean markdown codeblocks if accidentally wrapped
            clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
            return response_schema.model_validate_json(clean_json)
        except Exception as e:
            if isinstance(e, AIProviderError):
                raise
            raise self._map_error(e)

    async def test_connection(self) -> Dict[str, Any]:
        """Verify API connectivity with a lightweight ping to the default model."""
        client = self._get_client()
        try:
            response = await client.aio.models.generate_content(
                model=self.default_model,
                contents="Ping",
                config=types.GenerateContentConfig(max_output_tokens=5),
            )
            return {
                "status": "connected",
                "provider": self.provider_name,
                "model": self.default_model,
                "response": (response.text or "").strip(),
            }
        except Exception as e:
            raise self._map_error(e)
