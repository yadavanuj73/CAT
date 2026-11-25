"""
Shared Corpus Router: Global Shared Verified Question Bank.
Accessible to all authenticated users.
Provides access to approved papers, verified questions, multi-source provenance,
topic/subtopic filtering, full-text search, pagination, and review workflows.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.deduplication import DuplicateDetectionRecord
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
from app.routers.deps import get_current_user
from app.schemas.shared_corpus import (
    SharedCorpusStatsResponse,
    SharedHistoricalPaperListResponse,
    SharedHistoricalPaperResponse,
    SharedQuestionDetail,
    SharedQuestionListResponse,
    SharedQuestionOptionSchema,
    SharedQuestionReviewRequest,
    SharedQuestionReviewResponse,
    SharedQuestionSourceSchema,
)

router = APIRouter(prefix="/shared", tags=["Shared Question Bank"])


def _serialize_shared_question(q: SharedVerifiedQuestion) -> SharedQuestionDetail:
    """Serialize an eagerly-loaded SharedVerifiedQuestion without extra DB roundtrips."""
    options = sorted(q.options or [], key=lambda o: o.option_label)
    ak = q.answer_key
    sol = q.solution
    sources = sorted(q.sources or [], key=lambda s: s.year, reverse=True)

    top_obj = None
    if q.topics:
        for st in q.topics:
            if st.topic:
                top_obj = st.topic
                break

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
        topic=top_obj.topic_name if top_obj else None,
        subtopic=top_obj.subtopic_name if top_obj else None,
        options=[
            SharedQuestionOptionSchema(
                id=o.id,
                option_label=o.option_label,
                option_text=o.option_text,
                is_correct=o.is_correct,
            )
            for o in options
        ],
        correct_answer=ak.correct_answer if ak else None,
        solution_text=sol.solution_text if sol else None,
        sources=[
            SharedQuestionSourceSchema(
                id=s.id,
                year=s.year,
                slot=s.slot,
                question_number=s.question_number,
                source_name=s.source_name,
                source_type=s.source_type,
                provenance_notes=s.provenance_notes,
            )
            for s in sources
        ],
        created_at=q.created_at,
    )


@router.get("/papers", response_model=SharedHistoricalPaperListResponse)
async def list_shared_papers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all approved papers in the shared question bank."""
    stmt = (
        select(SharedHistoricalPaper)
        .where(SharedHistoricalPaper.is_verified.is_(True))
        .order_by(
            SharedHistoricalPaper.year.desc(),
            SharedHistoricalPaper.slot.asc(),
        )
    )
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
    topic: Optional[str] = Query(None, description="Filter by topic name"),
    subtopic: Optional[str] = Query(None, description="Filter by subtopic name"),
    search: Optional[str] = Query(None, description="Keyword search across question text"),
    source_type: Optional[str] = Query(None, description="ORIGINAL_AUTHORED, official, etc."),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List verified questions from the shared question bank with advanced filters and pagination."""
    if not isinstance(limit, int):
        limit = 50
    if not isinstance(offset, int):
        offset = 0

    filters = [SharedVerifiedQuestion.verification_status == "verified"]

    if section and isinstance(section, str):
        filters.append(SharedVerifiedQuestion.section == Section(section))
    if year and isinstance(year, int):
        filters.append(SharedVerifiedQuestion.primary_year == year)
    if slot and isinstance(slot, str):
        filters.append(SharedVerifiedQuestion.primary_slot == slot)
    if difficulty and isinstance(difficulty, str):
        filters.append(SharedVerifiedQuestion.difficulty == Difficulty(difficulty))
    if question_type and isinstance(question_type, str):
        filters.append(SharedVerifiedQuestion.question_type == QuestionType(question_type))

    if search and isinstance(search, str) and search.strip():
        search_term = f"%{search.strip()}%"
        filters.append(
            or_(
                SharedVerifiedQuestion.question_text.ilike(search_term),
                SharedVerifiedQuestion.passage_text.ilike(search_term),
                SharedVerifiedQuestion.dataset_text.ilike(search_term),
            )
        )

    if (topic and isinstance(topic, str) and topic.strip()) or (
        subtopic and isinstance(subtopic, str) and subtopic.strip()
    ):
        topic_conds = []
        if topic and isinstance(topic, str) and topic.strip():
            topic_conds.append(Topic.topic_name.ilike(f"%{topic.strip()}%"))
        if subtopic and isinstance(subtopic, str) and subtopic.strip():
            topic_conds.append(Topic.subtopic_name.ilike(f"%{subtopic.strip()}%"))

        filters.append(
            SharedVerifiedQuestion.topics.any(
                SharedQuestionTopic.topic.has(*topic_conds)
            )
        )

    if source_type and isinstance(source_type, str) and source_type.strip():
        filters.append(
            SharedVerifiedQuestion.sources.any(
                SharedQuestionSource.source_type == source_type.strip()
            )
        )

    # Count total matching verified questions cleanly without redundant wide joins
    count_stmt = select(func.count(SharedVerifiedQuestion.id)).where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    # Deterministic pagination with selectin eager loading (eliminates N+1 DB roundtrips)
    stmt = (
        select(SharedVerifiedQuestion)
        .options(
            selectinload(SharedVerifiedQuestion.options),
            selectinload(SharedVerifiedQuestion.answer_key),
            selectinload(SharedVerifiedQuestion.solution),
            selectinload(SharedVerifiedQuestion.sources),
            selectinload(SharedVerifiedQuestion.topics).selectinload(SharedQuestionTopic.topic),
        )
        .where(*filters)
        .order_by(
            SharedVerifiedQuestion.primary_year.desc(),
            SharedVerifiedQuestion.section.asc(),
            SharedVerifiedQuestion.question_number.asc(),
            SharedVerifiedQuestion.id.asc(),
        )
        .offset(offset)
        .limit(limit)
    )
    res = await db.execute(stmt)
    questions = res.scalars().all()

    return SharedQuestionListResponse(
        items=[_serialize_shared_question(q) for q in questions],
        total=total,
    )


@router.get("/questions/{question_id}", response_model=SharedQuestionDetail)
async def get_shared_question(
    question_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get single shared question with complete provenance, options, solution, and topic."""
    stmt = (
        select(SharedVerifiedQuestion)
        .options(
            selectinload(SharedVerifiedQuestion.options),
            selectinload(SharedVerifiedQuestion.answer_key),
            selectinload(SharedVerifiedQuestion.solution),
            selectinload(SharedVerifiedQuestion.sources),
            selectinload(SharedVerifiedQuestion.topics).selectinload(SharedQuestionTopic.topic),
        )
        .where(
            SharedVerifiedQuestion.id == question_id,
            SharedVerifiedQuestion.verification_status == "verified",
        )
    )
    q = (await db.execute(stmt)).scalar_one_or_none()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared question not found.",
        )

    return _serialize_shared_question(q)


@router.post("/questions/{question_id}/review", response_model=SharedQuestionReviewResponse)
async def review_shared_question(
    question_id: uuid.UUID,
    review_req: SharedQuestionReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Review / verify a shared question.
    Updates verification status.
    """
    stmt = select(SharedVerifiedQuestion).where(SharedVerifiedQuestion.id == question_id)
    q = (await db.execute(stmt)).scalar_one_or_none()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared question not found.",
        )

    valid_statuses = ["verified", "needs_review", "rejected"]
    if review_req.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}",
        )

    q.verification_status = review_req.status
    await db.commit()
    await db.refresh(q)

    return SharedQuestionReviewResponse(
        id=q.id,
        verification_status=q.verification_status,
        message=f"Shared question status updated to '{q.verification_status}'.",
    )


@router.get("/stats", response_model=SharedCorpusStatsResponse)
async def get_shared_corpus_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get live statistical summary of the global shared question bank.
    All numbers derived directly from verified database records.
    """
    verified_filter = SharedVerifiedQuestion.verification_status == "verified"

    # Total verified papers
    paper_count = (
        await db.execute(
            select(func.count(SharedHistoricalPaper.id)).where(
                SharedHistoricalPaper.is_verified.is_(True)
            )
        )
    ).scalar_one()

    # Total unique verified questions
    q_count = (
        await db.execute(
            select(func.count(SharedVerifiedQuestion.id)).where(verified_filter)
        )
    ).scalar_one()

    # Total duplicates prevented
    dup_count = (
        await db.execute(
            select(func.count(DuplicateDetectionRecord.id)).where(
                DuplicateDetectionRecord.action_taken.in_(["skipped", "merged_source"])
            )
        )
    ).scalar_one()

    # Total sources linked
    src_count = (
        await db.execute(
            select(func.count(SharedQuestionSource.id))
            .join(
                SharedVerifiedQuestion,
                SharedQuestionSource.shared_question_id == SharedVerifiedQuestion.id,
            )
            .where(verified_filter)
        )
    ).scalar_one()

    # Section breakdown
    sec_stmt = (
        select(SharedVerifiedQuestion.section, func.count(SharedVerifiedQuestion.id))
        .where(verified_filter)
        .group_by(SharedVerifiedQuestion.section)
    )
    sec_res = await db.execute(sec_stmt)
    section_breakdown = {}
    for row in sec_res.all():
        sec_name = row[0].value if hasattr(row[0], "value") else str(row[0])
        section_breakdown[sec_name] = row[1]

    # Year breakdown
    yr_stmt = (
        select(SharedVerifiedQuestion.primary_year, func.count(SharedVerifiedQuestion.id))
        .where(verified_filter)
        .group_by(SharedVerifiedQuestion.primary_year)
        .order_by(SharedVerifiedQuestion.primary_year.desc())
    )
    yr_res = await db.execute(yr_stmt)
    year_breakdown = {row[0]: row[1] for row in yr_res.all()}

    # Topic breakdown
    top_stmt = (
        select(Topic.topic_name, func.count(SharedQuestionTopic.id))
        .join(SharedQuestionTopic, Topic.id == SharedQuestionTopic.topic_id)
        .join(
            SharedVerifiedQuestion,
            SharedQuestionTopic.shared_question_id == SharedVerifiedQuestion.id,
        )
        .where(verified_filter)
        .group_by(Topic.topic_name)
        .order_by(func.count(SharedQuestionTopic.id).desc())
    )
    top_res = await db.execute(top_stmt)
    topic_breakdown = [{"topic": row[0], "count": row[1]} for row in top_res.all()]

    # Difficulty breakdown
    diff_stmt = (
        select(SharedVerifiedQuestion.difficulty, func.count(SharedVerifiedQuestion.id))
        .where(verified_filter)
        .group_by(SharedVerifiedQuestion.difficulty)
    )
    diff_res = await db.execute(diff_stmt)
    difficulty_breakdown = {
        (row[0].value if hasattr(row[0], "value") else str(row[0])): row[1]
        for row in diff_res.all()
    }

    # Recent approved questions
    recent_stmt = (
        select(SharedVerifiedQuestion)
        .where(verified_filter)
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
                topic=None,
                subtopic=None,
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
        topic_breakdown=topic_breakdown,
        difficulty_breakdown=difficulty_breakdown,
        recent_approved_questions=recent_items,
    )
