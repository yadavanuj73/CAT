"""
Shared Corpus models: Global shared verified question bank.
Accessible by all authenticated users.
Contains:
- SharedHistoricalPaper
- SharedVerifiedQuestion (with unique canonical_hash)
- SharedQuestionOption
- SharedAnswerKey
- SharedSolution
- SharedQuestionSource
- SharedQuestionTopic
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
from .question import Difficulty, QuestionType, Section


class SharedHistoricalPaper(TimestampMixin, Base):
    """
    Approved historical CAT examination paper in the shared corpus.
    Accessible to all users.
    Enforces uniqueness on file_fingerprint and (year, slot).
    """

    __tablename__ = "shared_historical_papers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    slot: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    paper_title: Mapped[str] = mapped_column(String(256), nullable=False)
    file_fingerprint: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="SHA-256 fingerprint of canonical paper",
    )
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    source_provenance: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    __table_args__ = (
        CheckConstraint("year >= 2000 AND year <= 2025", name="ck_shared_papers_year_range"),
        UniqueConstraint("year", "slot", name="uq_shared_papers_year_slot"),
    )

    # ── relationships ──────────────────────────────────────────────────
    questions: Mapped[List["SharedVerifiedQuestion"]] = relationship(
        "SharedVerifiedQuestion",
        back_populates="shared_paper",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sources: Mapped[List["SharedQuestionSource"]] = relationship(
        "SharedQuestionSource",
        back_populates="shared_paper",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<SharedHistoricalPaper {self.paper_title} (Year: {self.year})>"


class SharedVerifiedQuestion(TimestampMixin, Base):
    """
    Verified, deduplicated question in the global shared question bank.
    Enforces Level 2 Deduplication at database level via UNIQUE canonical_hash.
    """

    __tablename__ = "shared_verified_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    shared_paper_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_historical_papers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    canonical_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="SHA-256 canonical normalized representation - DB Level Unique",
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        make_enum(QuestionType, name="question_type", create_constraint=False),
        nullable=False,
    )
    section: Mapped[Section] = mapped_column(
        make_enum(Section, name="section", create_constraint=False),
        nullable=False,
        index=True,
    )
    difficulty: Mapped[Difficulty] = mapped_column(
        make_enum(Difficulty, name="difficulty", create_constraint=False),
        default=Difficulty.MEDIUM,
        nullable=False,
    )
    marks_positive: Mapped[float] = mapped_column(Float, default=3.0, nullable=False)
    marks_negative: Mapped[float] = mapped_column(Float, default=-1.0, nullable=False)
    has_image: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    has_table: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    has_passage: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    passage_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dataset_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    primary_slot: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="verified", nullable=False)
    verification_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    __table_args__ = (
        CheckConstraint("primary_year >= 2000 AND primary_year <= 2025", name="ck_shared_q_year_range"),
    )

    # ── relationships ──────────────────────────────────────────────────
    shared_paper: Mapped[Optional["SharedHistoricalPaper"]] = relationship(
        "SharedHistoricalPaper", back_populates="questions"
    )
    options: Mapped[List["SharedQuestionOption"]] = relationship(
        "SharedQuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    answer_key: Mapped[Optional["SharedAnswerKey"]] = relationship(
        "SharedAnswerKey",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    solution: Mapped[Optional["SharedSolution"]] = relationship(
        "SharedSolution",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sources: Mapped[List["SharedQuestionSource"]] = relationship(
        "SharedQuestionSource",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    topics: Mapped[List["SharedQuestionTopic"]] = relationship(
        "SharedQuestionTopic",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<SharedVerifiedQuestion id={self.id} year={self.primary_year} sec={self.section.value} #{self.question_number}>"


class SharedQuestionOption(Base):
    """Options for shared MCQ questions."""

    __tablename__ = "shared_question_options"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    shared_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_verified_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    option_label: Mapped[str] = mapped_column(String(1), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("shared_question_id", "option_label", name="uq_shared_option_question_label"),
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped["SharedVerifiedQuestion"] = relationship(
        "SharedVerifiedQuestion", back_populates="options"
    )


class SharedAnswerKey(Base):
    """Canonical correct answer for shared question."""

    __tablename__ = "shared_answer_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    shared_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_verified_questions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_type: Mapped[str] = mapped_column(String(16), default="MCQ", nullable=False)
    provenance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped["SharedVerifiedQuestion"] = relationship(
        "SharedVerifiedQuestion", back_populates="answer_key"
    )


class SharedSolution(Base):
    """Canonical solution and explanation for shared question."""

    __tablename__ = "shared_solutions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    shared_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_verified_questions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    solution_text: Mapped[str] = mapped_column(Text, nullable=False)
    approach_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped["SharedVerifiedQuestion"] = relationship(
        "SharedVerifiedQuestion", back_populates="solution"
    )


class SharedQuestionSource(Base):
    """
    Multiple source mapping for a single shared question.
    Allows a question to appear in multiple exams/slots/sources without duplication.
    """

    __tablename__ = "shared_question_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    shared_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_verified_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shared_paper_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_historical_papers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    slot: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    question_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    source_type: Mapped[str] = mapped_column(String(64), default="official", nullable=False)
    provenance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "shared_question_id", "year", "slot", "question_number",
            name="uq_shared_question_source_instance",
        ),
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped["SharedVerifiedQuestion"] = relationship(
        "SharedVerifiedQuestion", back_populates="sources"
    )
    shared_paper: Mapped[Optional["SharedHistoricalPaper"]] = relationship(
        "SharedHistoricalPaper", back_populates="sources"
    )


class SharedQuestionTopic(Base):
    """Topic classification for shared questions."""

    __tablename__ = "shared_question_topics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    shared_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_verified_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    classified_by: Mapped[str] = mapped_column(String(32), default="rule", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("shared_question_id", "topic_id", name="uq_shared_question_topic"),
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped["SharedVerifiedQuestion"] = relationship(
        "SharedVerifiedQuestion", back_populates="topics"
    )
    topic: Mapped["Topic"] = relationship("Topic", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
