"""
Historical Paper Ingestion Service.
Handles document upload, magic byte validation, SHA-256 deduplication,
source provenance recording, user consent tracking, and file persistence.
Treats all uploaded documents as untrusted data.
"""

import hashlib
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.deduplication import DuplicateDetectionRecord
from app.models.paper import Paper, PaperSource, PaperStatus, SourceType
from app.models.user_history import UserProcessingHistory, UserUploadPermission
from app.services.deduplication_service import check_exact_paper_duplicate, register_paper_fingerprint

UPLOAD_DIR = Path("uploads/papers")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# PDF Magic Bytes: %PDF-
PDF_MAGIC_BYTES = b"%PDF"


async def validate_and_save_upload(
    upload_file: UploadFile,
    user_id: uuid.UUID
) -> Tuple[str, str, int]:
    """
    Validate uploaded file:
    - Checks file extension
    - Checks magic bytes (%PDF)
    - Validates file size constraint
    - Computes SHA-256 checksum
    Returns: (file_path, file_hash, file_size)
    """
    ext = os.path.splitext(upload_file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension {ext}. Only PDF documents are allowed.",
        )

    # Read content and compute hash
    content = await upload_file.read()
    file_size = len(content)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )

    # Check PDF magic bytes
    if not content.startswith(PDF_MAGIC_BYTES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid PDF document (magic byte signature mismatch).",
        )

    file_hash = hashlib.sha256(content).hexdigest()
    filename = f"{user_id}_{file_hash[:16]}_{Path(upload_file.filename).name}"
    save_path = UPLOAD_DIR / filename

    with open(save_path, "wb") as f:
        f.write(content)

    return str(save_path), file_hash, file_size


async def register_paper(
    db: AsyncSession,
    user_id: uuid.UUID,
    year: int,
    slot: Optional[str],
    source_name: str,
    source_type: str,
    original_filename: str,
    file_path: str,
    file_hash: str,
    source_url: Optional[str] = None,
    allow_sharing: bool = True,
    terms_accepted: bool = True,
    notes: Optional[str] = None
) -> Paper:
    """Register paper record, user consent, processing history, and provenance in database."""
    # 1. Check for duplicate upload by this specific user
    existing = await db.execute(
        select(Paper).where(Paper.user_id == user_id, Paper.file_hash == file_hash)
    )
    dup = existing.scalar_one_or_none()
    if dup:
        return dup

    # 2. Level 1 Duplicate Detection against the Global Shared Question Bank
    shared_dup = await check_exact_paper_duplicate(db, file_hash)
    is_shared_duplicate = shared_dup is not None

    paper = Paper(
        user_id=user_id,
        year=year,
        slot=slot,
        source_name=source_name,
        original_filename=original_filename,
        file_path=file_path,
        file_hash=file_hash,
        status=PaperStatus.EXTRACTED if is_shared_duplicate else PaperStatus.UPLOADED,
        extraction_confidence=1.0 if is_shared_duplicate else 0.0,
        total_questions=shared_dup.total_questions if is_shared_duplicate else 0,
        allow_sharing=allow_sharing,
        sharing_status="approved" if is_shared_duplicate and allow_sharing else ("pending" if allow_sharing else "private"),
        is_duplicate=is_shared_duplicate,
        duplicate_of_id=shared_dup.id if is_shared_duplicate else None,
        shared_paper_id=shared_dup.id if is_shared_duplicate else None,
        notes=f"Identical paper already in shared bank. Reused verified questions." if is_shared_duplicate else notes,
    )
    db.add(paper)
    await db.flush()

    # Record source provenance
    source = PaperSource(
        paper_id=paper.id,
        source_type=SourceType(source_type.lower()) if source_type.lower() in [s.value for s in SourceType] else SourceType.OTHER,
        source_url=source_url,
        publisher=source_name,
        is_verified=is_shared_duplicate,
    )
    db.add(source)

    # Record explicit user consent permission
    permission = UserUploadPermission(
        user_id=user_id,
        paper_id=paper.id,
        allow_sharing=allow_sharing,
        terms_accepted=terms_accepted,
        legal_eligibility_confirmed=True,
    )
    db.add(permission)

    # Record processing history
    stage_status = "duplicate_detected" if is_shared_duplicate else "completed"
    details = {
        "file_hash": file_hash,
        "is_duplicate": is_shared_duplicate,
        "shared_paper_id": str(shared_dup.id) if shared_dup else None,
        "reused_questions": shared_dup.total_questions if shared_dup else 0,
    }
    history = UserProcessingHistory(
        user_id=user_id,
        paper_id=paper.id,
        stage="upload_validation",
        status=stage_status,
        details=details,
    )
    db.add(history)

    # Record duplicate detection record if Level 1 duplicate
    if is_shared_duplicate:
        dup_rec = DuplicateDetectionRecord(
            entity_type="paper",
            source_id=paper.id,
            target_id=shared_dup.id,
            detection_level="exact_pdf",
            similarity_score=1.0,
            match_metadata={"file_hash": file_hash},
            action_taken="skipped",
        )
        db.add(dup_rec)

    await db.commit()
    await db.refresh(paper)
    return paper


async def recover_stalled_paper_extractions(db: AsyncSession) -> int:
    """
    Failure recovery utility for interrupted extractions (e.g. Render container restarts).
    Finds papers left in EXTRACTING state and marks them as FAILED with retry instructions.
    """
    from sqlalchemy import update
    stmt = (
        update(Paper)
        .where(Paper.status == PaperStatus.EXTRACTING)
        .values(
            status=PaperStatus.FAILED,
            notes="Extraction interrupted by container restart or unexpected termination. Ready for retry.",
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
