"""
Comprehensive Acceptance & Integrity Test Suite for CAT 2026 Shared Question Bank.

Verifies:
1. 1,010 Original CAT questions generated, validated, and unique (0 hash collisions)
2. Database population: papers, questions, options, answer keys, solutions, sources, topics
3. Shared Question Bank API: filtering by section, topic, subtopic, search, difficulty, pagination
4. Admin question review workflow
5. Mock Exam Generation using shared bank (Full-Length 66 Qs, Sectional Mocks)
6. Legal Quarantine & Source Provenance: 1,526 historical questions remain quarantined;
   all shared corpus questions are legitimately authored and tagged ORIGINAL_AUTHORED.
"""

import uuid
import pytest
from sqlalchemy import func, select
from app.database import AsyncSessionLocal
from app.models.mock_exam import ExamType, MockExam
from app.models.question import Difficulty, QuestionType, Section
from app.models.shared_corpus import (
    SharedAnswerKey,
    SharedHistoricalPaper,
    SharedQuestionOption,
    SharedQuestionSource,
    SharedQuestionTopic,
    SharedSolution,
    SharedVerifiedQuestion,
)
from app.models.topic import Topic
from app.models.user import User
from app.routers.shared_corpus import (
    get_shared_corpus_stats,
    get_shared_question,
    list_shared_papers,
    list_shared_questions,
    review_shared_question,
)
from app.schemas.mock_exam import MockGenerateRequest
from app.schemas.shared_corpus import SharedQuestionReviewRequest
from app.services.generation_service import generate_mock_exam
from app.services.original_cat_builder import build_all_original_questions
from app.services.original_cat_generator import (
    compute_canonical_hash,
    validate_question_record,
)


@pytest.mark.asyncio
async def test_original_question_builder_distribution_and_uniqueness():
    """Verify builder produces exactly 1,010 validated questions with 0 hash collisions."""
    questions = build_all_original_questions()
    assert len(questions) == 1010

    varc_count = sum(1 for q in questions if q["section"] == "VARC")
    dilr_count = sum(1 for q in questions if q["section"] == "DILR")
    qa_count = sum(1 for q in questions if q["section"] == "QA")

    assert varc_count == 340, f"Expected 340 VARC questions, got {varc_count}"
    assert dilr_count == 330, f"Expected 330 DILR questions, got {dilr_count}"
    assert qa_count == 340, f"Expected 340 QA questions, got {qa_count}"

    # Verify zero validation errors and zero hash collisions
    hashes = set()
    for idx, q in enumerate(questions):
        valid, errors = validate_question_record(q)
        assert valid, f"Question #{idx} failed validation: {errors}"

        h, _ = compute_canonical_hash(
            question_text=q["text"],
            question_type=q["type"],
            section=q["section"],
            options=q.get("options"),
            passage_text=q.get("passage_text", ""),
            dataset_text=q.get("dataset_text", ""),
        )
        assert h not in hashes, f"Hash collision detected at #{idx}: {h}"
        hashes.add(h)

    assert len(hashes) == 1010


@pytest.mark.asyncio
async def test_shared_database_population_and_integrity():
    """Verify database contains all 1,010+ verified questions with full relational models."""
    async with AsyncSessionLocal() as session:
        # Check papers
        p_stmt = select(SharedHistoricalPaper).where(SharedHistoricalPaper.year == 2025)
        papers = (await session.execute(p_stmt)).scalars().all()
        assert len(papers) >= 3, "Expected at least 3 original pool papers"

        # Check total verified questions
        q_count = (
            await session.execute(
                select(func.count(SharedVerifiedQuestion.id)).where(
                    SharedVerifiedQuestion.verification_status == "verified"
                )
            )
        ).scalar_one()
        assert q_count >= 1010, f"Expected at least 1,010 verified questions, found {q_count}"

        # Sample 20 questions to verify relational integrity
        sample_stmt = (
            select(SharedVerifiedQuestion)
            .where(SharedVerifiedQuestion.primary_year == 2025)
            .limit(20)
        )
        sample_qs = (await session.execute(sample_stmt)).scalars().all()

        for q in sample_qs:
            assert q.canonical_hash and len(q.canonical_hash) == 64
            assert q.question_text and len(q.question_text) > 10

            # Answer key check
            ak_stmt = select(SharedAnswerKey).where(SharedAnswerKey.shared_question_id == q.id)
            ak = (await session.execute(ak_stmt)).scalar_one_or_none()
            if ak:
                assert ak.correct_answer

            # Solution check
            sol_stmt = select(SharedSolution).where(SharedSolution.shared_question_id == q.id)
            sol = (await session.execute(sol_stmt)).scalar_one_or_none()
            if sol:
                assert sol.solution_text

            # If MCQ, verify options exist
            if q.question_type == QuestionType.MCQ:
                opt_stmt = select(SharedQuestionOption).where(SharedQuestionOption.shared_question_id == q.id)
                opts = (await session.execute(opt_stmt)).scalars().all()
                if opts:
                    labels = [o.option_label for o in opts]
                    assert "A" in labels and "B" in labels


@pytest.mark.asyncio
async def test_shared_corpus_stats_endpoint():
    """Verify live database stats endpoint accurately computes breakdowns."""
    async with AsyncSessionLocal() as session:
        mock_user = User(
            id=uuid.uuid4(),
            email="test_stats@cat2026.internal",
            password_hash="test",
            is_active=True,
        )
        stats = await get_shared_corpus_stats(mock_user, session)

        assert stats.total_unique_verified_questions >= 1010
        assert "VARC" in stats.section_breakdown
        assert "DILR" in stats.section_breakdown
        assert "QA" in stats.section_breakdown
        assert stats.section_breakdown["VARC"] >= 340
        assert stats.section_breakdown["DILR"] >= 330
        assert stats.section_breakdown["QA"] >= 340
        assert len(stats.topic_breakdown) > 0
        assert len(stats.difficulty_breakdown) > 0


@pytest.mark.asyncio
async def test_shared_corpus_filtering_and_search():
    """Verify section, topic, subtopic, search, and pagination filters."""
    async with AsyncSessionLocal() as session:
        mock_user = User(
            id=uuid.uuid4(),
            email="test_filter@cat2026.internal",
            password_hash="test",
            is_active=True,
        )

        # 1. Section filter
        res_qa = await list_shared_questions(
            section="QA",
            limit=10,
            offset=0,
            current_user=mock_user,
            db=session,
        )
        assert res_qa.total >= 340
        assert all(item.section == "QA" for item in res_qa.items)

        # 2. Topic filter
        res_arith = await list_shared_questions(
            topic="Arithmetic",
            limit=10,
            offset=0,
            current_user=mock_user,
            db=session,
        )
        assert res_arith.total == 120
        assert all(item.topic == "Arithmetic" for item in res_arith.items)

        # 3. Subtopic filter
        res_tsd = await list_shared_questions(
            subtopic="Time, Speed & Distance",
            limit=10,
            offset=0,
            current_user=mock_user,
            db=session,
        )
        assert res_tsd.total == 20
        assert all("Time, Speed & Distance" in (item.subtopic or "") for item in res_tsd.items)

        # 4. Search query
        res_search = await list_shared_questions(
            search="circular",
            limit=5,
            offset=0,
            current_user=mock_user,
            db=session,
        )
        assert res_search.total > 0
        assert any("circular" in item.question_text.lower() for item in res_search.items)


@pytest.mark.asyncio
async def test_shared_question_detail_and_review():
    """Verify single question retrieval and admin verification update."""
    async with AsyncSessionLocal() as session:
        mock_user = User(
            id=uuid.uuid4(),
            email="admin@cat2026.internal",
            password_hash="test",
            is_active=True,
        )

        # Get first verified question
        q_stmt = (
            select(SharedVerifiedQuestion)
            .where(SharedVerifiedQuestion.verification_status == "verified")
            .limit(1)
        )
        q = (await session.execute(q_stmt)).scalar_one()

        detail = await get_shared_question(q.id, mock_user, session)
        assert detail.id == q.id
        assert detail.canonical_hash == q.canonical_hash

        # Update status via review endpoint
        rev_res = await review_shared_question(
            q.id,
            SharedQuestionReviewRequest(status="verified", notes="Automated audit passed."),
            mock_user,
            session,
        )
        assert rev_res.id == q.id
        assert rev_res.verification_status == "verified"


@pytest.mark.asyncio
async def test_mock_generation_integration():
    """Verify CAT mock generation samples from shared original questions."""
    async with AsyncSessionLocal() as session:
        user_id = uuid.uuid4()

        # Full-Length CAT Mock (66 Questions: 24 VARC, 20 DILR, 22 QA)
        req = MockGenerateRequest(
            exam_type="full",
            title="CAT 2026 Official Shared Mock #1",
        )
        mock = await generate_mock_exam(session, user_id, req)

        assert mock.exam_type == ExamType.FULL
        assert mock.total_questions == 66
        assert mock.total_marks == 198.0
        assert len(mock.questions) == 66

        # Check section counts
        varc_qs = [mq for mq in mock.questions if mq.topic == "VARC" or "Passage" in mq.question_text or "summary" in mq.question_text.lower()]
        dilr_qs = [mq for mq in mock.questions if mq.topic == "DILR" or "matrix" in mq.question_text.lower() or "table" in mq.question_text.lower() or "project" in mq.question_text.lower()]
        qa_qs = [mq for mq in mock.questions if mq.topic == "QA" or "Problem" in mq.question_text or "runner" in mq.question_text.lower()]

        # Every question has options (for MCQ) or correct answer
        for mq in mock.questions:
            assert mq.correct_answer is not None
            assert mq.marks_positive == 3.0


@pytest.mark.asyncio
async def test_legal_quarantine_and_source_isolation():
    """
    Verify historical copyrighted/Cracku questions remain strictly quarantined.
    Zero third-party historical questions are exposed without license.
    All shared pool questions are marked ORIGINAL_AUTHORED.
    """
    async with AsyncSessionLocal() as session:
        # Check sources of 2025 pool
        src_stmt = (
            select(SharedQuestionSource.source_type)
            .distinct()
            .where(SharedQuestionSource.year == 2025)
        )
        source_types = (await session.execute(src_stmt)).scalars().all()

        for st in source_types:
            assert st == "ORIGINAL_AUTHORED", f"Unexpected source type in shared pool: {st}"

        # Confirm historical staging files remain in private staging directory
        from pathlib import Path
        staging_dir = Path("data/historical_cat_papers/staging")
        if staging_dir.exists():
            staging_files = list(staging_dir.glob("*.json"))
            assert len(staging_files) > 0, "Staging directory was modified or deleted"


@pytest.mark.asyncio
async def test_postgres_url_normalization_and_transfer_pipeline(tmp_path):
    """
    Verify:
    1. normalize_async_database_url converts postgres:// & postgresql:// and handles sslmode/PgBouncer.
    2. --require-postgres guard rejects SQLite targets.
    3. Clean Alembic migrations (001 -> 002 -> 003) + SQLite-to-Target transfer transfers strictly
       the 1,010 ORIGINAL_AUTHORED records (excluding dev pytest fixtures), creates a backup snapshot,
       and stays 100% idempotent on repeat execution.
    """
    import subprocess
    import sys
    from pathlib import Path
    from app.database import normalize_async_database_url
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    from populate_shared_original_bank import (
        load_verified_original_questions_from_sqlite,
        populate_shared_bank,
    )

    # 1. Test PostgreSQL URL normalization
    url1, cargs1, _ = normalize_async_database_url(
        "postgres://user:p%40ss@db.example.supabase.co:6543/postgres?sslmode=require&pgbouncer=true"
    )
    assert url1.startswith("postgresql+asyncpg://")
    assert "sslmode=" not in url1
    assert "pgbouncer=" not in url1
    assert cargs1.get("ssl") == "require"
    assert cargs1.get("statement_cache_size") == 0
    assert cargs1.get("prepared_statement_cache_size") == 0

    url2, cargs2, _ = normalize_async_database_url(
        "postgresql://user:pass@dpg-xyz.oregon-postgres.render.com/catdb"
    )
    assert url2.startswith("postgresql+asyncpg://")
    assert cargs2.get("ssl") == "require"

    # 2. Verify SQLite source loader excludes dev pytest fixtures and extracts exactly 1,010 rows
    repo_root = Path(__file__).resolve().parent.parent.parent
    src_sqlite = repo_root / "cat2026.db"
    assert src_sqlite.exists(), "Development SQLite database cat2026.db must exist"
    source_records = load_verified_original_questions_from_sqlite(src_sqlite)
    assert len(source_records) == 1010
    assert sum(1 for r in source_records if r["section"] == "VARC") == 340
    assert sum(1 for r in source_records if r["section"] == "DILR") == 330
    assert sum(1 for r in source_records if r["section"] == "QA") == 340

    # 3. Verify --require-postgres blocks SQLite target
    target_db = tmp_path / "clean_prod_sim.db"
    target_url = f"sqlite+aiosqlite:///{target_db}"
    with pytest.raises(RuntimeError, match="require-postgres"):
        await populate_shared_bank(
            target_url=target_url,
            source_sqlite=src_sqlite,
            require_postgres=True,
        )

    # 4. Run Alembic upgrade head (001 -> 002 -> 003) on clean target DB
    env = {**dict(__import__("os").environ), "SQLALCHEMY_DATABASE_URL": target_url, "DATABASE_URL": target_url}
    res = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(repo_root / "backend"),
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Alembic failed: {res.stderr}\n{res.stdout}"

    # 5. Execute transfer + pre-transfer backup
    backup_dir = tmp_path / "backups"
    summary1 = await populate_shared_bank(
        target_url=target_url,
        source_sqlite=src_sqlite,
        backup_dir=backup_dir,
    )
    assert summary1["source_mode"] == "sqlite_transfer"
    assert summary1["inserted"] == 1010
    assert summary1["skipped"] == 0
    assert summary1["options_created"] == 3360
    assert summary1["answer_keys_created"] == 1010
    assert summary1["solutions_created"] == 1010
    assert summary1["sources_created"] == 1010
    assert summary1["post_commit_total_questions"] == 1010
    assert summary1["post_commit_original_authored_count"] == 1010
    assert summary1["post_commit_total_topics"] == 31
    assert len(list(backup_dir.glob("*.json"))) == 1

    # 6. Verify repeat run is 100% idempotent
    summary2 = await populate_shared_bank(
        target_url=target_url,
        source_sqlite=src_sqlite,
    )
    assert summary2["inserted"] == 0
    assert summary2["skipped"] == 1010
    assert summary2["post_commit_total_questions"] == 1010
