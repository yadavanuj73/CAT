"""
Authentication router: register, login, logout, me.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user, get_session_id
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.security.csrf import generate_csrf_token
from app.security.session import session_key_store
from app.services.auth_service import (
    create_access_token,
    create_user,
    get_user_by_email,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    existing = await get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user = await create_user(db, req.email, req.password)
    token = create_access_token(user.id, user.email)
    csrf_token = generate_csrf_token(str(user.id))

    is_prod = getattr(settings, "ENVIRONMENT", "development") == "production"
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,  # Client needs to read CSRF token to send in X-CSRF-Token header
        secure=is_prod,
        samesite="lax",
    )

    return TokenResponse(
        access_token=token,
        csrf_token=csrf_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    """Authenticate existing user credentials."""
    user = await get_user_by_email(db, req.email)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token(user.id, user.email)
    csrf_token = generate_csrf_token(str(user.id))

    is_prod = getattr(settings, "ENVIRONMENT", "development") == "production"
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=is_prod,
        samesite="lax",
    )

    return TokenResponse(
        access_token=token,
        csrf_token=csrf_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
):
    """
    Log out user. Expunges in-memory session API keys immediately
    and clears authentication cookies.
    """
    session_key_store.delete_key(str(current_user.id), session_id)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="csrf_token")
    return {"message": "Successfully logged out. Session credentials cleared."}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return authenticated profile information."""
    return UserResponse.model_validate(current_user)
