"""
Analysis result model.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, JSONType
from .question import Section


class AnalysisResult(Base):
    """Cached analysis artefact produced by the analytics engine."""

    __tablename__ = "analysis_results"

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
    analysis_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        comment="topic_frequency | difficulty_distribution | slot_analysis | trend_analysis | archetype_analysis",
    )
    parameters: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    result_data: Mapped[dict] = mapped_column(JSONType, nullable=False)
    methodology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_coverage: Mapped[Optional[dict]] = mapped_column(
        JSONType,
        nullable=True,
        comment="Which years/slots were included in this analysis",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── relationships ──────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", lazy="selectin")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"<AnalysisResult id={self.id} type={self.analysis_type!r} section={self.section.value}>"
