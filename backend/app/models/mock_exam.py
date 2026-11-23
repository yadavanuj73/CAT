"""
Mock-exam models: MockExam, MockQuestion, ExamAttempt.
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
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, JSONType, TimestampMixin
from .question import Difficulty, QuestionType, Section


class ExamType(str, enum.Enum):
    """What kind of mock this exam represents."""

    FULL = "full"
    SECTIONAL = "sectional"
    TOPIC = "topic"
    PREDICTED = "predicted"


class MockVerificationStatus(str, enum.Enum):
    """Verification state for a mock exam or its questions."""

    PENDING = "pending"
    VERIFIED = "verified"
    PARTIAL = "partial"
    FAILED = "failed"


class AttemptStatus(str, enum.Enum):
    """Life-cycle of a user's exam attempt."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MockExam(Base):
    """A generated or curated mock examination."""

    __tablename__ = "mock_exams"

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
    exam_type: Mapped[ExamType] = mapped_column(
        Enum(ExamType, name="exam_type", create_constraint=True),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    section: Mapped[Optional[Section]] = mapped_column(
        Enum(Section, name="section", create_constraint=False, create_type=False),
        nullable=True,
        comment="For sectional mocks",
    )
    topic_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="For topic-focused mocks",
    )
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    total_marks: Mapped[float] = mapped_column(Float, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    marking_scheme: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    verification_status: Mapped[MockVerificationStatus] = mapped_column(
        Enum(MockVerificationStatus, name="mock_verification_status", create_constraint=True),
        default=MockVerificationStatus.PENDING,
        server_default=MockVerificationStatus.PENDING.value,
        nullable=False,
    )
    questions_verified: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    questions_failed: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    topic: Mapped[Optional["Topic"]] = relationship("Topic", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    questions: Mapped[List["MockQuestion"]] = relationship(
        "MockQuestion",
        back_populates="mock_exam",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attempts: Mapped[List["ExamAttempt"]] = relationship(
        "ExamAttempt",
        back_populates="mock_exam",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<MockExam id={self.id} type={self.exam_type.value!r} title={self.title!r}>"


class MockQuestion(Base):
    """A single question within a mock exam (may be AI-generated)."""

    __tablename__ = "mock_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    mock_exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mock_exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, name="question_type", create_constraint=False, create_type=False),
        nullable=False,
    )
    options: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    solution_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topic: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    subtopic: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    difficulty: Mapped[Optional[Difficulty]] = mapped_column(
        Enum(Difficulty, name="difficulty", create_constraint=False, create_type=False),
        nullable=True,
    )
    estimated_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    marks_positive: Mapped[float] = mapped_column(Float, default=3.0, nullable=False)
    marks_negative: Mapped[float] = mapped_column(Float, default=-1.0, nullable=False)
    verification_status: Mapped[MockVerificationStatus] = mapped_column(
        Enum(MockVerificationStatus, name="mock_verification_status", create_constraint=False, create_type=False),
        default=MockVerificationStatus.PENDING,
        server_default=MockVerificationStatus.PENDING.value,
        nullable=False,
    )
    verification_details: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    mock_exam: Mapped["MockExam"] = relationship("MockExam", back_populates="questions")

    def __repr__(self) -> str:
        return f"<MockQuestion exam={self.mock_exam_id} #{self.question_number}>"


class ExamAttempt(Base):
    """A user's attempt at a mock exam."""

    __tablename__ = "exam_attempts"

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
    mock_exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mock_exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    responses: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    section_scores: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus, name="attempt_status", create_constraint=True),
        default=AttemptStatus.IN_PROGRESS,
        server_default=AttemptStatus.IN_PROGRESS.value,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    mock_exam: Mapped["MockExam"] = relationship("MockExam", back_populates="attempts")

    def __repr__(self) -> str:
        return f"<ExamAttempt id={self.id} exam={self.mock_exam_id} status={self.status.value!r}>"
