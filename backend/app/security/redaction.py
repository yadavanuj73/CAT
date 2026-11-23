"""
Credential redaction utilities for logs, error messages, and responses.
Guarantees API keys and secrets are never exposed in logs or exception reports.
"""

import re
from typing import Any

# Patterns matching API keys (Gemini AIza..., OpenAI sk-..., Bearer tokens, passwords)
KEY_PATTERNS = [
    (re.compile(r"AIza[a-zA-Z0-9_\-]{30,}", re.IGNORECASE), "[REDACTED_GEMINI_KEY]"),
    (re.compile(r"sk-[a-zA-Z0-9_-]{20,}", re.IGNORECASE), "[REDACTED_API_KEY]"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"('password'|\"password\"):\s*('|\")[^'\"]+('|\")", re.IGNORECASE), r'\1: "[REDACTED]"'),
    (re.compile(r"('password_hash'|\"password_hash\"):\s*('|\")[^'\"]+('|\")", re.IGNORECASE), r'\1: "[REDACTED]"'),
]


def redact_secrets(text: Any) -> str:
    """Redact known secret patterns from any string or representation."""
    if not isinstance(text, str):
        text = str(text)

    for pattern, replacement in KEY_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def mask_key(key: str) -> str:
    """Safely format an API key for display (e.g., sk-...a1b2)."""
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return f"{key[:3]}...{key[-4:]}"
