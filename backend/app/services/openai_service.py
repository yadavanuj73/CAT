"""
BYOK OpenAI API Client Service.
Executes AI completions using the authenticated user's session key or encrypted key.
Never exposes the key in logs or error messages.
"""

from typing import Dict, List, Optional
import httpx
from openai import AsyncOpenAI
from app.security.redaction import redact_secrets


async def get_openai_client(api_key: str) -> AsyncOpenAI:
    """Initialize an AsyncOpenAI client with timeout and redacted error handling."""
    if not api_key:
        raise ValueError("Valid OpenAI API key must be supplied via BYOK session or stored settings.")
    return AsyncOpenAI(
        api_key=api_key,
        timeout=httpx.Timeout(60.0, connect=10.0),
        max_retries=2,
    )


async def generate_chat_completion(
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o",
    temperature: float = 0.2,
) -> str:
    """Execute LLM chat completion with strict secret redaction on exceptions."""
    try:
        client = await get_openai_client(api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "human" if model.startswith("o") else "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        redacted_msg = redact_secrets(str(e))
        raise RuntimeError(f"OpenAI completion failed: {redacted_msg}")
