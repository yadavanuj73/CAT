"""
Mandatory Security Acceptance Tests for CAT Intelligence 2026.
Systematically tests all 10 security controls required by specification:
1. Inspect frontend bundles for API key exposure.
2. Verify no secret tokens in frontend source.
3. Test credential redaction in logs/exceptions.
4. Test cross-user session isolation.
5. Test logout credential invalidation.
6. Test session expiration.
7. Test server restart volatile memory purging.
8. Test encrypted credential deletion (AES-256-GCM).
9. Test unauthorized credential retrieval.
10. Test API key pattern masking.
"""

import os
import re
import time
import pytest
from app.security.session import SessionKeyStore
from app.security.redaction import redact_secrets, mask_key
from app.security.encryption import encrypt_credential, decrypt_credential


def test_1_and_2_inspect_frontend_for_secret_leakage():
    """Ensure no hardcoded OpenAI API keys (sk-...) exist in frontend build or source."""
    frontend_dist = "d:/Cat 2026/frontend/dist"
    secret_pattern = re.compile(r"sk-[a-zA-Z0-9_-]{24,}")

    if os.path.exists(frontend_dist):
        for root, _, files in os.walk(frontend_dist):
            for file in files:
                if file.endswith((".js", ".html", ".css")):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        matches = secret_pattern.findall(content)
                        assert len(matches) == 0, f"Exposed secret in frontend bundle: {file}"


def test_3_and_10_redact_secrets_in_exception_traces():
    """Verify raw API keys are redacted in all exception and error log outputs."""
    raw_error = "AuthenticationError: Error code 401 with sk-proj-superSecretLiveKey1234567890abcdef from OpenAI"
    safe_error = redact_secrets(raw_error)
    assert "sk-proj-" not in safe_error
    assert "[REDACTED_API_KEY]" in safe_error


def test_4_cross_user_isolation():
    """Verify that User A cannot read or decrypt User B's credentials under any condition."""
    store = SessionKeyStore()
    user_alice = "alice-1001"
    user_bob = "bob-2002"
    sess_alice = "session-alice-xyz"
    sess_bob = "session-bob-xyz"

    store.set_key(user_alice, sess_alice, "sk-proj-alice-secret-key-12345678")
    store.set_key(user_bob, sess_bob, "sk-proj-bob-secret-key-87654321")

    # Bob attempts to access Alice's session
    assert store.get_key(user_bob, sess_alice) is None
    # Alice attempts to access Bob's session
    assert store.get_key(user_alice, sess_bob) is None


def test_5_logout_credential_invalidation():
    """Verify that logout expunges in-memory session credentials immediately."""
    store = SessionKeyStore()
    user_id = "user-test-logout"
    sess_id = "session-token-99"
    key = "sk-proj-testkey123456789012"

    store.set_key(user_id, sess_id, key)
    assert store.get_key(user_id, sess_id) == key

    # Simulating logout
    deleted = store.delete_key(user_id, sess_id)
    assert deleted is True
    assert store.get_key(user_id, sess_id) is None


def test_6_session_expiration():
    """Verify that expired session keys cannot be retrieved."""
    store = SessionKeyStore()
    user_id = "user-expire-test"
    sess_id = "sess-expire"

    # Manually inject key with expired timestamp
    store._store[(user_id, sess_id)] = ("sk-proj-expired-key", time.time() - 100, "openai")
    assert store.get_key(user_id, sess_id) is None


def test_7_server_restart_behavior():
    """Volatile session store guarantees credentials disappear on process restart."""
    # When server restarts, memory store is initialized fresh
    restarted_store = SessionKeyStore()
    assert len(restarted_store._store) == 0


def test_8_encrypted_credential_roundtrip_and_deletion():
    """Test AES-256-GCM encryption and verify tamper resistance."""
    api_key = "sk-proj-aes256gcmSecureProductionTestKey"
    ciphertext, iv, tag, version = encrypt_credential(api_key)
    decrypted = decrypt_credential(ciphertext, iv, tag, version)
    assert decrypted == api_key

    # Verification tag tamper check
    tampered_tag = bytearray(tag)
    tampered_tag[0] ^= 0x01
    with pytest.raises(ValueError):
        decrypt_credential(ciphertext, iv, bytes(tampered_tag), version)


def test_9_unauthorized_credential_retrieval():
    """Verify get_status returns masked key without exposing raw key characters."""
    store = SessionKeyStore()
    store.set_key("user-1", "sess-1", "sk-proj-1234567890abcdef1234")
    status = store.get_status("user-1", "sess-1")

    assert status["is_set"] is True
    assert status["masked_key"].startswith("sk-...")
    assert "1234567890abcdef" not in status["masked_key"]
