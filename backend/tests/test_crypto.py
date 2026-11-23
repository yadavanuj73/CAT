"""
Automated tests for AES-256-GCM authenticated encryption.
"""

import pytest
from app.security.encryption import encrypt_credential, decrypt_credential


def test_aes_gcm_roundtrip():
    secret_key = "sk-proj-test1234567890abcdefghijklmnopqrstuvwxyz"
    ciphertext, iv, tag, version = encrypt_credential(secret_key)

    assert ciphertext != secret_key.encode()
    assert len(iv) == 12
    assert len(tag) == 16
    assert version == 1

    decrypted = decrypt_credential(ciphertext, iv, tag, version)
    assert decrypted == secret_key


def test_aes_gcm_tamper_detection():
    secret_key = "sk-proj-integrity-test-key"
    ciphertext, iv, tag, version = encrypt_credential(secret_key)

    # Tamper with the ciphertext
    tampered_ciphertext = bytearray(ciphertext)
    tampered_ciphertext[0] ^= 0xFF

    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_credential(bytes(tampered_ciphertext), iv, tag, version)
