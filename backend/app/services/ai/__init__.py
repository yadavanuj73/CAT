"""
AI Services Module.
Exports the unified provider factory, concrete Gemini provider, schemas, and typed exceptions.
"""

from .base import BaseAIProvider
from .exceptions import (
    AIAuthenticationError,
    AIProviderError,
    AIQuotaExhaustedError,
    AIRateLimitError,
    AIServiceUnavailableError,
    AITimeoutError,
)
from .factory import get_ai_provider, register_ai_provider
from .gemini_provider import GeminiProvider
from .schemas import (
    AIVerificationFeedbackSchema,
    ExtractedOptionSchema,
    ExtractedPaperBatchSchema,
    ExtractedQuestionSchema,
    QuestionClassificationSchema,
)

__all__ = [
    "BaseAIProvider",
    "GeminiProvider",
    "get_ai_provider",
    "register_ai_provider",
    "AIProviderError",
    "AIAuthenticationError",
    "AIRateLimitError",
    "AIQuotaExhaustedError",
    "AITimeoutError",
    "AIServiceUnavailableError",
    "ExtractedOptionSchema",
    "ExtractedQuestionSchema",
    "ExtractedPaperBatchSchema",
    "QuestionClassificationSchema",
    "AIVerificationFeedbackSchema",
]
