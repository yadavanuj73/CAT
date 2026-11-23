"""
Historical Papers Router: Upload, List, Extraction Trigger, Provenance.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.paper import Paper
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.paper import PaperListResponse, PaperResponse
from app.services.extraction_service import extract_and_store_paper_questions
from app.services.ingestion_service import register_paper, validate_and_save_upload

router = APIRouter(prefix="/papers", tags=["Historical Papers"])


@router.post("/upload", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile,
    year: int = Form(...),
    slot: Optional[str] = Form(None),
    source_name: str = Form("Official"),
    source_type: str = Form("official"),
    source_url: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload authentic historical CAT question paper PDF."""
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
        notes=notes,
    )
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
    """Get single paper by ID."""
    stmt = select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    result = await db.execute(stmt)
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")
    return PaperResponse.model_validate(paper)


@router.post("/{paper_id}/extract")
async def trigger_extraction(
    paper_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger asynchronous extraction of questions from uploaded paper."""
    stmt = select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    result = await db.execute(stmt)
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found.")

    # Synchronous extraction for immediate feedback or background execution
    count = await extract_and_store_paper_questions(db, paper)
    return {
        "status": "success",
        "message": f"Extraction completed. {count} questions extracted.",
        "questions_count": count,
    }
