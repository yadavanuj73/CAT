"""
CSRF protection utilities for state-changing requests.
"""

import hmac
import hashlib
import secrets
from app.config import settings


def generate_csrf_token(user_id: str) -> str:
    """Generate a signed, secure CSRF token for the authenticated user session."""
    random_bytes = secrets.token_hex(16)
    signature = hmac.new(
        settings.JWT_SECRET_KEY.encode(),
        f"{user_id}:{random_bytes}".encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{random_bytes}.{signature}"


def verify_csrf_token(user_id: str, token: str) -> bool:
    """Verify CSRF token authenticity."""
    if not token or "." not in token:
        return False
    parts = token.split(".", 1)
    if len(parts) != 2:
        return False
    random_bytes, signature = parts
    expected_sig = hmac.new(
        settings.JWT_SECRET_KEY.encode(),
        f"{user_id}:{random_bytes}".encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_sig)
