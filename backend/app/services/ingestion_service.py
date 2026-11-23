"""
Historical Paper Ingestion Service.
Handles document upload, magic byte validation, SHA-256 deduplication,
source provenance recording, and file persistence.
Treats all uploaded documents as untrusted data.
"""

import hashlib
import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.paper import Paper, PaperSource, PaperStatus, SourceType

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
    slot: str,
    source_name: str,
    source_type: str,
    original_filename: str,
    file_path: str,
    file_hash: str,
    source_url: str = None,
    notes: str = None
) -> Paper:
    """Register paper record and provenance in database."""
    # Check for duplicate upload by hash
    existing = await db.execute(
        select(Paper).where(Paper.user_id == user_id, Paper.file_hash == file_hash)
    )
    dup = existing.scalar_one_or_none()
    if dup:
        return dup

    paper = Paper(
        user_id=user_id,
        year=year,
        slot=slot,
        source_name=source_name,
        original_filename=original_filename,
        file_path=file_path,
        file_hash=file_hash,
        status=PaperStatus.UPLOADED,
        extraction_confidence=0.0,
        total_questions=0,
        notes=notes,
    )
    db.add(paper)
    await db.flush()

    source = PaperSource(
        paper_id=paper.id,
        source_type=SourceType(source_type.lower()) if source_type.lower() in [s.value for s in SourceType] else SourceType.OTHER,
        source_url=source_url,
        publisher=source_name,
        is_verified=False,
    )
    db.add(source)
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
