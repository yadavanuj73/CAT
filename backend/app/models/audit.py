"""
Audit & verification models: VerificationRecord, AuditLog.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, JSONType, make_enum


class VerificationType(str, enum.Enum):
    """Categories of automated or manual verification checks."""

    ANSWER_CHECK = "answer_check"
    MATH_VERIFY = "math_verify"
    OPTION_CONSISTENCY = "option_consistency"
    DUPLICATE_CHECK = "duplicate_check"
    AMBIGUITY_CHECK = "ambiguity_check"
    EXPLANATION_VERIFY = "explanation_verify"
    SOURCE_VERIFY = "source_verify"


class VerificationResult(str, enum.Enum):
    """Outcome of a verification check."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class VerifiedBy(str, enum.Enum):
    """Who/what performed the verification."""

    SYSTEM = "system"
    AI = "ai"
    MANUAL = "manual"


class VerificationRecord(Base):
    """Individual verification check on a question or mock-question."""

    __tablename__ = "verification_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    question_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    mock_question_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mock_questions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    verification_type: Mapped[VerificationType] = mapped_column(
        make_enum(VerificationType, name="verification_type", create_constraint=True),
        nullable=False,
    )
    result: Mapped[VerificationResult] = mapped_column(
        make_enum(VerificationResult, name="verification_result", create_constraint=True),
        nullable=False,
    )
    details: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    verified_by: Mapped[VerifiedBy] = mapped_column(
        make_enum(VerifiedBy, name="verified_by", create_constraint=True),
        nullable=False,
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    question: Mapped[Optional["Question"]] = relationship("Question", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    mock_question: Mapped[Optional["MockQuestion"]] = relationship("MockQuestion", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        target = self.question_id or self.mock_question_id
        return f"<VerificationRecord id={self.id} target={target} result={self.result.value!r}>"


class AuditLog(Base):
    """Immutable audit trail of significant user/system actions."""

    __tablename__ = "audit_logs"

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
    action: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action!r} user={self.user_id}>"
