"""
Questions & Verification Router.
"""

from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.question import Question, QuestionOption, Section, VerificationStatus
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.question import (
    QuestionListResponse,
    QuestionOptionSchema,
    QuestionResponse,
    VerifyQuestionRequest,
)
from app.services.verification_service import verify_question_data

router = APIRouter(prefix="/questions", tags=["Questions & Verification"])


@router.get("", response_model=QuestionListResponse)
async def list_questions(
    section: Optional[str] = Query(None, description="VARC, DILR, QA"),
    verification_status: Optional[str] = Query(None, description="verified, unverified, needs_review, rejected"),
    year: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List questions with section and verification filters."""
    stmt = select(Question).where(Question.user_id == current_user.id)

    if section:
        stmt = stmt.where(Question.section == Section(section))
    if verification_status:
        stmt = stmt.where(Question.verification_status == VerificationStatus(verification_status))
    if year:
        stmt = stmt.where(Question.year == year)

    stmt = stmt.order_by(Question.year.desc(), Question.question_number.asc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    questions = result.scalars().all()

    items = []
    for q in questions:
        # Load options
        opt_stmt = select(QuestionOption).where(QuestionOption.question_id == q.id).order_by(QuestionOption.option_label)
        opt_res = await db.execute(opt_stmt)
        options = opt_res.scalars().all()

        items.append(
            QuestionResponse(
                id=q.id,
                paper_id=q.paper_id,
                user_id=q.user_id,
                question_number=q.question_number,
                question_text=q.question_text,
                question_type=q.question_type.value,
                section=q.section.value,
                difficulty=q.difficulty.value,
                marks_positive=q.marks_positive,
                marks_negative=q.marks_negative,
                has_image=q.has_image,
                has_table=q.has_table,
                has_passage=q.has_passage,
                passage_text=q.passage_text,
                extraction_confidence=q.extraction_confidence,
                verification_status=q.verification_status.value,
                year=q.year,
                slot=q.slot,
                options=[QuestionOptionSchema(option_label=o.option_label, option_text=o.option_text, is_correct=o.is_correct) for o in options],
                created_at=q.created_at,
            )
        )

    return QuestionListResponse(items=items, total=len(items))


@router.post("/{question_id}/verify")
async def verify_question(
    question_id: uuid.UUID,
    req: VerifyQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run independent verification checks or record manual review."""
    stmt = select(Question).where(Question.id == question_id, Question.user_id == current_user.id)
    result = await db.execute(stmt)
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")

    passed, reasons = await verify_question_data(
        db=db,
        question_id=question_id,
        manual_override=req.status_override,
        reviewer_notes=req.notes,
    )

    return {
        "question_id": str(question_id),
        "verified": passed,
        "status": q.verification_status.value,
        "validation_issues": reasons,
    }


@router.get("/stats")
async def get_question_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return count breakdown by section and verification status."""
    total_q = await db.scalar(select(func.count(Question.id)).where(Question.user_id == current_user.id)) or 0
    verified_q = await db.scalar(
        select(func.count(Question.id)).where(
            Question.user_id == current_user.id,
            Question.verification_status == VerificationStatus.VERIFIED,
        )
    ) or 0
    unverified_q = await db.scalar(
        select(func.count(Question.id)).where(
            Question.user_id == current_user.id,
            Question.verification_status == VerificationStatus.UNVERIFIED,
        )
    ) or 0
    needs_review_q = await db.scalar(
        select(func.count(Question.id)).where(
            Question.user_id == current_user.id,
            Question.verification_status == VerificationStatus.NEEDS_REVIEW,
        )
    ) or 0

    return {
        "total_questions": total_q,
        "verified": verified_q,
        "unverified": unverified_q,
        "needs_review": needs_review_q,
        "verification_rate": round((verified_q / total_q) * 100, 1) if total_q > 0 else 0.0,
    }
