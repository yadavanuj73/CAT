"""
Legacy AI Client Adapter.
Seamlessly routes AI completion requests through the unified AI provider architecture (Google Gemini).
Retains backwards compatibility for any legacy callers while defaulting to Gemini.
"""

from typing import Dict, List, Optional
from app.services.ai import get_ai_provider, AIProviderError
from app.security.redaction import redact_secrets


async def generate_chat_completion(
    api_key: Optional[str] = None,
    system_prompt: str = "",
    user_prompt: str = "",
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    """Execute LLM chat completion using the unified Gemini AI provider."""
    try:
        # Determine provider by key format or default to gemini
        provider_name = "gemini"
        if api_key and api_key.startswith("sk-"):
            provider_name = "openai"

        provider = get_ai_provider(provider_name, api_key=api_key, model=model)
        return await provider.generate_text(
            prompt=user_prompt,
            system_instruction=system_prompt,
            temperature=temperature,
        )
    except Exception as e:
        redacted_msg = redact_secrets(str(e))
        raise RuntimeError(f"AI completion failed: {redacted_msg}")
