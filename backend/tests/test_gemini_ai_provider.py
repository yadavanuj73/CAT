"""
Unit and Integration Tests for Google Gemini AI Provider and Reusable AI Architecture.
Verifies:
1. Provider initialization with gemini-2.5-flash default.
2. Secret redaction on Gemini API keys (AIza...).
3. Granular error mapping: Rate limits (429), Quota exhaustion, Timeouts, Auth errors.
4. Anti-paid-switching constraint: Quota exhaustion raises explicit AIQuotaExhaustedError.
5. Structured JSON extraction, classification, and verification schemas.
6. Reusable provider factory and custom provider extensibility.
7. Requirement 11 & 12: Deterministic verification and math checks remain 100% independent.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from google.genai import errors
from app.services.ai import (
    BaseAIProvider,
    GeminiProvider,
    get_ai_provider,
    register_ai_provider,
    AIAuthenticationError,
    AIRateLimitError,
    AIQuotaExhaustedError,
    AITimeoutError,
    AIProviderError,
    ExtractedQuestionSchema,
    QuestionClassificationSchema,
    AIVerificationFeedbackSchema,
)
from app.security.redaction import redact_secrets, mask_key
from app.utils.math_solver import verify_arithmetic_statement


def test_gemini_provider_default_model_and_name():
    """Verify provider defaults to gemini-2.5-flash without hardcoded secrets."""
    provider = GeminiProvider(api_key="AIzaSyTestKeyForInitialization12345678")
    assert provider.provider_name == "gemini"
    assert provider.default_model == "gemini-2.5-flash"
    assert provider.api_key == "AIzaSyTestKeyForInitialization12345678"


def test_missing_api_key_raises_auth_error():
    """Verify operations raise typed AIAuthenticationError when no key is present."""
    with patch("app.services.ai.gemini_provider.settings.GEMINI_API_KEY", ""):
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            provider = GeminiProvider(api_key="")
            with pytest.raises(AIAuthenticationError) as exc_info:
                provider._get_client()
            assert "key not configured" in str(exc_info.value).lower()


def test_gemini_key_redaction():
    """Verify Gemini keys (AIza...) are strictly redacted from logs and errors."""
    sample_key = "AIzaSyD7ExampleSecretKey12345678901234"
    text_with_secret = f"Call failed with key: {sample_key} on endpoint"
    redacted = redact_secrets(text_with_secret)
    assert sample_key not in redacted
    assert "[REDACTED_GEMINI_KEY]" in redacted

    # Test key masking
    masked = mask_key(sample_key)
    assert masked.startswith("AIz")
    assert masked.endswith("1234")
    assert "ExampleSecretKey" not in masked


def test_quota_exhaustion_does_not_switch_to_paid():
    """
    Requirement 10: Handle quota exhaustion without silently switching to paid models.
    Must raise explicit AIQuotaExhaustedError.
    """
    provider = GeminiProvider(api_key="AIzaSyFakeKey12345678901234567890123")
    quota_err = errors.APIError(
        429,
        {"error": {"message": "ResourceExhausted: You have exceeded your current quota. Check your plan."}},
    )
    mapped = provider._map_error(quota_err)
    assert isinstance(mapped, AIQuotaExhaustedError)
    assert "quota has been exhausted" in mapped.message
    assert "paid models" in mapped.message


def test_rate_limit_error_mapping():
    """Verify 429 rate limit is mapped to AIRateLimitError."""
    provider = GeminiProvider(api_key="AIzaSyFakeKey12345678901234567890123")
    rate_err = errors.APIError(
        429,
        {"error": {"message": "Rate limit exceeded for requests per minute (RPM)."}},
    )
    mapped = provider._map_error(rate_err)
    assert isinstance(mapped, AIRateLimitError)
    assert "rate limit reached" in mapped.message


def test_timeout_error_mapping():
    """Verify timeouts raise AITimeoutError."""
    provider = GeminiProvider(api_key="AIzaSyFakeKey12345678901234567890123")
    timeout_err = TimeoutError("Request timed out after 30.0s")
    mapped = provider._map_error(timeout_err)
    assert isinstance(mapped, AITimeoutError)


def test_reusable_factory_and_custom_provider():
    """
    Requirement 8: Build a reusable AI provider service so another provider can be added later.
    """
    # 1. Default factory returns GeminiProvider
    p = get_ai_provider("gemini", api_key="AIzaSyTest1234567890123456789012345")
    assert isinstance(p, GeminiProvider)

    # 2. Register a new custom provider class
    class MockCustomProvider(BaseAIProvider):
        provider_name = "custom"
        default_model = "custom-v1"

        def __init__(self, api_key=None, model=None, **kwargs):
            self.api_key = api_key
            self.model = model or self.default_model

        async def generate_text(self, prompt, **kwargs):
            return "Custom response"

        async def generate_structured(self, prompt, response_schema, **kwargs):
            return response_schema()

        async def test_connection(self):
            return {"status": "ok"}

    register_ai_provider("custom_ai", MockCustomProvider)
    custom_p = get_ai_provider("custom_ai")
    assert isinstance(custom_p, MockCustomProvider)

    # 3. Reject unknown provider
    with pytest.raises(AIProviderError) as exc_info:
        get_ai_provider("unknown_provider_xyz")
    assert "Unsupported AI provider" in str(exc_info.value)


@pytest.mark.asyncio
async def test_structured_json_generation_mock():
    """
    Requirement 9: Support structured JSON responses for extraction.
    """
    provider = GeminiProvider(api_key="AIzaSyFakeKey12345678901234567890123")

    mock_json_response = """{
        "question_number": 1,
        "section": "QA",
        "question_type": "MCQ",
        "question_text": "In a race of 200m, A beats B by 20m. Find ratio of speeds.",
        "has_passage": false,
        "options": [
            {"label": "A", "text": "10:9", "is_correct": true},
            {"label": "B", "text": "9:10", "is_correct": false},
            {"label": "C", "text": "5:4", "is_correct": false},
            {"label": "D", "text": "4:5", "is_correct": false}
        ],
        "correct_answer": "A",
        "solution_text": "Speed ratio equals distance ratio: 200/(200-20) = 200/180 = 10/9.",
        "difficulty": "medium",
        "confidence": 0.95
    }"""

    mock_resp = MagicMock()
    mock_resp.text = mock_json_response

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)

    with patch.object(provider, "_get_client", return_value=mock_client):
        parsed = await provider.generate_structured(
            prompt="Extract question",
            response_schema=ExtractedQuestionSchema,
        )
        assert parsed.question_number == 1
        assert parsed.section == "QA"
        assert parsed.question_type == "MCQ"
        assert len(parsed.options) == 4
        assert parsed.correct_answer == "A"
        assert parsed.difficulty == "medium"


def test_independent_deterministic_math_verification_veto():
    """
    Requirement 11 & 12:
    Never claim a question is verified solely because Gemini generated an answer.
    Deterministic arithmetic verification must independently catch and reject math contradictions.
    """
    # Contradictory statement with explicit equality
    contradictory_text = "A vendor notes that 25 * 4 = 120 items are available in stock."
    valid, contradiction = verify_arithmetic_statement(contradictory_text)
    # 25 * 4 = 100 != 120
    assert not valid
    assert "Arithmetic contradiction" in contradiction
    assert "120" in contradiction

    # Correct statement passes
    correct_text = "A vendor notes that 25 * 4 = 100 items are available in stock."
    valid, contradiction = verify_arithmetic_statement(correct_text)
    assert valid
