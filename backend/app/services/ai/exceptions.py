"""
AI Provider Exceptions.
Defines clean, typed exceptions for rate limits, quota exhaustion, timeouts, and auth failures.
"""


class AIProviderError(Exception):
    """Base exception for all AI provider operations."""

    def __init__(self, message: str, provider: str = "gemini", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code

    def __str__(self) -> str:
        return f"[{self.provider.upper()}] {self.message}"


class AIAuthenticationError(AIProviderError):
    """Raised when API credentials are invalid or missing."""

    def __init__(self, message: str = "Invalid or missing API key.", provider: str = "gemini"):
        super().__init__(message=message, provider=provider, status_code=401)


class AIRateLimitError(AIProviderError):
    """Raised when request rate limits (RPM / TPM) are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please wait a moment before sending more requests.",
        provider: str = "gemini",
    ):
        super().__init__(message=message, provider=provider, status_code=429)


class AIQuotaExhaustedError(AIProviderError):
    """
    Raised when API quota has been exhausted.
    Strict policy: Never silently switch to a paid tier or charge the user.
    """

    def __init__(
        self,
        message: str = "Google Gemini API quota has been exhausted. System policy strictly forbids automatic switching to paid models. Please verify your Google AI Studio quota or configure another key.",
        provider: str = "gemini",
    ):
        super().__init__(message=message, provider=provider, status_code=429)


class AITimeoutError(AIProviderError):
    """Raised when an AI provider call times out."""

    def __init__(
        self,
        message: str = "AI request timed out. Please try again with a shorter prompt or retry later.",
        provider: str = "gemini",
    ):
        super().__init__(message=message, provider=provider, status_code=504)


class AIServiceUnavailableError(AIProviderError):
    """Raised when the AI provider returns 5xx or is temporarily unreachable."""

    def __init__(
        self,
        message: str = "AI provider service is temporarily unavailable. Please retry later.",
        provider: str = "gemini",
    ):
        super().__init__(message=message, provider=provider, status_code=503)
