"""
BYOK credential resolver service.
Prioritizes volatile server-side session memory (default).
Falls back to encrypted database storage if the user explicitly opted-in.
Never reveals the raw key in logs or outward responses.
"""

import os
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.security.session import session_key_store
from app.services.crypto_service import get_user_credential, get_credential_status


async def resolve_api_key(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: str,
    provider: str = "gemini"
) -> Optional[str]:
    """
    Resolve active API key for execution:
    1. Check ephemeral session memory (preferred default)
    2. Check AES-256-GCM encrypted persistence (opt-in)
    3. Fallback to server environment GEMINI_API_KEY if configured
    """
    # 1. Ephemeral memory
    session_key = session_key_store.get_key(str(user_id), session_id)
    if session_key:
        return session_key

    # 2. Encrypted database
    saved_key = await get_user_credential(db, user_id, provider)
    if saved_key:
        return saved_key

    # 3. Server environment variable fallback
    if provider in ("gemini", "google"):
        server_key = getattr(settings, "GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
        if server_key:
            return server_key

    return None


async def resolve_key_status(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: str,
    provider: str = "gemini"
) -> dict:
    """Return overall API key status for the user."""
    # Check session memory first
    session_status = session_key_store.get_status(str(user_id), session_id)
    if session_status.get("is_set"):
        return session_status

    # Check saved credential
    saved_status = await get_credential_status(db, user_id, provider)
    if saved_status.get("is_set"):
        return saved_status

    # Check server environment fallback
    if provider in ("gemini", "google"):
        server_key = getattr(settings, "GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
        if server_key:
            masked = f"{server_key[:4]}...{server_key[-4:]}" if len(server_key) >= 8 else "AIza...****"
            return {
                "provider": "gemini",
                "is_set": True,
                "is_saved": True,
                "masked_key": f"{masked} (Server Env)",
            }

    return saved_status
