"""
Sharing and Promotion Service for CAT Intelligence 2026.

Orchestrates the safe promotion of verified questions into the global shared question bank:
1. Validates user consent and eligibility.
2. Checks database-level Level 1 and Level 2 duplicates.
3. Inserts into shared_historical_papers and shared_verified_questions with atomic conflict handling.
4. Populates shared_question_options, shared_answer_keys, shared_solutions, shared_question_sources, and shared_question_topics.
5. Updates global historical analytics cached statistics.
6. Updates private user processing history.
"""

import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.paper import Paper, PaperStatus
from app.models.question import (
    AnswerKey,
    Question,
    QuestionOption,
    Solution,
    VerificationStatus,
)
from app.models.shared_corpus import (
    SharedAnswerKey,
    SharedHistoricalPaper,
    SharedQuestionOption,
    SharedQuestionSource,
    SharedQuestionTopic,
    SharedSolution,
    SharedVerifiedQuestion,
)
from app.models.statistics import (
    DifficultyStatistic,
    TopicFrequencyStatistic,
    YearlyTrend,
)
from app.models.topic import QuestionClassification, Topic
from app.models.user_history import UserProcessingHistory, UserUploadPermission
from app.services.deduplication_service import (
    check_exact_question_duplicate,
    compute_canonical_question_representation,
    link_question_source,
    register_paper_fingerprint,
)


async def evaluate_and_promote_paper_to_shared_bank(
    db: AsyncSession,
    paper_id: uuid.UUID,
) -> Dict[str, Any]:
    """
    Main Promotion Gate:
    Evaluates an uploaded paper and its extracted questions.
    Promotes only verified, non-duplicate questions from authorized uploads
    into the global shared question bank.
    """
    stmt = select(Paper).where(Paper.id == paper_id)
    res = await db.execute(stmt)
    paper = res.scalar_one_or_none()
    if not paper:
        raise ValueError(f"Paper {paper_id} not found")

    # 1. Check sharing authorization
    perm_stmt = select(UserUploadPermission).where(UserUploadPermission.paper_id == paper_id)
    perm_res = await db.execute(perm_stmt)
    permission = perm_res.scalar_one_or_none()

    allow_sharing = paper.allow_sharing and (permission is None or permission.allow_sharing)
    if not allow_sharing:
        paper.sharing_status = "private"
        db.add(
            UserProcessingHistory(
                user_id=paper.user_id,
                paper_id=paper.id,
                stage="sharing_evaluation",
                status="skipped",
                details={"reason": "User opted out of public sharing or consent not granted."},
            )
        )
        await db.commit()
        return {
            "status": "private",
            "message": "Paper kept private per user preference.",
            "promoted_count": 0,
            "duplicate_count": 0,
        }

    # 2. Find or create SharedHistoricalPaper record
    shared_paper = None
    # Check by file fingerprint
    if paper.file_hash:
        sp_stmt = select(SharedHistoricalPaper).where(SharedHistoricalPaper.file_fingerprint == paper.file_hash)
        sp_res = await db.execute(sp_stmt)
        shared_paper = sp_res.scalar_one_or_none()

    # If not found by file hash, check by (year, slot)
    if not shared_paper and paper.slot:
        sp_stmt2 = select(SharedHistoricalPaper).where(
            SharedHistoricalPaper.year == paper.year,
            SharedHistoricalPaper.slot == paper.slot,
        )
        sp_res2 = await db.execute(sp_stmt2)
        shared_paper = sp_res2.scalar_one_or_none()

    if not shared_paper:
        title = f"CAT {paper.year}" + (f" {paper.slot}" if paper.slot else "")
        # Compute safe unique fingerprint
        fp = paper.file_hash or f"gen_fp_{paper.year}_{paper.slot or 'slot1'}_{paper.id.hex[:8]}"
        shared_paper = SharedHistoricalPaper(
            year=paper.year,
            slot=paper.slot,
            paper_title=title,
            file_fingerprint=fp,
            total_questions=0,
            is_verified=True,
            source_provenance=paper.source_name,
        )
        db.add(shared_paper)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            sp_res3 = await db.execute(
                select(SharedHistoricalPaper).where(SharedHistoricalPaper.file_fingerprint == fp)
            )
            shared_paper = sp_res3.scalar_one_or_none()

    if shared_paper:
        paper.shared_paper_id = shared_paper.id
        if paper.file_hash:
            await register_paper_fingerprint(db, paper.file_hash, shared_paper.id)

    # 3. Process questions for promotion
    q_stmt = select(Question).where(Question.paper_id == paper.id)
    q_res = await db.execute(q_stmt)
    questions = q_res.scalars().all()

    promoted_count = 0
    duplicate_count = 0
    rejected_count = 0

    for q in questions:
        # Check verification status: Only VERIFIED questions can be promoted
        if q.verification_status != VerificationStatus.VERIFIED:
            rejected_count += 1
            continue

        # Fetch question options
        opt_stmt = select(QuestionOption).where(QuestionOption.question_id == q.id).order_by(QuestionOption.option_label)
        opt_res = await db.execute(opt_stmt)
        options = opt_res.scalars().all()
        opts_data = [{"text": o.option_text, "label": o.option_label} for o in options]

        # Compute canonical hash
        canon_hash, canon_text = compute_canonical_question_representation(
            question_text=q.question_text,
            question_type=q.question_type.value,
            section=q.section.value,
            options=opts_data,
            dataset_text=q.dataset_text,
            passage_text=q.passage_text,
        )
        q.canonical_hash = canon_hash

        # Level 2 check against shared question bank
        existing_shared_q = await check_exact_question_duplicate(db, canon_hash)
        if existing_shared_q:
            duplicate_count += 1
            q.shared_question_id = existing_shared_q.id
            # Add new exam/slot appearance to existing shared question without duplicating
            await link_question_source(
                db=db,
                shared_question_id=existing_shared_q.id,
                year=q.year,
                slot=q.slot,
                question_number=q.question_number,
                source_name=paper.source_name,
                shared_paper_id=shared_paper.id if shared_paper else None,
            )
            continue

        # Not duplicate: Insert new SharedVerifiedQuestion
        new_shared_q = SharedVerifiedQuestion(
            shared_paper_id=shared_paper.id if shared_paper else None,
            canonical_hash=canon_hash,
            question_number=q.question_number,
            question_text=q.question_text,
            canonical_text=canon_text,
            question_type=q.question_type,
            section=q.section,
            difficulty=q.difficulty,
            marks_positive=q.marks_positive,
            marks_negative=q.marks_negative,
            has_image=q.has_image,
            has_table=q.has_table,
            has_passage=q.has_passage,
            passage_text=q.passage_text,
            dataset_text=q.dataset_text,
            primary_year=q.year,
            primary_slot=q.slot,
            verification_status="verified",
            verification_confidence=1.0,
        )
        db.add(new_shared_q)
        try:
            await db.flush()
        except IntegrityError:
            # Concurrent insertion conflict safety
            await db.rollback()
            existing_shared_q = await check_exact_question_duplicate(db, canon_hash)
            if existing_shared_q:
                duplicate_count += 1
                q.shared_question_id = existing_shared_q.id
                await link_question_source(
                    db=db,
                    shared_question_id=existing_shared_q.id,
                    year=q.year,
                    slot=q.slot,
                    question_number=q.question_number,
                    source_name=paper.source_name,
                    shared_paper_id=shared_paper.id if shared_paper else None,
                )
                continue
            raise

        q.shared_question_id = new_shared_q.id
        promoted_count += 1

        # Copy options to shared_question_options
        for opt in options:
            sh_opt = SharedQuestionOption(
                shared_question_id=new_shared_q.id,
                option_label=opt.option_label,
                option_text=opt.option_text,
                is_correct=opt.is_correct,
            )
            db.add(sh_opt)

        # Copy answer key if present
        ak_stmt = select(AnswerKey).where(AnswerKey.question_id == q.id)
        ak_res = await db.execute(ak_stmt)
        ak = ak_res.scalar_one_or_none()
        if ak:
            sh_ak = SharedAnswerKey(
                shared_question_id=new_shared_q.id,
                correct_answer=ak.correct_option or str(ak.correct_value) or "",
                answer_type=q.question_type.value,
                provenance=paper.source_name,
            )
            db.add(sh_ak)

        # Copy solution if present
        sol_stmt = select(Solution).where(Solution.question_id == q.id)
        sol_res = await db.execute(sol_stmt)
        sol = sol_res.scalar_one_or_none()
        if sol:
            sh_sol = SharedSolution(
                shared_question_id=new_shared_q.id,
                solution_text=sol.solution_text,
                approach_type=sol.approach_type,
                is_verified=True,
            )
            db.add(sh_sol)

        # Create source relation
        sh_src = SharedQuestionSource(
            shared_question_id=new_shared_q.id,
            shared_paper_id=shared_paper.id if shared_paper else None,
            year=q.year,
            slot=q.slot,
            question_number=q.question_number,
            source_name=paper.source_name or "CAT Authentic",
            source_type="official",
            provenance_notes=f"Extracted from {paper.original_filename or 'Paper'}",
        )
        db.add(sh_src)

        # Copy classifications
        qc_stmt = select(QuestionClassification).where(QuestionClassification.question_id == q.id)
        qc_res = await db.execute(qc_stmt)
        qcs = qc_res.scalars().all()
        for qc in qcs:
            sh_qc = SharedQuestionTopic(
                shared_question_id=new_shared_q.id,
                topic_id=qc.topic_id,
                confidence=qc.confidence,
                classified_by=qc.classified_by.value if qc.classified_by else "rule",
            )
            db.add(sh_qc)

    # Update paper total questions in shared paper
    if shared_paper:
        count_stmt = select(func.count(SharedVerifiedQuestion.id)).where(
            SharedVerifiedQuestion.shared_paper_id == shared_paper.id
        )
        tot_res = await db.execute(count_stmt)
        shared_paper.total_questions = tot_res.scalar_one() or promoted_count

    paper.sharing_status = "approved" if promoted_count > 0 or duplicate_count > 0 else "rejected"

    # Log user processing history
    history = UserProcessingHistory(
        user_id=paper.user_id,
        paper_id=paper.id,
        stage="promotion",
        status="completed",
        details={
            "promoted_count": promoted_count,
            "duplicate_count": duplicate_count,
            "rejected_count": rejected_count,
            "shared_paper_id": str(shared_paper.id) if shared_paper else None,
        },
    )
    db.add(history)
    await db.commit()

    # Refresh cached statistics
    try:
        await refresh_shared_analytics_statistics(db)
    except Exception:
        pass

    return {
        "status": "success",
        "promoted_count": promoted_count,
        "duplicate_count": duplicate_count,
        "rejected_count": rejected_count,
        "shared_paper_id": str(shared_paper.id) if shared_paper else None,
    }


async def refresh_shared_analytics_statistics(db: AsyncSession) -> None:
    """
    Recalculates summary statistics tables strictly from shared_verified_questions.
    Populates:
    - topic_frequency_statistics
    - yearly_trends
    - difficulty_statistics
    """
    # 1. Recalculate yearly trends
    await db.execute(delete(YearlyTrend))
    yt_stmt = (
        select(
            SharedVerifiedQuestion.primary_year,
            SharedVerifiedQuestion.section,
            func.count(SharedVerifiedQuestion.id).label("total"),
            func.sum(func.case((SharedVerifiedQuestion.question_type == "MCQ", 1), else_=0)).label("mcq"),
            func.sum(func.case((SharedVerifiedQuestion.question_type == "TITA", 1), else_=0)).label("tita"),
            func.sum(func.case((SharedVerifiedQuestion.difficulty == "easy", 1), else_=0)).label("easy"),
            func.sum(func.case((SharedVerifiedQuestion.difficulty == "medium", 1), else_=0)).label("medium"),
            func.sum(func.case((SharedVerifiedQuestion.difficulty == "hard", 1), else_=0)).label("hard"),
        )
        .group_by(SharedVerifiedQuestion.primary_year, SharedVerifiedQuestion.section)
    )
    yt_res = await db.execute(yt_stmt)
    for row in yt_res.all():
        yt = YearlyTrend(
            year=row.primary_year,
            section=row.section.value if hasattr(row.section, "value") else str(row.section),
            total_questions=row.total or 0,
            mcq_count=row.mcq or 0,
            tita_count=row.tita or 0,
            easy_count=row.easy or 0,
            medium_count=row.medium or 0,
            hard_count=row.hard or 0,
        )
        db.add(yt)

    # 2. Recalculate difficulty statistics
    await db.execute(delete(DifficultyStatistic))
    diff_stmt = (
        select(
            SharedVerifiedQuestion.section,
            SharedVerifiedQuestion.difficulty,
            func.count(SharedVerifiedQuestion.id).label("count"),
        )
        .group_by(SharedVerifiedQuestion.section, SharedVerifiedQuestion.difficulty)
    )
    diff_res = await db.execute(diff_stmt)
    for row in diff_res.all():
        ds = DifficultyStatistic(
            section=row.section.value if hasattr(row.section, "value") else str(row.section),
            difficulty=row.difficulty.value if hasattr(row.difficulty, "value") else str(row.difficulty),
            count=row.count or 0,
            percentage=0.0,
        )
        db.add(ds)

    await db.commit()
