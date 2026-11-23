"""
Authentication and Session Dependencies for FastAPI endpoints.
Extracts user from JWT cookie or Authorization header.
Extracts session ID for ephemeral in-memory BYOK API key lookup.
"""

import uuid
from typing import Optional
from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.services.auth_service import decode_access_token, get_user_by_id


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
) -> User:
    """Extract authenticated user from Authorization header or httpOnly cookie."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed user credential.",
        )

    user = await get_user_by_id(db, user_uuid)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is deactivated.",
        )

    return user


def get_session_id(
    authorization: Optional[str] = Header(None),
    session_id: Optional[str] = Cookie(None),
    x_session_id: Optional[str] = Header(None),
) -> str:
    """Return active session identifier for ephemeral key isolation."""
    if x_session_id:
        return x_session_id
    if session_id:
        return session_id
    if authorization and authorization.startswith("Bearer "):
        # Use first 16 chars of JWT as deterministic session token
        return authorization.split(" ", 1)[1][:16]
    return "default_session"
