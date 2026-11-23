"""
Crypto service for persistent (opt-in) API credentials.
Handles AES-256-GCM encryption, decryption, and secure deletion from database.
"""

import uuid
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import EncryptedCredential
from app.security.encryption import encrypt_credential, decrypt_credential
from app.security.redaction import mask_key


async def save_user_credential(
    db: AsyncSession,
    user_id: uuid.UUID,
    api_key: str,
    provider: str = "openai"
) -> EncryptedCredential:
    """Encrypt and store an API key in the database (Opt-in mode)."""
    ciphertext, iv, tag, key_version = encrypt_credential(api_key)

    # Remove existing credential for provider if present
    await db.execute(
        delete(EncryptedCredential).where(
            EncryptedCredential.user_id == user_id,
            EncryptedCredential.provider == provider,
        )
    )

    credential = EncryptedCredential(
        user_id=user_id,
        provider=provider,
        encrypted_key=ciphertext,
        iv=iv,
        auth_tag=tag,
        key_version=key_version,
    )
    db.add(credential)
    await db.commit()
    await db.refresh(credential)
    return credential


async def get_user_credential(
    db: AsyncSession,
    user_id: uuid.UUID,
    provider: str = "openai"
) -> Optional[str]:
    """Retrieve and decrypt stored credential for authorized background execution."""
    stmt = select(EncryptedCredential).where(
        EncryptedCredential.user_id == user_id,
        EncryptedCredential.provider == provider,
    )
    result = await db.execute(stmt)
    cred = result.scalar_one_or_none()
    if not cred:
        return None

    try:
        return decrypt_credential(cred.encrypted_key, cred.iv, cred.auth_tag, cred.key_version)
    except Exception:
        return None


async def delete_user_credential(
    db: AsyncSession,
    user_id: uuid.UUID,
    provider: str = "openai"
) -> bool:
    """Hard delete saved credential from database."""
    result = await db.execute(
        delete(EncryptedCredential).where(
            EncryptedCredential.user_id == user_id,
            EncryptedCredential.provider == provider,
        )
    )
    await db.commit()
    return result.rowcount > 0


async def get_credential_status(
    db: AsyncSession,
    user_id: uuid.UUID,
    provider: str = "openai"
) -> dict:
    """Return status indicating whether key is saved, with masked preview."""
    key = await get_user_credential(db, user_id, provider)
    if key:
        return {
            "provider": provider,
            "is_set": True,
            "is_saved": True,
            "masked_key": mask_key(key),
        }
    return {
        "provider": provider,
        "is_set": False,
        "is_saved": False,
        "masked_key": None,
    }
