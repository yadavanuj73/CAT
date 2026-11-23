"""
Topic & classification models: Topic, QuestionClassification.
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, ArrayType, make_enum
from .question import Section


class ClassifiedBy(str, enum.Enum):
    """Who/what performed the classification."""

    MANUAL = "manual"
    AI = "ai"
    RULE = "rule"


class Topic(Base):
    """Canonical topic/subtopic within a CAT section."""

    __tablename__ = "topics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    section: Mapped[Section] = mapped_column(
        make_enum(Section, name="section", create_constraint=False, create_type=False),
        nullable=False,
        index=True,
    )
    topic_name: Mapped[str] = mapped_column(String(256), nullable=False)
    subtopic_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("section", "topic_name", "subtopic_name", name="uq_topics_section_topic_subtopic"),
    )

    # ── relationships ──────────────────────────────────────────────────
    classifications: Mapped[List["QuestionClassification"]] = relationship(
        "QuestionClassification",
        back_populates="topic",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        sub = f"/{self.subtopic_name}" if self.subtopic_name else ""
        return f"<Topic {self.section.value}:{self.topic_name}{sub}>"


class QuestionClassification(Base):
    """Maps a question to a topic with an optional archetype & tags."""

    __tablename__ = "question_classifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    archetype: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    concept_tags: Mapped[Optional[list]] = mapped_column(
        ArrayType, nullable=True, default=list
    )
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    classified_by: Mapped[ClassifiedBy] = mapped_column(
        make_enum(ClassifiedBy, name="classified_by", create_constraint=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_question_classifications_confidence_range",
        ),
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped["Question"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Question", back_populates="classifications"
    )
    topic: Mapped["Topic"] = relationship("Topic", back_populates="classifications")

    def __repr__(self) -> str:
        return f"<QuestionClassification question={self.question_id} topic={self.topic_id}>"
