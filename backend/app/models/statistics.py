"""
Statistics and Analytics Caching models:
- TopicFrequencyStatistic
- YearlyTrend
- DifficultyStatistic
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TopicFrequencyStatistic(Base):
    """Aggregated topic frequency derived strictly from verified shared questions."""

    __tablename__ = "topic_frequency_statistics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    section: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    subtopic: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    total_occurrences: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recent_occurrences: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    frequency_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recency_weighted_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("section", "topic", "subtopic", name="uq_topic_freq_sec_topic_sub"),
    )


class YearlyTrend(Base):
    """Yearly trends across examination sections."""

    __tablename__ = "yearly_trends"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    section: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mcq_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tita_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    easy_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    medium_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hard_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("year", "section", name="uq_yearly_trend_year_section"),
    )


class DifficultyStatistic(Base):
    """Difficulty distribution stats per section."""

    __tablename__ = "difficulty_statistics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    section: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(16), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("section", "difficulty", name="uq_diff_stat_section_diff"),
    )
