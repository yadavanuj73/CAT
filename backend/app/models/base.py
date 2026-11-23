"""
Base model classes and mixins for the CAT Intelligence 2026 platform.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, Text, Uuid, func
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY, JSONB as PG_JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Portable cross-database types (PostgreSQL native in prod, SQLite compatible in test)
JSONType = JSON().with_variant(PG_JSONB, "postgresql")
ArrayType = JSON().with_variant(PG_ARRAY(Text), "postgresql")
UUIDType = Uuid(as_uuid=True)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
