"""
Background Processing, Ingestion & Restart Failure Recovery Audit Tests.
Tests:
1. Duplicate ingestion handling (SHA-256 deduplication).
2. Processing status persistence.
3. Interrupted extraction recovery (Render restart simulation).
4. Key rotation service execution.
"""

import pytest
import uuid
from app.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.models.paper import Paper, PaperStatus
from app.services.ingestion_service import register_paper, recover_stalled_paper_extractions
from app.security.encryption import register_key_version, rotate_credential, encrypt_credential, decrypt_credential


@pytest.mark.asyncio
async def test_duplicate_paper_ingestion_deduplication():
    """Verify that re-uploading the same paper hash returns the existing paper without duplicate inserts."""
    await init_db()
    async with AsyncSessionLocal() as db:
        user = User(email=f"dedup_{uuid.uuid4().hex[:6]}@cat.org", password_hash="dummy")
        db.add(user)
        await db.flush()

        file_hash = uuid.uuid4().hex

        paper1 = await register_paper(
            db=db,
            user_id=user.id,
            year=2023,
            slot="Slot 2",
            source_name="Official",
            source_type="official",
            original_filename="cat2023_slot2.pdf",
            file_path="uploads/cat2023_slot2.pdf",
            file_hash=file_hash,
        )

        # Upload duplicate with same hash
        paper2 = await register_paper(
            db=db,
            user_id=user.id,
            year=2023,
            slot="Slot 2",
            source_name="Official",
            source_type="official",
            original_filename="cat2023_slot2_copy.pdf",
            file_path="uploads/cat2023_slot2_copy.pdf",
            file_hash=file_hash,
        )

        assert paper1.id == paper2.id, "Duplicate upload must resolve to existing paper."


@pytest.mark.asyncio
async def test_restart_recovery_for_stalled_extractions():
    """Simulate server termination during PDF extraction and test recovery to FAILED."""
    await init_db()
    async with AsyncSessionLocal() as db:
        user = User(email=f"restart_{uuid.uuid4().hex[:6]}@cat.org", password_hash="dummy")
        db.add(user)
        await db.flush()

        # Paper left in EXTRACTING when server restarted
        stalled_paper = Paper(
            user_id=user.id,
            year=2022,
            slot="Slot 1",
            source_name="Official",
            original_filename="cat2022.pdf",
            file_path="uploads/cat2022.pdf",
            file_hash=uuid.uuid4().hex,
            status=PaperStatus.EXTRACTING,  # Stalled!
        )
        db.add(stalled_paper)
        await db.commit()

        # Run startup recovery
        recovered_count = await recover_stalled_paper_extractions(db)
        assert recovered_count >= 1

        await db.refresh(stalled_paper)
        assert stalled_paper.status == PaperStatus.FAILED
        assert "interrupted by container restart" in stalled_paper.notes.lower()


def test_key_rotation_service():
    """Verify credential rotation from key version 1 to key version 2."""
    v1_bytes = b"master_key_version_1_32bytes_123"
    v2_bytes = b"master_key_version_2_32bytes_456"

    register_key_version(1, v1_bytes)
    register_key_version(2, v2_bytes)

    secret = "sk-proj-rotation-test-api-key"
    ciphertext1, iv1, tag1, v1 = encrypt_credential(secret, version=1)
    assert v1 == 1

    # Rotate to version 2
    ciphertext2, iv2, tag2, v2 = rotate_credential(ciphertext1, iv1, tag1, current_version=1, new_version=2)
    assert v2 == 2

    # Verify decryption with version 2
    decrypted = decrypt_credential(ciphertext2, iv2, tag2, key_version=2)
    assert decrypted == secret
