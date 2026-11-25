"""Align shared_verified_questions enum column types safely on PostgreSQL.

Revision ID: 003
Revises: 002
Create Date: 2026-11-25 01:35:00.000000+00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        # On SQLite, enum columns are already stored as affinity TEXT/VARCHAR.
        inspector = sa.inspect(bind)
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("shared_verified_questions")
        }
        if "ix_shared_verified_questions_verification_status" not in existing_indexes:
            op.create_index(
                "ix_shared_verified_questions_verification_status",
                "shared_verified_questions",
                ["verification_status"],
            )
        return

    # Ensure enum types exist in PostgreSQL (created in 001, guarded with duplicate_object)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'question_type') THEN
                CREATE TYPE question_type AS ENUM ('MCQ', 'TITA');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'section') THEN
                CREATE TYPE section AS ENUM ('VARC', 'DILR', 'QA');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'difficulty') THEN
                CREATE TYPE difficulty AS ENUM ('easy', 'medium', 'hard');
            END IF;
        END$$;
        """
    )

    # Non-destructively convert VARCHAR(16) columns created by migration 002
    # to their corresponding PostgreSQL enum types if not already converted.
    op.execute(
        """
        DO $$
        DECLARE
            qt_type text;
            sec_type text;
            diff_type text;
        BEGIN
            SELECT data_type INTO qt_type
            FROM information_schema.columns
            WHERE table_name = 'shared_verified_questions' AND column_name = 'question_type';

            IF qt_type = 'character varying' THEN
                ALTER TABLE shared_verified_questions
                ALTER COLUMN question_type TYPE question_type USING question_type::question_type;
            END IF;

            SELECT data_type INTO sec_type
            FROM information_schema.columns
            WHERE table_name = 'shared_verified_questions' AND column_name = 'section';

            IF sec_type = 'character varying' THEN
                ALTER TABLE shared_verified_questions
                ALTER COLUMN section TYPE section USING section::section;
            END IF;

            SELECT data_type INTO diff_type
            FROM information_schema.columns
            WHERE table_name = 'shared_verified_questions' AND column_name = 'difficulty';

            IF diff_type = 'character varying' THEN
                ALTER TABLE shared_verified_questions ALTER COLUMN difficulty DROP DEFAULT;
                ALTER TABLE shared_verified_questions
                ALTER COLUMN difficulty TYPE difficulty USING difficulty::difficulty;
                ALTER TABLE shared_verified_questions ALTER COLUMN difficulty SET DEFAULT 'medium'::difficulty;
            END IF;
        END$$;
        """
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_shared_verified_questions_verification_status "
        "ON shared_verified_questions (verification_status);"
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.execute(
        "DROP INDEX IF EXISTS ix_shared_verified_questions_verification_status;"
    )
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            DO $$
            BEGIN
                ALTER TABLE shared_verified_questions
                    ALTER COLUMN difficulty DROP DEFAULT,
                    ALTER COLUMN difficulty TYPE VARCHAR(16) USING difficulty::text,
                    ALTER COLUMN difficulty SET DEFAULT 'medium';
                ALTER TABLE shared_verified_questions
                    ALTER COLUMN section TYPE VARCHAR(16) USING section::text;
                ALTER TABLE shared_verified_questions
                    ALTER COLUMN question_type TYPE VARCHAR(16) USING question_type::text;
            EXCEPTION WHEN others THEN
                NULL;
            END$$;
            """
        )
