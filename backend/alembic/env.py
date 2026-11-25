"""
Alembic async environment for CAT Intelligence 2026.

This env.py drives migrations against an **asyncpg** (or local aiosqlite) connection
so the same engine settings used by the application can be reused here.
"""

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# ── Import all models so metadata is populated ────────────────────────
from app.models import Base  # noqa: F401  (registers all tables)
from app.config import settings
from app.database import normalize_async_database_url

# Alembic Config object (provides access to alembic.ini values).
config = context.config

# Interpret the alembic.ini [loggers] section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support.
target_metadata = Base.metadata

# Allow overriding the DB URL via environment variable or app settings.
raw_url = os.getenv("SQLALCHEMY_DATABASE_URL") or os.getenv("DATABASE_URL") or settings.DATABASE_URL
DATABASE_URL, CONNECT_ARGS, _ = normalize_async_database_url(raw_url)
if DATABASE_URL:
    # Escape '%' to avoid ConfigParser interpolation failures on URL-encoded passwords
    config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = DATABASE_URL or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Helper that configures the migration context on a live connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations inside its connection."""
    connectable = create_async_engine(
        DATABASE_URL,
        connect_args=CONNECT_ARGS,
        poolclass=pool.NullPool,
        future=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
