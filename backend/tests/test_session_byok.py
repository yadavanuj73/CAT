"""
Automated tests for Session-First BYOK architecture and credential isolation.
"""

import time
from app.security.session import SessionKeyStore
from app.security.redaction import redact_secrets, mask_key


def test_session_store_isolation():
    store = SessionKeyStore()
    user_a = "user-uuid-1"
    user_b = "user-uuid-2"
    sess_a = "session-token-alpha"
    sess_b = "session-token-beta"

    key_a = "sk-proj-user-a-secret-key-12345"
    key_b = "sk-proj-user-b-secret-key-67890"

    store.set_key(user_a, sess_a, key_a)
    store.set_key(user_b, sess_b, key_b)

    # User A cannot retrieve User B's key
    assert store.get_key(user_a, sess_a) == key_a
    assert store.get_key(user_b, sess_b) == key_b
    assert store.get_key(user_a, sess_b) is None

    # Status hides the raw key
    status = store.get_status(user_a, sess_a)
    assert status["is_set"] is True
    assert "sk-" in status["masked_key"]
    assert key_a not in status["masked_key"]

    # Deletion expunges immediately
    assert store.delete_key(user_a, sess_a) is True
    assert store.get_key(user_a, sess_a) is None


def test_credential_redaction():
    raw_log = "Error in OpenAI API call with key sk-proj-1234567890abcdefghijklmn: rate limited"
    clean_log = redact_secrets(raw_log)
    assert "sk-proj-" not in clean_log
    assert "[REDACTED_API_KEY]" in clean_log


def test_mask_key():
    assert mask_key("sk-1234567890abcdef") == "sk-...cdef"
    assert mask_key("short") == "****"
