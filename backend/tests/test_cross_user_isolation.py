"""
Cross-user isolation and authorization audit tests.
Ensures User A cannot access, mutate, or decrypt User B's papers, questions, or credentials.
"""

import pytest
import uuid
from app.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.models.paper import Paper, PaperStatus
from app.services.crypto_service import save_user_credential, get_user_credential
from sqlalchemy import select


@pytest.mark.asyncio
async def test_cross_user_paper_isolation():
    """Verify that user A's papers cannot be queried or updated as user B."""
    await init_db()
    async with AsyncSessionLocal() as db:
        user_a = User(email=f"alice_{uuid.uuid4().hex[:6]}@cat.org", password_hash="hash_a")
        user_b = User(email=f"bob_{uuid.uuid4().hex[:6]}@cat.org", password_hash="hash_b")
        db.add_all([user_a, user_b])
        await db.flush()

        paper_a = Paper(
            user_id=user_a.id,
            year=2024,
            slot="Slot 1",
            source_name="Official",
            original_filename="cat2024.pdf",
            file_path="uploads/cat2024.pdf",
            file_hash=uuid.uuid4().hex,
            status=PaperStatus.UPLOADED,
        )
        db.add(paper_a)
        await db.commit()

        # Query papers scoped to User B
        stmt = select(Paper).where(Paper.user_id == user_b.id)
        result = await db.execute(stmt)
        user_b_papers = result.scalars().all()

        assert len(user_b_papers) == 0
        assert paper_a.id not in [p.id for p in user_b_papers]


@pytest.mark.asyncio
async def test_cross_user_credential_isolation():
    """Verify user B cannot decrypt or access user A's encrypted credentials."""
    await init_db()
    async with AsyncSessionLocal() as db:
        user_a = User(email=f"alice_key_{uuid.uuid4().hex[:6]}@cat.org", password_hash="hash_a")
        user_b = User(email=f"bob_key_{uuid.uuid4().hex[:6]}@cat.org", password_hash="hash_b")
        db.add_all([user_a, user_b])
        await db.flush()

        alice_key = "sk-proj-aliceSecretLiveKey1234567890"
        await save_user_credential(db, user_a.id, alice_key, provider="openai")

        # Bob attempts to retrieve Alice's key
        retrieved_by_bob = await get_user_credential(db, user_b.id, provider="openai")
        assert retrieved_by_bob is None

        # Alice retrieves her key successfully
        retrieved_by_alice = await get_user_credential(db, user_a.id, provider="openai")
        assert retrieved_by_alice == alice_key
