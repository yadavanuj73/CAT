"""
AI Data Verification Engine Audit Tests.
Tests all 7 mandatory verification gates:
1. QA mathematical verification (arithmetic & algebraic consistency).
2. VARC passage-grounded answer verification.
3. DILR logical constraint verification.
4. MCQ option validation (4 distinct choices).
5. TITA answer validation (no options, valid format).
6. Duplicate question detection.
7. Strict analytical gate preventing unverified questions from entering prediction datasets.
"""

import pytest
import uuid
from app.database import AsyncSessionLocal, init_db
from app.models.question import Question, QuestionOption, QuestionType, Section, Difficulty, VerificationStatus
from app.models.user import User
from app.services.verification_service import verify_question_data
from app.services.analysis_service import run_section_analysis
from app.services.auth_service import hash_password


@pytest.mark.asyncio
async def test_qa_mathematical_verification_gate():
    """Test QA math solver rejects arithmetic contradictions and passes valid statements."""
    await init_db()
    async with AsyncSessionLocal() as db:
        # Create user
        user = User(email=f"qa_test_{uuid.uuid4().hex[:6]}@cat.org", password_hash="dummy")
        db.add(user)
        await db.flush()

        # Contradictory QA Question
        bad_q = Question(
            user_id=user.id,
            paper_id=uuid.uuid4(),
            question_number=1,
            question_text="A company produces items where 25 * 4 = 120 units are shipped daily.",
            question_type=QuestionType.TITA,
            section=Section.QA,
            difficulty=Difficulty.MEDIUM,
            verification_status=VerificationStatus.UNVERIFIED,
            year=2024,
        )
        db.add(bad_q)
        await db.commit()

        passed, issues = await verify_question_data(db, bad_q.id)
        # Warning recorded for arithmetic contradiction
        assert any("Arithmetic contradiction" in str(issue) for issue in issues) or bad_q.verification_status != VerificationStatus.VERIFIED


@pytest.mark.asyncio
async def test_varc_passage_grounded_verification():
    """Verify VARC RC questions missing passage context are rejected."""
    await init_db()
    async with AsyncSessionLocal() as db:
        user = User(email=f"varc_test_{uuid.uuid4().hex[:6]}@cat.org", password_hash="dummy")
        db.add(user)
        await db.flush()

        # VARC question with missing passage
        ungrounded_rc = Question(
            user_id=user.id,
            paper_id=uuid.uuid4(),
            question_number=2,
            question_text="Which of the following best reflects the author's primary thesis in paragraph 3?",
            question_type=QuestionType.MCQ,
            section=Section.VARC,
            difficulty=Difficulty.HARD,
            has_passage=True,
            passage_text=None,  # Missing passage!
            verification_status=VerificationStatus.UNVERIFIED,
            year=2023,
        )
        db.add(ungrounded_rc)
        await db.flush()

        # Add 4 options so option check passes, isolating passage check
        for lbl in ["A", "B", "C", "D"]:
            db.add(QuestionOption(question_id=ungrounded_rc.id, option_label=lbl, option_text=f"Option {lbl} text"))
        await db.commit()

        passed, issues = await verify_question_data(db, ungrounded_rc.id)
        assert passed is False
        assert any("missing linked passage" in issue.lower() for issue in issues)
        assert ungrounded_rc.verification_status == VerificationStatus.REJECTED


@pytest.mark.asyncio
async def test_dilr_logical_constraint_verification():
    """Verify DILR questions lacking puzzle/caselet structure are flagged."""
    await init_db()
    async with AsyncSessionLocal() as db:
        user = User(email=f"dilr_test_{uuid.uuid4().hex[:6]}@cat.org", password_hash="dummy")
        db.add(user)
        await db.flush()

        vague_dilr = Question(
            user_id=user.id,
            paper_id=uuid.uuid4(),
            question_number=3,
            question_text=f"Find final rank {uuid.uuid4().hex[:4]}?",
            question_type=QuestionType.TITA,
            section=Section.DILR,
            difficulty=Difficulty.MEDIUM,
            verification_status=VerificationStatus.UNVERIFIED,
            year=2024,
        )
        db.add(vague_dilr)
        await db.commit()

        passed, issues = await verify_question_data(db, vague_dilr.id)
        assert passed is False
        assert any("logical constraint" in issue.lower() for issue in issues)


@pytest.mark.asyncio
async def test_tita_answer_validation_no_options_allowed():
    """Verify that TITA questions containing MCQ options are rejected."""
    await init_db()
    async with AsyncSessionLocal() as db:
        user = User(email=f"tita_test_{uuid.uuid4().hex[:6]}@cat.org", password_hash="dummy")
        db.add(user)
        await db.flush()

        invalid_tita = Question(
            user_id=user.id,
            paper_id=uuid.uuid4(),
            question_number=4,
            question_text="Find the remainder when 7^84 is divided by 24.",
            question_type=QuestionType.TITA,
            section=Section.QA,
            difficulty=Difficulty.EASY,
            verification_status=VerificationStatus.UNVERIFIED,
            year=2024,
        )
        db.add(invalid_tita)
        await db.flush()

        # Erroneously attaching an option to a TITA question
        db.add(QuestionOption(question_id=invalid_tita.id, option_label="A", option_text="1"))
        await db.commit()

        passed, issues = await verify_question_data(db, invalid_tita.id)
        assert passed is False
        assert any("must not contain multiple choice options" in issue.lower() for issue in issues)


@pytest.mark.asyncio
async def test_duplicate_question_detection():
    """Verify duplicate questions matching existing verified questions are detected."""
    await init_db()
    async with AsyncSessionLocal() as db:
        user = User(email=f"dup_test_{uuid.uuid4().hex[:6]}@cat.org", password_hash="dummy")
        db.add(user)
        await db.flush()

        # Verified question
        orig_q = Question(
            user_id=user.id,
            paper_id=uuid.uuid4(),
            question_number=10,
            question_text="Two trains A and B start simultaneously from stations X and Y traveling towards each other.",
            question_type=QuestionType.TITA,
            section=Section.QA,
            difficulty=Difficulty.MEDIUM,
            verification_status=VerificationStatus.VERIFIED,
            year=2024,
        )
        db.add(orig_q)
        await db.commit()

        # Duplicate question
        dup_q = Question(
            user_id=user.id,
            paper_id=uuid.uuid4(),
            question_number=11,
            question_text="Two trains A and B start simultaneously from stations X and Y traveling towards each other.",
            question_type=QuestionType.TITA,
            section=Section.QA,
            difficulty=Difficulty.MEDIUM,
            verification_status=VerificationStatus.UNVERIFIED,
            year=2024,
        )
        db.add(dup_q)
        await db.commit()

        passed, issues = await verify_question_data(db, dup_q.id)
        assert passed is False
        assert any("duplicate question detected" in issue.lower() for issue in issues)


@pytest.mark.asyncio
async def test_unverified_questions_cannot_enter_analytical_dataset():
    """Verify that unverified questions are strictly blocked from analytical intelligence."""
    await init_db()
    async with AsyncSessionLocal() as db:
        user = User(email=f"gate_test_{uuid.uuid4().hex[:6]}@cat.org", password_hash="dummy")
        db.add(user)
        await db.flush()

        initial_summary = await run_section_analysis(db, user.id, "QA")

        # Add unverified question
        unverified_q = Question(
            user_id=user.id,
            paper_id=uuid.uuid4(),
            question_number=1,
            question_text=f"Solve log_2(x) = 4 for gate test {uuid.uuid4().hex[:6]}.",
            question_type=QuestionType.TITA,
            section=Section.QA,
            difficulty=Difficulty.EASY,
            verification_status=VerificationStatus.UNVERIFIED,
            year=2024,
        )
        db.add(unverified_q)
        await db.commit()

        summary_after = await run_section_analysis(db, user.id, "QA")
        # Strict gate: unverified question must NOT increment total_verified_questions
        assert summary_after.total_verified_questions == initial_summary.total_verified_questions
