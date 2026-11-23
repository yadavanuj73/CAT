"""
Base AI Provider Interface.
Defines the abstract contract for AI models (Google Gemini, Anthropic, OpenAI, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseAIProvider(ABC):
    """Abstract interface for all AI provider implementations."""

    provider_name: str = "generic"
    default_model: str = "gemini-2.5-flash"

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate plain text response from the model.
        Must redact secrets on any exception.
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        """
        Generate structured output adhering to a Pydantic schema using constrained JSON generation.
        """
        pass

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Check connectivity with the AI provider using a lightweight ping.
        Returns a dict with status and model details.
        """
        pass
