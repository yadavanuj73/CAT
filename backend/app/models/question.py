"""
Question-related models: Question, QuestionOption, AnswerKey, Solution.
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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, make_enum


class QuestionType(str, enum.Enum):
    """CAT question format."""

    MCQ = "MCQ"
    TITA = "TITA"


class Section(str, enum.Enum):
    """CAT examination sections."""

    VARC = "VARC"
    DILR = "DILR"
    QA = "QA"


class Difficulty(str, enum.Enum):
    """Subjective difficulty rating."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class VerificationStatus(str, enum.Enum):
    """Verification workflow states for extracted content."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class Question(TimestampMixin, Base):
    """An individual CAT question extracted from a paper."""

    __tablename__ = "questions"

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
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        make_enum(QuestionType, name="question_type", create_constraint=True),
        nullable=False,
    )
    section: Mapped[Section] = mapped_column(
        make_enum(Section, name="section", create_constraint=True),
        nullable=False,
        index=True,
    )
    difficulty: Mapped[Optional[Difficulty]] = mapped_column(
        make_enum(Difficulty, name="difficulty", create_constraint=True),
        nullable=True,
    )
    marks_positive: Mapped[float] = mapped_column(Float, default=3.0, nullable=False)
    marks_negative: Mapped[float] = mapped_column(Float, default=-1.0, nullable=False)
    has_image: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    has_table: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    has_passage: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    passage_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extraction_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        make_enum(VerificationStatus, name="verification_status", create_constraint=True),
        default=VerificationStatus.UNVERIFIED,
        server_default=VerificationStatus.UNVERIFIED.value,
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    slot: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    canonical_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    shared_question_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_verified_questions.id", ondelete="SET NULL"),
        nullable=True,
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dataset_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "extraction_confidence IS NULL OR (extraction_confidence >= 0 AND extraction_confidence <= 1)",
            name="ck_questions_extraction_confidence_range",
        ),
    )

    # ── relationships ──────────────────────────────────────────────────
    paper: Mapped["Paper"] = relationship("Paper", back_populates="questions")  # type: ignore[name-defined]  # noqa: F821
    user: Mapped["User"] = relationship("User", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    options: Mapped[List["QuestionOption"]] = relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    answer_key: Mapped[Optional["AnswerKey"]] = relationship(
        "AnswerKey",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    solution: Mapped[Optional["Solution"]] = relationship(
        "Solution",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    classifications: Mapped[List["QuestionClassification"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "QuestionClassification",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Question id={self.id} year={self.year} section={self.section.value} #{self.question_number}>"


class QuestionOption(Base):
    """One option (A/B/C/D) for an MCQ question."""

    __tablename__ = "question_options"

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
    option_label: Mapped[str] = mapped_column(String(1), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped["Question"] = relationship("Question", back_populates="options")

    def __repr__(self) -> str:
        return f"<QuestionOption question_id={self.question_id} label={self.option_label!r}>"


class AnswerKey(Base):
    """Canonical correct answer for a question."""

    __tablename__ = "answer_keys"

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
        unique=True,
        index=True,
    )
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped["Question"] = relationship("Question", back_populates="answer_key")

    def __repr__(self) -> str:
        return f"<AnswerKey question_id={self.question_id}>"


class Solution(Base):
    """Detailed solution / explanation for a question."""

    __tablename__ = "solutions"

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
        unique=True,
        index=True,
    )
    solution_text: Mapped[str] = mapped_column(Text, nullable=False)
    solution_source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped["Question"] = relationship("Question", back_populates="solution")

    def __repr__(self) -> str:
        return f"<Solution question_id={self.question_id}>"
