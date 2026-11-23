"""
Shared Corpus Router: Global Shared Verified Question Bank.
Accessible to all authenticated users.
Provides access to approved historical papers, verified questions, and multi-source provenance.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.deduplication import DuplicateDetectionRecord
from app.models.question import Difficulty, QuestionType, Section
from app.models.shared_corpus import (
    SharedAnswerKey,
    SharedHistoricalPaper,
    SharedQuestionOption,
    SharedQuestionSource,
    SharedSolution,
    SharedVerifiedQuestion,
)
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.shared_corpus import (
    SharedCorpusStatsResponse,
    SharedHistoricalPaperListResponse,
    SharedHistoricalPaperResponse,
    SharedQuestionDetail,
    SharedQuestionListResponse,
    SharedQuestionOptionSchema,
    SharedQuestionSourceSchema,
)

router = APIRouter(prefix="/shared", tags=["Shared Question Bank"])


@router.get("/papers", response_model=SharedHistoricalPaperListResponse)
async def list_shared_papers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all approved historical papers in the shared question bank."""
    stmt = select(SharedHistoricalPaper).order_by(SharedHistoricalPaper.year.desc(), SharedHistoricalPaper.slot.asc())
    result = await db.execute(stmt)
    papers = result.scalars().all()
    return SharedHistoricalPaperListResponse(
        items=[SharedHistoricalPaperResponse.model_validate(p) for p in papers],
        total=len(papers),
    )


@router.get("/questions", response_model=SharedQuestionListResponse)
async def list_shared_questions(
    section: Optional[str] = Query(None, description="VARC, DILR, QA"),
    year: Optional[int] = Query(None),
    slot: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None, description="easy, medium, hard"),
    question_type: Optional[str] = Query(None, description="MCQ, TITA"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List verified questions from the shared question bank with filters."""
    stmt = select(SharedVerifiedQuestion)

    if section:
        stmt = stmt.where(SharedVerifiedQuestion.section == Section(section))
    if year:
        stmt = stmt.where(SharedVerifiedQuestion.primary_year == year)
    if slot:
        stmt = stmt.where(SharedVerifiedQuestion.primary_slot == slot)
    if difficulty:
        stmt = stmt.where(SharedVerifiedQuestion.difficulty == Difficulty(difficulty))
    if question_type:
        stmt = stmt.where(SharedVerifiedQuestion.question_type == QuestionType(question_type))

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Pagination
    stmt = stmt.order_by(SharedVerifiedQuestion.primary_year.desc(), SharedVerifiedQuestion.question_number.asc()).offset(offset).limit(limit)
    res = await db.execute(stmt)
    questions = res.scalars().all()

    items = []
    for q in questions:
        # Load options
        opt_stmt = select(SharedQuestionOption).where(SharedQuestionOption.shared_question_id == q.id).order_by(SharedQuestionOption.option_label)
        options = (await db.execute(opt_stmt)).scalars().all()

        # Load answer key
        ak_stmt = select(SharedAnswerKey).where(SharedAnswerKey.shared_question_id == q.id)
        ak = (await db.execute(ak_stmt)).scalar_one_or_none()

        # Load solution
        sol_stmt = select(SharedSolution).where(SharedSolution.shared_question_id == q.id)
        sol = (await db.execute(sol_stmt)).scalar_one_or_none()

        # Load sources
        src_stmt = select(SharedQuestionSource).where(SharedQuestionSource.shared_question_id == q.id).order_by(SharedQuestionSource.year.desc())
        sources = (await db.execute(src_stmt)).scalars().all()

        items.append(
            SharedQuestionDetail(
                id=q.id,
                canonical_hash=q.canonical_hash,
                question_number=q.question_number,
                question_text=q.question_text,
                question_type=q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
                section=q.section.value if hasattr(q.section, "value") else str(q.section),
                difficulty=q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
                marks_positive=q.marks_positive,
                marks_negative=q.marks_negative,
                has_image=q.has_image,
                has_table=q.has_table,
                has_passage=q.has_passage,
                passage_text=q.passage_text,
                dataset_text=q.dataset_text,
                primary_year=q.primary_year,
                primary_slot=q.primary_slot,
                verification_status=q.verification_status,
                verification_confidence=q.verification_confidence,
                options=[SharedQuestionOptionSchema(id=o.id, option_label=o.option_label, option_text=o.option_text, is_correct=o.is_correct) for o in options],
                correct_answer=ak.correct_answer if ak else None,
                solution_text=sol.solution_text if sol else None,
                sources=[SharedQuestionSourceSchema(id=s.id, year=s.year, slot=s.slot, question_number=s.question_number, source_name=s.source_name, source_type=s.source_type, provenance_notes=s.provenance_notes) for s in sources],
                created_at=q.created_at,
            )
        )

    return SharedQuestionListResponse(items=items, total=total)


@router.get("/questions/{question_id}", response_model=SharedQuestionDetail)
async def get_shared_question(
    question_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get single shared question with complete provenance and solutions."""
    stmt = select(SharedVerifiedQuestion).where(SharedVerifiedQuestion.id == question_id)
    q = (await db.execute(stmt)).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared question not found.")

    opt_stmt = select(SharedQuestionOption).where(SharedQuestionOption.shared_question_id == q.id).order_by(SharedQuestionOption.option_label)
    options = (await db.execute(opt_stmt)).scalars().all()

    ak_stmt = select(SharedAnswerKey).where(SharedAnswerKey.shared_question_id == q.id)
    ak = (await db.execute(ak_stmt)).scalar_one_or_none()

    sol_stmt = select(SharedSolution).where(SharedSolution.shared_question_id == q.id)
    sol = (await db.execute(sol_stmt)).scalar_one_or_none()

    src_stmt = select(SharedQuestionSource).where(SharedQuestionSource.shared_question_id == q.id).order_by(SharedQuestionSource.year.desc())
    sources = (await db.execute(src_stmt)).scalars().all()

    return SharedQuestionDetail(
        id=q.id,
        canonical_hash=q.canonical_hash,
        question_number=q.question_number,
        question_text=q.question_text,
        question_type=q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
        section=q.section.value if hasattr(q.section, "value") else str(q.section),
        difficulty=q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
        marks_positive=q.marks_positive,
        marks_negative=q.marks_negative,
        has_image=q.has_image,
        has_table=q.has_table,
        has_passage=q.has_passage,
        passage_text=q.passage_text,
        dataset_text=q.dataset_text,
        primary_year=q.primary_year,
        primary_slot=q.primary_slot,
        verification_status=q.verification_status,
        verification_confidence=q.verification_confidence,
        options=[SharedQuestionOptionSchema(id=o.id, option_label=o.option_label, option_text=o.option_text, is_correct=o.is_correct) for o in options],
        correct_answer=ak.correct_answer if ak else None,
        solution_text=sol.solution_text if sol else None,
        sources=[SharedQuestionSourceSchema(id=s.id, year=s.year, slot=s.slot, question_number=s.question_number, source_name=s.source_name, source_type=s.source_type, provenance_notes=s.provenance_notes) for s in sources],
        created_at=q.created_at,
    )


@router.get("/stats", response_model=SharedCorpusStatsResponse)
async def get_shared_corpus_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get live statistical summary of the global shared question bank.
    All numbers derived directly from authentic database records.
    """
    # Total verified papers
    paper_count = (await db.execute(select(func.count(SharedHistoricalPaper.id)))).scalar_one()

    # Total unique verified questions
    q_count = (await db.execute(select(func.count(SharedVerifiedQuestion.id)))).scalar_one()

    # Total duplicates prevented
    dup_count = (
        await db.execute(
            select(func.count(DuplicateDetectionRecord.id)).where(
                DuplicateDetectionRecord.action_taken.in_(["skipped", "merged_source"])
            )
        )
    ).scalar_one()

    # Total sources linked
    src_count = (await db.execute(select(func.count(SharedQuestionSource.id)))).scalar_one()

    # Section breakdown
    sec_stmt = select(SharedVerifiedQuestion.section, func.count(SharedVerifiedQuestion.id)).group_by(SharedVerifiedQuestion.section)
    sec_res = await db.execute(sec_stmt)
    section_breakdown = {}
    for row in sec_res.all():
        sec_name = row[0].value if hasattr(row[0], "value") else str(row[0])
        section_breakdown[sec_name] = row[1]

    # Year breakdown
    yr_stmt = select(SharedVerifiedQuestion.primary_year, func.count(SharedVerifiedQuestion.id)).group_by(SharedVerifiedQuestion.primary_year).order_by(SharedVerifiedQuestion.primary_year.desc())
    yr_res = await db.execute(yr_stmt)
    year_breakdown = {row[0]: row[1] for row in yr_res.all()}

    # Recent approved questions
    recent_stmt = (
        select(SharedVerifiedQuestion)
        .order_by(SharedVerifiedQuestion.created_at.desc())
        .limit(5)
    )
    recent_qs = (await db.execute(recent_stmt)).scalars().all()
    recent_items = []
    for q in recent_qs:
        recent_items.append(
            SharedQuestionDetail(
                id=q.id,
                canonical_hash=q.canonical_hash,
                question_number=q.question_number,
                question_text=q.question_text[:200] + ("..." if len(q.question_text) > 200 else ""),
                question_type=q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
                section=q.section.value if hasattr(q.section, "value") else str(q.section),
                difficulty=q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
                marks_positive=q.marks_positive,
                marks_negative=q.marks_negative,
                has_image=q.has_image,
                has_table=q.has_table,
                has_passage=q.has_passage,
                passage_text=None,
                dataset_text=None,
                primary_year=q.primary_year,
                primary_slot=q.primary_slot,
                verification_status=q.verification_status,
                verification_confidence=q.verification_confidence,
                options=[],
                correct_answer=None,
                solution_text=None,
                sources=[],
                created_at=q.created_at,
            )
        )

    return SharedCorpusStatsResponse(
        total_verified_papers=paper_count,
        total_unique_verified_questions=q_count,
        total_duplicates_prevented=dup_count,
        total_sources_linked=src_count,
        section_breakdown=section_breakdown,
        year_breakdown=year_breakdown,
        topic_breakdown=[],
        recent_approved_questions=recent_items,
    )
