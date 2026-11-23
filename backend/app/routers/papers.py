"""
Historical Papers Router: Upload, List, Extraction Trigger, Provenance & Contribution History.
"""

import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.paper import Paper, PaperStatus
from app.models.question import Question, VerificationStatus
from app.models.user import User
from app.models.user_history import UserProcessingHistory
from app.routers.deps import get_current_user
from app.schemas.paper import (
    PaperContributionSummary,
    PaperListResponse,
    PaperResponse,
    UserProcessingHistoryResponse,
)
from app.services.extraction_service import extract_and_store_paper_questions
from app.services.ingestion_service import register_paper, validate_and_save_upload
from app.services.sharing_service import evaluate_and_promote_paper_to_shared_bank
from app.services.verification_service import verify_question_data

router = APIRouter(prefix="/papers", tags=["Historical Papers"])


@router.post("/upload", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile,
    year: int = Form(...),
    slot: Optional[str] = Form(None),
    source_name: str = Form("Official"),
    source_type: str = Form("official"),
    source_url: Optional[str] = Form(None),
    allow_sharing: bool = Form(True),
    terms_accepted: bool = Form(True),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload authentic historical CAT question paper PDF with sharing consent."""
    if year < 2000 or year > 2025:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year must be between 2000 and 2025.",
        )

    saved_path, file_hash, _ = await validate_and_save_upload(file, current_user.id)
    paper = await register_paper(
        db=db,
        user_id=current_user.id,
        year=year,
        slot=slot,
        source_name=source_name,
        source_type=source_type,
        original_filename=file.filename or "paper.pdf",
        file_path=saved_path,
        file_hash=file_hash,
        source_url=source_url,
        allow_sharing=allow_sharing,
        terms_accepted=terms_accepted,
        notes=notes,
    )

    # Immediately extract and verify questions while file is fresh in local storage
    if not paper.is_duplicate or (paper.total_questions or 0) == 0:
        try:
            await extract_and_store_paper_questions(db, paper)
            q_stmt = select(Question).where(Question.paper_id == paper.id)
            questions = (await db.execute(q_stmt)).scalars().all()
            for q in questions:
                try:
                    await verify_question_data(db, q.id)
                except Exception:
                    pass
            if allow_sharing:
                await evaluate_and_promote_paper_to_shared_bank(db, paper.id)
        except Exception as e:
            # Paper registration succeeds even if OCR/extraction encounters issues
            pass

    await db.refresh(paper)
    return PaperResponse.model_validate(paper)


@router.get("", response_model=PaperListResponse)
async def list_papers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all papers uploaded by the authenticated user."""
    stmt = select(Paper).where(Paper.user_id == current_user.id).order_by(Paper.year.desc())
    result = await db.execute(stmt)
    papers = result.scalars().all()
    return PaperListResponse(
        items=[PaperResponse.model_validate(p) for p in papers],
        total=len(papers),
    )


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get single paper by ID (private to the uploading user)."""
    stmt = select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    result = await db.execute(stmt)
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")
    return PaperResponse.model_validate(paper)


@router.get("/{paper_id}/history", response_model=List[UserProcessingHistoryResponse])
async def get_paper_processing_history(
    paper_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get processing audit logs for a user upload."""
    # Ensure paper belongs to current user
    stmt = select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    paper = (await db.execute(stmt)).scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")

    hist_stmt = (
        select(UserProcessingHistory)
        .where(UserProcessingHistory.paper_id == paper_id, UserProcessingHistory.user_id == current_user.id)
        .order_by(UserProcessingHistory.created_at.asc())
    )
    res = await db.execute(hist_stmt)
    return [UserProcessingHistoryResponse.model_validate(h) for h in res.scalars().all()]


@router.get("/{paper_id}/summary", response_model=PaperContributionSummary)
async def get_paper_contribution_summary(
    paper_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get contribution summary for an uploaded paper."""
    stmt = select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    paper = (await db.execute(stmt)).scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")

    # Calculate question counts
    q_stmt = select(Question).where(Question.paper_id == paper_id)
    questions = (await db.execute(q_stmt)).scalars().all()

    total_extracted = len(questions)
    total_verified = sum(1 for q in questions if q.verification_status == VerificationStatus.VERIFIED)
    total_rejected = sum(1 for q in questions if q.verification_status == VerificationStatus.REJECTED)
    total_duplicate = sum(1 for q in questions if q.shared_question_id is not None and q.canonical_hash is not None)
    promoted = sum(1 for q in questions if q.shared_question_id is not None)

    return PaperContributionSummary(
        paper_id=paper.id,
        year=paper.year,
        slot=paper.slot,
        status=paper.status.value if hasattr(paper.status, "value") else str(paper.status),
        total_extracted=total_extracted,
        total_verified=total_verified,
        total_duplicate=total_duplicate,
        total_rejected=total_rejected,
        promoted_to_shared=promoted,
        shared_paper_id=paper.shared_paper_id,
        sharing_status=paper.sharing_status,
    )


@router.post("/{paper_id}/extract")
async def trigger_extraction(
    paper_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger end-to-end processing:
    1. Extract questions if not duplicate.
    2. Run verification pipeline.
    3. Promote verified eligible questions into global shared question bank.
    """
    stmt = select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    result = await db.execute(stmt)
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")

    # If it is an exact Level 1 duplicate of an existing shared paper, no re-OCR needed!
    if paper.is_duplicate and paper.shared_paper_id:
        return {
            "status": "duplicate_reused",
            "message": "Exact duplicate paper detected. Reused existing verified shared questions.",
            "questions_count": paper.total_questions,
            "shared_paper_id": str(paper.shared_paper_id),
        }

    # Verify that the physical file exists in current container storage
    if not paper.file_path or not os.path.exists(paper.file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The original PDF file is not on the server container (containers restart periodically). Please re-upload the PDF to automatically extract and publish questions.",
        )

    # Extract questions
    count = await extract_and_store_paper_questions(db, paper)

    # Automatically verify extracted questions
    q_stmt = select(Question).where(Question.paper_id == paper.id)
    questions = (await db.execute(q_stmt)).scalars().all()
    for q in questions:
        try:
            await verify_question_data(db, q.id)
        except Exception:
            pass

    # Evaluate and promote verified questions to the shared question bank
    promotion_result = await evaluate_and_promote_paper_to_shared_bank(db, paper.id)

    return {
        "status": "success",
        "message": f"Extraction and verification completed. {count} questions extracted.",
        "questions_count": count,
        "promotion": promotion_result,
    }


@router.delete("/{paper_id}", status_code=status.HTTP_200_OK)
async def delete_paper(
    paper_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an uploaded paper record and any unverified questions."""
    stmt = select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    paper = (await db.execute(stmt)).scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")

    if paper.file_path and os.path.exists(paper.file_path):
        try:
            os.remove(paper.file_path)
        except Exception:
            pass

    await db.delete(paper)
    await db.commit()
    return {"status": "success", "message": "Paper record removed."}
