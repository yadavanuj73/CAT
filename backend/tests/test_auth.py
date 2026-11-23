"""
Automated tests for Authentication & JWT tokens.
"""

import pytest
import uuid
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hashing():
    pwd = "SecureCAT2026Password!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_generation_and_decoding():
    user_id = uuid.uuid4()
    email = "aspirant@cat2026.org"
    token = create_access_token(user_id, email)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["email"] == email


def test_invalid_jwt():
    assert decode_access_token("invalid.token.structure") is None
