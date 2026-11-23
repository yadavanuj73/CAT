"""
Prediction models: Prediction, PredictionEvidence.
"""

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
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .question import Section


class Prediction(Base):
    """A single forward-looking prediction for a CAT section/topic."""

    __tablename__ = "predictions"

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
    section: Mapped[Section] = mapped_column(
        Enum(Section, name="section", create_constraint=False, create_type=False),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    predicted_archetype: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    statistical_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    limitations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    methodology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    backtesting_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "statistical_score IS NULL OR (statistical_score >= 0 AND statistical_score <= 1)",
            name="ck_predictions_statistical_score_range",
        ),
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_predictions_confidence_range",
        ),
    )

    # ── relationships ──────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    topic: Mapped["Topic"] = relationship("Topic", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    evidence: Mapped[List["PredictionEvidence"]] = relationship(
        "PredictionEvidence",
        back_populates="prediction",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Prediction id={self.id} section={self.section.value} topic={self.topic_id}>"


class PredictionEvidence(Base):
    """Supporting evidence for a prediction."""

    __tablename__ = "prediction_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    analysis_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_results.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    evidence_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="historical_frequency | trend | archetype_match | expert_input",
    )
    evidence_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    prediction: Mapped["Prediction"] = relationship("Prediction", back_populates="evidence")
    question: Mapped[Optional["Question"]] = relationship("Question", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    analysis: Mapped[Optional["AnalysisResult"]] = relationship("AnalysisResult", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"<PredictionEvidence id={self.id} type={self.evidence_type!r}>"
