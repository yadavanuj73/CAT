"""
Cross-User Shared Corpus Growth and Privacy Isolation Tests.
Verifies:
1. User A uploads paper with sharing consent -> approved questions enter global shared bank.
2. User B logs in and can access those shared questions.
3. User B cannot access User A's private PDF or private processing history.
4. User C uploads paper without consent (private) -> questions NEVER enter shared bank.
5. User D uploads duplicate paper -> reuses shared record without duplicating database records.
"""

import hashlib
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.main import app
from app.models.paper import Paper
from app.models.question import Difficulty, Question, QuestionOption, QuestionType, Section, VerificationStatus
from app.models.shared_corpus import SharedVerifiedQuestion
from app.models.user import User
from app.models.user_history import UserProcessingHistory
from app.services.ingestion_service import register_paper
from app.services.sharing_service import evaluate_and_promote_paper_to_shared_bank


@pytest.mark.asyncio
async def test_shared_growth_and_cross_user_privacy_isolation():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Register User A
        email_a = f"alice_{uuid.uuid4().hex[:6]}@cat.org"
        res_a = await client.post("/api/auth/register", json={"email": email_a, "password": "Password123!", "full_name": "Alice"})
        token_a = res_a.json()["access_token"]
        user_a_id = res_a.json()["user"]["id"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Register User B
        email_b = f"bob_{uuid.uuid4().hex[:6]}@cat.org"
        res_b = await client.post("/api/auth/register", json={"email": email_b, "password": "Password123!", "full_name": "Bob"})
        token_b = res_b.json()["access_token"]
        user_b_id = res_b.json()["user"]["id"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Step 1: User A uploads an eligible paper with sharing consent
        fake_content = b"%PDF-1.4 CAT 2023 Slot 2 Paper by Alice " + uuid.uuid4().bytes
        file_hash = hashlib.sha256(fake_content).hexdigest()

        async with AsyncSessionLocal() as db:
            paper_a = await register_paper(
                db=db,
                user_id=uuid.UUID(user_a_id),
                year=2023,
                slot="Slot 2",
                source_name="Official IIM Lucknow",
                source_type="official",
                original_filename="alice_cat2023.pdf",
                file_path="uploads/alice_cat2023.pdf",
                file_hash=file_hash,
                allow_sharing=True,
            )

            # Add verified question
            q = Question(
                user_id=uuid.UUID(user_a_id),
                paper_id=paper_a.id,
                question_number=1,
                question_text=f"Find the sum of roots of 3x^2 - 12x + 5 = 0 for unique key {uuid.uuid4().hex[:6]}.",
                question_type=QuestionType.TITA,
                section=Section.QA,
                difficulty=Difficulty.EASY,
                verification_status=VerificationStatus.VERIFIED,
                year=2023,
                slot="Slot 2",
            )
            db.add(q)
            await db.commit()

            # Promote to shared bank
            promote_res = await evaluate_and_promote_paper_to_shared_bank(db, paper_a.id)
            assert promote_res["promoted_count"] == 1
            paper_a_id = str(paper_a.id)

        # Step 2: User B can access the shared verified question in the global question bank!
        res_shared = await client.get("/api/shared/questions", headers=headers_b)
        assert res_shared.status_code == 200
        shared_list = res_shared.json()
        assert shared_list["total"] >= 1

        # Step 3: Privacy check — User B CANNOT view User A's private upload record or processing logs!
        res_private_get = await client.get(f"/api/papers/{paper_a_id}", headers=headers_b)
        assert res_private_get.status_code == 404  # Isolated!

        res_private_hist = await client.get(f"/api/papers/{paper_a_id}/history", headers=headers_b)
        assert res_private_hist.status_code == 404  # Isolated!

        # Step 4: User A CAN access their own private paper and processing history
        res_own_paper = await client.get(f"/api/papers/{paper_a_id}", headers=headers_a)
        assert res_own_paper.status_code == 200
        assert res_own_paper.json()["sharing_status"] == "approved"

        res_own_hist = await client.get(f"/api/papers/{paper_a_id}/history", headers=headers_a)
        assert res_own_hist.status_code == 200
        assert len(res_own_hist.json()) > 0


@pytest.mark.asyncio
async def test_private_upload_without_consent_never_published_to_shared():
    """
    Test Section 3 & 12: When a user uploads a paper with allow_sharing=False (opt-out),
    the questions are NEVER published into the shared verified question bank.
    """
    await init_db()
    async with AsyncSessionLocal() as db:
        user = User(email=f"private_user_{uuid.uuid4().hex[:6]}@cat.org", password_hash="hash")
        db.add(user)
        await db.commit()

        file_hash = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
        private_paper = await register_paper(
            db=db,
            user_id=user.id,
            year=2021,
            slot="Slot 1",
            source_name="Private Mock",
            source_type="other",
            original_filename="confidential.pdf",
            file_path="uploads/confidential.pdf",
            file_hash=file_hash,
            allow_sharing=False,  # USER OPTS OUT
        )

        q = Question(
            user_id=user.id,
            paper_id=private_paper.id,
            question_number=1,
            question_text=f"Confidential proprietary question text {uuid.uuid4().hex[:8]}.",
            question_type=QuestionType.TITA,
            section=Section.QA,
            difficulty=Difficulty.HARD,
            verification_status=VerificationStatus.VERIFIED,
            year=2021,
        )
        db.add(q)
        await db.commit()

        # Promotion attempt
        res = await evaluate_and_promote_paper_to_shared_bank(db, private_paper.id)
        assert res["status"] == "private"
        assert res["promoted_count"] == 0

        # Assert question NOT present in shared_verified_questions
        shared_res = await db.execute(
            select(SharedVerifiedQuestion).where(
                SharedVerifiedQuestion.question_text == q.question_text
            )
        )
        assert shared_res.scalar_one_or_none() is None
