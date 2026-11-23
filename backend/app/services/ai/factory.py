"""
AI Provider Factory and Registry.
Enables pluggable switching between AI providers (Gemini, Anthropic, OpenAI, Local).
"""

from typing import Dict, Optional, Type
from .base import BaseAIProvider
from .exceptions import AIProviderError
from .gemini_provider import GeminiProvider

# Provider registry for dynamic extensibility
_PROVIDERS: Dict[str, Type[BaseAIProvider]] = {
    "gemini": GeminiProvider,
    "google": GeminiProvider,
}


def register_ai_provider(name: str, provider_cls: Type[BaseAIProvider]) -> None:
    """Register an additional AI provider class."""
    _PROVIDERS[name.lower()] = provider_cls


def get_ai_provider(
    provider: str = "gemini",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseAIProvider:
    """
    Instantiate and return the configured AI provider.
    Defaults to Google Gemini (gemini-2.5-flash).
    """
    key = provider.lower()
    if key not in _PROVIDERS:
        supported = ", ".join(_PROVIDERS.keys())
        raise AIProviderError(
            f"Unsupported AI provider '{provider}'. Supported providers: {supported}"
        )

    provider_cls = _PROVIDERS[key]
    return provider_cls(api_key=api_key, model=model)
