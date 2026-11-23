"""
Paper-related models: Paper, PaperSource.
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class PaperStatus(str, enum.Enum):
    """Processing pipeline status for an uploaded paper."""

    UPLOADED = "uploaded"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    FAILED = "failed"


class SourceType(str, enum.Enum):
    """Origin category of a paper source."""

    OFFICIAL = "official"
    COACHING = "coaching"
    COMMUNITY = "community"
    OTHER = "other"


class Paper(TimestampMixin, Base):
    """A CAT question paper (PDF / image) uploaded by a user."""

    __tablename__ = "papers"

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
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    slot: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    source_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    original_filename: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(
        String(1024), nullable=True, comment="Supabase storage path"
    )
    file_hash: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True, comment="SHA-256 for dedup"
    )
    status: Mapped[PaperStatus] = mapped_column(
        Enum(PaperStatus, name="paper_status", create_constraint=True),
        default=PaperStatus.UPLOADED,
        server_default=PaperStatus.UPLOADED.value,
        nullable=False,
        index=True,
    )
    extraction_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_questions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("year >= 2000 AND year <= 2025", name="ck_papers_year_range"),
        CheckConstraint(
            "extraction_confidence IS NULL OR (extraction_confidence >= 0 AND extraction_confidence <= 1)",
            name="ck_papers_extraction_confidence_range",
        ),
    )

    # ── relationships ──────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    sources: Mapped[List["PaperSource"]] = relationship(
        "PaperSource",
        back_populates="paper",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    questions: Mapped[List["Question"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Question",
        back_populates="paper",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Paper id={self.id} year={self.year} slot={self.slot!r} status={self.status.value!r}>"


class PaperSource(Base):
    """Provenance metadata for a paper."""

    __tablename__ = "paper_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type", create_constraint=True),
        nullable=False,
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    paper: Mapped["Paper"] = relationship("Paper", back_populates="sources")

    def __repr__(self) -> str:
        return f"<PaperSource paper_id={self.paper_id} type={self.source_type.value!r}>"
