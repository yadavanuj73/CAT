"""
User History and Permission models:
- UserUploadPermission (explicit user consent & legal eligibility)
- UserProcessingHistory (step-by-step private upload execution log)
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, JSONType


class UserUploadPermission(Base):
    """Explicit user authorization for sharing uploaded content."""

    __tablename__ = "user_upload_permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    allow_sharing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    terms_accepted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    legal_eligibility_confirmed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class UserProcessingHistory(Base):
    """Private detailed processing audit trail for an individual user's upload."""

    __tablename__ = "user_processing_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="upload, validation, deduplication, extraction, classification, verification, sharing_evaluation, promotion",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="started, completed, failed, skipped, duplicate_detected",
    )
    details: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
