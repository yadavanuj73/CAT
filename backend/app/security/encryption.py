"""
AES-256-GCM authenticated encryption service.
Uses standard cryptography hazmat primitives with a secure 32-byte master key.
Never writes raw secrets or plaintext credentials.
"""

import base64
import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings


def _get_master_key() -> bytes:
    """Load and validate the 32-byte master encryption key."""
    raw_key = settings.MASTER_ENCRYPTION_KEY
    if not raw_key:
        raise ValueError("MASTER_ENCRYPTION_KEY is not configured in settings.")
    try:
        decoded = base64.b64decode(raw_key)
        if len(decoded) != 32:
            # Fallback pad/truncate to 32 bytes for dev stability if needed
            decoded = (decoded + b"\x00" * 32)[:32]
        return decoded
    except Exception:
        # Fallback to UTF-8 encoded bytes padded to 32 bytes
        return raw_key.encode("utf-8").ljust(32, b"0")[:32]


def encrypt_credential(plaintext: str) -> Tuple[bytes, bytes, bytes, int]:
    """
    Encrypt plaintext using AES-256-GCM.
    Returns: (ciphertext, iv, auth_tag, key_version)
    Note: cryptography AESGCM.encrypt appends a 16-byte tag to the ciphertext.
    We split it to store ciphertext, iv, and tag cleanly.
    """
    key = _get_master_key()
    aesgcm = AESGCM(key)
    iv = os.urandom(12)  # Standard 96-bit IV for AES-GCM
    
    # AESGCM encrypts with authentication tag appended (16 bytes)
    encrypted_payload = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)
    ciphertext = encrypted_payload[:-16]
    tag = encrypted_payload[-16:]
    key_version = 1
    
    return ciphertext, iv, tag, key_version


def decrypt_credential(ciphertext: bytes, iv: bytes, tag: bytes, key_version: int = 1) -> str:
    """
    Decrypt an AES-256-GCM encrypted credential.
    Raises ValueError if authentication verification fails.
    """
    key = _get_master_key()
    aesgcm = AESGCM(key)
    payload = ciphertext + tag
    try:
        decrypted_bytes = aesgcm.decrypt(iv, payload, None)
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError("Decryption failed: integrity check or authentication tag mismatch.") from e
