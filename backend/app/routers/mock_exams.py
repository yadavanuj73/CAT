"""
Mock Exams & Question Generation Router.
"""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.mock_exam import ExamAttempt, MockExam, MockQuestion
from app.models.user import User
from app.routers.deps import get_current_user, get_session_id
from app.schemas.mock_exam import (
    AttemptResult,
    AttemptSubmission,
    MockExamResponse,
    MockGenerateRequest,
    MockQuestionOption,
    MockQuestionResponse,
)
from app.services.generation_service import generate_mock_exam
from app.services.session_service import resolve_api_key

router = APIRouter(prefix="/mocks", tags=["Mock Examinations"])


@router.post("/generate", response_model=MockExamResponse, status_code=status.HTTP_201_CREATED)
async def create_mock_exam(
    req: MockGenerateRequest,
    current_user: User = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate CAT 2026 Practice Mock Paper.
    All questions pass through independent mathematical and option verification.
    """
    api_key = await resolve_api_key(db, current_user.id, session_id)
    exam = await generate_mock_exam(db, current_user.id, req, api_key=api_key)

    stmt = select(MockQuestion).where(MockQuestion.mock_exam_id == exam.id).order_by(MockQuestion.question_number)
    q_res = await db.execute(stmt)
    questions = q_res.scalars().all()

    q_items = [
        MockQuestionResponse(
            id=q.id,
            mock_exam_id=q.mock_exam_id,
            question_number=q.question_number,
            question_text=q.question_text,
            question_type=q.question_type.value,
            options=[MockQuestionOption(**opt) for opt in q.options] if q.options else None,
            correct_answer=q.correct_answer,
            solution_text=q.solution_text,
            topic=q.topic,
            subtopic=q.subtopic,
            difficulty=q.difficulty.value,
            estimated_time_seconds=q.estimated_time_seconds,
            marks_positive=q.marks_positive,
            marks_negative=q.marks_negative,
            verification_status=q.verification_status.value,
            verification_details=q.verification_details,
        )
        for q in questions
    ]

    res = MockExamResponse.model_validate(exam)
    res.questions = q_items
    return res


@router.get("", response_model=List[MockExamResponse])
async def list_mock_exams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List mock examinations generated for user."""
    stmt = select(MockExam).where(MockExam.user_id == current_user.id).order_by(MockExam.created_at.desc())
    result = await db.execute(stmt)
    exams = result.scalars().all()
    return [MockExamResponse.model_validate(e) for e in exams]


@router.get("/{mock_id}", response_model=MockExamResponse)
async def get_mock_exam(
    mock_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve mock exam with all verified questions and solutions."""
    stmt = select(MockExam).where(MockExam.id == mock_id, MockExam.user_id == current_user.id)
    result = await db.execute(stmt)
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Mock examination not found.")

    q_stmt = select(MockQuestion).where(MockQuestion.mock_exam_id == mock_id).order_by(MockQuestion.question_number)
    q_res = await db.execute(q_stmt)
    questions = q_res.scalars().all()

    q_items = [
        MockQuestionResponse(
            id=q.id,
            mock_exam_id=q.mock_exam_id,
            question_number=q.question_number,
            question_text=q.question_text,
            question_type=q.question_type.value,
            options=[MockQuestionOption(**opt) for opt in q.options] if q.options else None,
            correct_answer=q.correct_answer,
            solution_text=q.solution_text,
            topic=q.topic,
            subtopic=q.subtopic,
            difficulty=q.difficulty.value,
            estimated_time_seconds=q.estimated_time_seconds,
            marks_positive=q.marks_positive,
            marks_negative=q.marks_negative,
            verification_status=q.verification_status.value,
            verification_details=q.verification_details,
        )
        for q in questions
    ]

    res = MockExamResponse.model_validate(exam)
    res.questions = q_items
    return res


@router.post("/{mock_id}/attempt", response_model=AttemptResult)
async def submit_mock_attempt(
    mock_id: uuid.UUID,
    sub: AttemptSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit answers for grading against verified answer keys."""
    stmt = select(MockExam).where(MockExam.id == mock_id, MockExam.user_id == current_user.id)
    exam = (await db.execute(stmt)).scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Mock exam not found.")

    q_stmt = select(MockQuestion).where(MockQuestion.mock_exam_id == mock_id)
    questions = (await db.execute(q_stmt)).scalars().all()

    total_score = 0.0
    correct_count = 0
    incorrect_count = 0
    feedback = []

    for q in questions:
        user_ans = sub.responses.get(str(q.id), "").strip()
        is_attempted = bool(user_ans)
        is_correct = False

        if is_attempted:
            if user_ans.lower() == q.correct_answer.strip().lower():
                is_correct = True
                total_score += q.marks_positive
                correct_count += 1
            else:
                total_score -= q.marks_negative
                incorrect_count += 1

        feedback.append({
            "question_id": str(q.id),
            "question_number": q.question_number,
            "user_answer": user_ans,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "solution": q.solution_text,
        })

    total_attempted = correct_count + incorrect_count
    accuracy = round((correct_count / total_attempted * 100), 1) if total_attempted > 0 else 0.0
    pct = round((max(0.0, total_score) / exam.total_marks * 100), 1) if exam.total_marks > 0 else 0.0

    attempt = ExamAttempt(
        user_id=current_user.id,
        mock_exam_id=mock_id,
        time_spent_seconds=sub.time_spent_seconds,
        responses=sub.responses,
        score=total_score,
        max_score=exam.total_marks,
        status="completed",
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    return AttemptResult(
        attempt_id=attempt.id,
        mock_exam_id=mock_id,
        total_score=total_score,
        max_score=exam.total_marks,
        percentage=pct,
        accuracy_percentage=accuracy,
        total_attempted=total_attempted,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        section_breakdown={"overall": {"score": total_score, "max": exam.total_marks}},
        detailed_feedback=feedback,
    )
