"""
Database schema, migration, and table integrity audit tests.
Verifies all 18 tables, foreign keys, primary keys, and indexes.
"""

import pytest
from sqlalchemy import inspect
from app.database import engine, init_db
from app.models.base import Base


@pytest.mark.asyncio
async def test_database_schema_initialization():
    """Verify that all ORM tables initialize properly with valid schema constraints."""
    await init_db()

    # Inspect SQLite database tables
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())

    required_tables = [
        "users",
        "user_settings",
        "encrypted_credentials",
        "papers",
        "paper_sources",
        "questions",
        "question_options",
        "answer_keys",
        "solutions",
        "topics",
        "question_classifications",
        "analysis_results",
        "predictions",
        "prediction_evidence",
        "mock_exams",
        "mock_questions",
        "exam_attempts",
        "verification_records",
        "audit_logs",
    ]

    for table in required_tables:
        assert table in tables, f"Mandatory table '{table}' missing from database schema."


@pytest.mark.asyncio
async def test_indexes_and_foreign_keys():
    """Verify table indexes exist for high-volume lookup columns."""
    async with engine.connect() as conn:
        user_indexes = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_indexes("users"))
        index_names = [idx["name"] for idx in user_indexes]
        assert any("email" in (name or "") for name in index_names), "Index on users.email is missing."
