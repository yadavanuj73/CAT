"""
BYOK API Key Management Router.
Strict Session-First BYOK architecture:
- Default: Session-only ephemeral memory store.
- Optional: Opt-in AES-256-GCM encrypted persistence.
- Never returns raw API keys in response.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user, get_session_id
from app.schemas.api_keys import ApiKeyStatusResponse, SaveApiKeyRequest, SessionApiKeyRequest
from app.security.session import session_key_store
from app.services.crypto_service import (
    delete_user_credential,
    save_user_credential,
)
from app.services.session_service import resolve_key_status

router = APIRouter(prefix="/keys", tags=["API Keys"])


def _validate_api_key_format(api_key: str, provider: str = "gemini") -> None:
    """Validate format depending on provider."""
    prov = (provider or "gemini").lower()
    if prov in ("gemini", "google"):
        if not (api_key.startswith("AIza") or len(api_key) >= 20):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google Gemini API key format. Expected key starting with 'AIza' or minimum 20 characters.",
            )
    elif prov == "openai":
        if not api_key.startswith("sk-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OpenAI API key format. Expected key starting with 'sk-'.",
            )
    elif len(api_key) < 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid API key format for provider '{provider}'.",
        )


@router.post("/session", response_model=ApiKeyStatusResponse)
async def set_session_key(
    req: SessionApiKeyRequest,
    current_user: User = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
):
    """
    Set ephemeral API key for the current session (DEFAULT MODE).
    Key lives strictly in server RAM and is purged on logout or server restart.
    Never persisted to database or disk.
    """
    _validate_api_key_format(req.api_key, req.provider)

    session_key_store.set_key(str(current_user.id), session_id, req.api_key, req.provider)
    status_dict = session_key_store.get_status(str(current_user.id), session_id)
    return ApiKeyStatusResponse(**status_dict)


@router.post("/save", response_model=ApiKeyStatusResponse)
async def save_encrypted_key(
    req: SaveApiKeyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Save API key with AES-256-GCM authenticated encryption (OPT-IN MODE).
    User explicitly accepts persistent storage risk.
    """
    _validate_api_key_format(req.api_key, req.provider)

    await save_user_credential(db, current_user.id, req.api_key, req.provider)
    from app.services.crypto_service import get_credential_status
    status_dict = await get_credential_status(db, current_user.id, req.provider)
    return ApiKeyStatusResponse(**status_dict)


@router.delete("", response_model=ApiKeyStatusResponse)
async def delete_key(
    current_user: User = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Expunge all API credentials:
    - Removes ephemeral key from server RAM
    - Hard-deletes AES-256-GCM encrypted record from database
    """
    session_key_store.delete_key(str(current_user.id), session_id)
    await delete_user_credential(db, current_user.id)
    return ApiKeyStatusResponse(
        provider="gemini",
        is_set=False,
        is_saved=False,
        masked_key=None,
    )


@router.get("/status", response_model=ApiKeyStatusResponse)
async def get_key_status(
    current_user: User = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
):
    """Check whether an API key is currently active, without disclosing the key."""
    status_dict = await resolve_key_status(db, current_user.id, session_id)
    return ApiKeyStatusResponse(**status_dict)
