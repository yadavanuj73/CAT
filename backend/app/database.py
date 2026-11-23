"""
Async database connection and session management.
Supports PostgreSQL (asyncpg) and SQLite (aiosqlite) for test/local environments.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from app.config import settings
from app.models.base import Base

connect_args = {}
engine_kwargs = {
    "echo": False,
    "future": True,
}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # Disable prepared statement caching for Supabase PgBouncer pooler (port 6543)
    connect_args["statement_cache_size"] = 0
    connect_args["prepared_statement_cache_size"] = 0
    engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
