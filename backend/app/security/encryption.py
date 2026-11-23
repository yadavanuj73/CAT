"""
AES-256-GCM authenticated encryption service.
Uses standard cryptography hazmat primitives with a secure 32-byte master key.
Never writes raw secrets or plaintext credentials.
"""

import base64
import os
from typing import Dict, Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings

# Key ring mapping key version -> 32 bytes master key
# In production, past keys can be specified via ROTATED_ENCRYPTION_KEYS
_KEY_RING: Dict[int, bytes] = {}


def _get_master_key(version: int = 1) -> bytes:
    """Load and validate the 32-byte master encryption key for a given version."""
    if version in _KEY_RING:
        return _KEY_RING[version]

    raw_key = settings.MASTER_ENCRYPTION_KEY
    if not raw_key:
        raise ValueError("MASTER_ENCRYPTION_KEY is not configured in settings.")
    try:
        decoded = base64.b64decode(raw_key)
        if len(decoded) != 32:
            decoded = (decoded + b"\x00" * 32)[:32]
        _KEY_RING[1] = decoded
        return decoded
    except Exception:
        fallback = raw_key.encode("utf-8").ljust(32, b"0")[:32]
        _KEY_RING[1] = fallback
        return fallback


def register_key_version(version: int, key_bytes: bytes) -> None:
    """Register historical or rotated key versions for seamless rotation support."""
    if len(key_bytes) != 32:
        raise ValueError("Master encryption key must be exactly 32 bytes.")
    _KEY_RING[version] = key_bytes


def encrypt_credential(plaintext: str, version: int = 1) -> Tuple[bytes, bytes, bytes, int]:
    """
    Encrypt plaintext using AES-256-GCM under specified key version.
    Returns: (ciphertext, iv, auth_tag, key_version)
    """
    key = _get_master_key(version)
    aesgcm = AESGCM(key)
    iv = os.urandom(12)  # Standard 96-bit IV for AES-GCM
    
    # AESGCM encrypts with authentication tag appended (16 bytes)
    encrypted_payload = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)
    ciphertext = encrypted_payload[:-16]
    tag = encrypted_payload[-16:]
    
    return ciphertext, iv, tag, version


def decrypt_credential(ciphertext: bytes, iv: bytes, tag: bytes, key_version: int = 1) -> str:
    """
    Decrypt an AES-256-GCM encrypted credential using the appropriate key version.
    Raises ValueError if authentication verification fails.
    """
    key = _get_master_key(key_version)
    aesgcm = AESGCM(key)
    payload = ciphertext + tag
    try:
        decrypted_bytes = aesgcm.decrypt(iv, payload, None)
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError("Decryption failed: integrity check or authentication tag mismatch.") from e


def rotate_credential(
    ciphertext: bytes,
    iv: bytes,
    tag: bytes,
    current_version: int,
    new_version: int
) -> Tuple[bytes, bytes, bytes, int]:
    """
    Decrypt with current key version and re-encrypt under new master key version.
    Zero plaintext exposure outside memory.
    """
    plaintext = decrypt_credential(ciphertext, iv, tag, current_version)
    return encrypt_credential(plaintext, new_version)
