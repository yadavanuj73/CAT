"""
Deduplication and Review Queue models:
- PaperFingerprint
- QuestionFingerprint
- DuplicateDetectionRecord
- QuestionSimilarityReview
- ReviewQueue
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, JSONType, TimestampMixin


class PaperFingerprint(Base):
    """Level 1 Deduplication: PDF SHA-256 fingerprint registry."""

    __tablename__ = "paper_fingerprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    file_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="SHA-256 hash of paper PDF content",
    )
    shared_paper_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_historical_papers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    times_seen: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class QuestionFingerprint(Base):
    """Level 2 Deduplication: Canonical question fingerprint registry."""

    __tablename__ = "question_fingerprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    canonical_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="SHA-256 of normalized canonical question representation",
    )
    shared_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_verified_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class DuplicateDetectionRecord(Base):
    """Audit log of all duplicate detection events across all 3 levels."""

    __tablename__ = "duplicate_detection_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="paper or question")
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    detection_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="exact_pdf, exact_canonical, semantic",
    )
    similarity_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    match_metadata: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    action_taken: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="skipped, merged_source, needs_review, rejected",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class QuestionSimilarityReview(Base):
    """Level 3 Deduplication: Semantic similarity candidates flagged for review."""

    __tablename__ = "question_similarity_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    candidate_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    existing_shared_question_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_verified_questions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        nullable=False,
        comment="pending, approved_as_new, merged_as_duplicate, rejected",
    )
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ReviewQueue(Base):
    """General review queue for flagged content (ambiguous, OCR low confidence, etc.)."""

    __tablename__ = "review_queue"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="paper, question, similarity")
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        nullable=False,
        comment="pending, in_review, resolved, dismissed",
    )
    assigned_to: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
