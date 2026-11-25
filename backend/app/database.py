"""
Async database connection and session management.
Supports PostgreSQL (asyncpg / Supabase PgBouncer) and SQLite (aiosqlite) for local development.
"""

from typing import AsyncGenerator, Dict, Tuple
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from app.config import settings
from app.models.base import Base


def normalize_async_database_url(raw_url: str) -> Tuple[str, Dict, Dict]:
    """
    Normalize DATABASE_URL for SQLAlchemy async engines and extract connect_args.

    Handles standard Render/Supabase `postgres://` and `postgresql://` strings,
    translates libpq `sslmode` into asyncpg `ssl`, strips incompatible PgBouncer
    query params, and disables prepared statement caches for PgBouncer transaction mode.
    """
    url = (raw_url or "").strip()
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]

    connect_args: Dict = {}
    engine_kwargs: Dict = {
        "echo": False,
        "future": True,
    }

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        return url, connect_args, engine_kwargs

    # Parse PostgreSQL query params cleanly for asyncpg
    parsed = urlsplit(url)
    kept_params = []
    for k, v in parse_qsl(parsed.query, keep_blank_values=True):
        kl = k.lower()
        if kl == "sslmode":
            if v.lower() in ("require", "verify-ca", "verify-full", "prefer"):
                connect_args["ssl"] = "require"
            elif v.lower() == "disable":
                connect_args["ssl"] = False
        elif kl in ("pgbouncer", "supa", "channel_binding"):
            continue
        else:
            kept_params.append((k, v))

    clean_url = urlunsplit((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        urlencode(kept_params),
        parsed.fragment,
    ))

    # Supabase / Neon / Render hosted PostgreSQL TLS default if sslmode wasn't set
    if "ssl" not in connect_args and parsed.hostname and (
        parsed.hostname.endswith(".supabase.co")
        or parsed.hostname.endswith(".supabase.com")
        or parsed.hostname.endswith(".render.com")
    ):
        connect_args["ssl"] = "require"

    # Disable prepared statement caching for Supabase PgBouncer transaction pooler (port 6543)
    connect_args["statement_cache_size"] = 0
    connect_args["prepared_statement_cache_size"] = 0
    engine_kwargs["poolclass"] = NullPool

    return clean_url, connect_args, engine_kwargs


DATABASE_URL, connect_args, engine_kwargs = normalize_async_database_url(settings.DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
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
