"""Initial schema — all tables, indexes, constraints, and enum types.

Revision ID: 001
Revises: None
Create Date: 2026-11-23 00:00:00.000000+00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

PortableJSON = sa.JSON().with_variant(JSONB, "postgresql")
PortableArray = sa.JSON().with_variant(ARRAY(sa.Text()), "postgresql")
PortableUUID = sa.Uuid().with_variant(UUID(as_uuid=True), "postgresql")

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ── Enum types ─────────────────────────────────────────────────────────
paper_status = sa.Enum(
    "uploaded", "extracting", "extracted", "verified", "failed",
    name="paper_status",
)
source_type = sa.Enum("official", "coaching", "community", "other", name="source_type")
question_type = sa.Enum("MCQ", "TITA", name="question_type")
section = sa.Enum("VARC", "DILR", "QA", name="section")
difficulty = sa.Enum("easy", "medium", "hard", name="difficulty")
verification_status = sa.Enum(
    "unverified", "verified", "rejected", "needs_review",
    name="verification_status",
)
classified_by = sa.Enum("manual", "ai", "rule", name="classified_by")
exam_type = sa.Enum("full", "sectional", "topic", "predicted", name="exam_type")
mock_verification_status = sa.Enum(
    "pending", "verified", "partial", "failed",
    name="mock_verification_status",
)
attempt_status = sa.Enum("in_progress", "completed", "abandoned", name="attempt_status")
verification_type_enum = sa.Enum(
    "answer_check", "math_verify", "option_consistency", "duplicate_check",
    "ambiguity_check", "explanation_verify", "source_verify",
    name="verification_type",
)
verification_result = sa.Enum("passed", "failed", "warning", "skipped", name="verification_result")
verified_by = sa.Enum("system", "ai", "manual", name="verified_by")


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    # ── Create enum types ──────────────────────────────────────────────
    if is_postgres:
        paper_status.create(bind, checkfirst=True)
        source_type.create(bind, checkfirst=True)
        question_type.create(bind, checkfirst=True)
        section.create(bind, checkfirst=True)
        difficulty.create(bind, checkfirst=True)
        verification_status.create(bind, checkfirst=True)
        classified_by.create(bind, checkfirst=True)
        exam_type.create(bind, checkfirst=True)
        mock_verification_status.create(bind, checkfirst=True)
        attempt_status.create(bind, checkfirst=True)
        verification_type_enum.create(bind, checkfirst=True)
        verification_result.create(bind, checkfirst=True)
        verified_by.create(bind, checkfirst=True)

    # ── 1. users ───────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("email", sa.String(320), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── 2. user_settings ───────────────────────────────────────────────
    op.create_table(
        "user_settings",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("setting_key", sa.String(128), nullable=False),
        sa.Column("setting_value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_settings_user_id", "user_settings", ["user_id"])

    # ── 3. encrypted_credentials ───────────────────────────────────────
    op.create_table(
        "encrypted_credentials",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("encrypted_key", sa.LargeBinary(), nullable=False),
        sa.Column("iv", sa.LargeBinary(), nullable=False),
        sa.Column("auth_tag", sa.LargeBinary(), nullable=False),
        sa.Column("key_version", sa.Integer(), default=1, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_encrypted_credentials_user_id", "encrypted_credentials", ["user_id"])

    # ── 4. papers ──────────────────────────────────────────────────────
    op.create_table(
        "papers",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("slot", sa.String(32), nullable=True),
        sa.Column("source_name", sa.String(256), nullable=True),
        sa.Column("original_filename", sa.String(512), nullable=True),
        sa.Column("file_path", sa.String(1024), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("status", paper_status, server_default="uploaded", nullable=False),
        sa.Column("extraction_confidence", sa.Float(), nullable=True),
        sa.Column("total_questions", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("year >= 2000 AND year <= 2025", name="ck_papers_year_range"),
        sa.CheckConstraint(
            "extraction_confidence IS NULL OR (extraction_confidence >= 0 AND extraction_confidence <= 1)",
            name="ck_papers_extraction_confidence_range",
        ),
    )
    op.create_index("ix_papers_user_id", "papers", ["user_id"])
    op.create_index("ix_papers_file_hash", "papers", ["file_hash"])
    op.create_index("ix_papers_status", "papers", ["status"])

    # ── 5. paper_sources ───────────────────────────────────────────────
    op.create_table(
        "paper_sources",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("paper_id", PortableUUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", source_type, nullable=False),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("publisher", sa.String(256), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("verification_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_paper_sources_paper_id", "paper_sources", ["paper_id"])

    # ── 6. questions ───────────────────────────────────────────────────
    op.create_table(
        "questions",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("paper_id", PortableUUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", question_type, nullable=False),
        sa.Column("section", section, nullable=False),
        sa.Column("difficulty", difficulty, nullable=True),
        sa.Column("marks_positive", sa.Float(), nullable=False),
        sa.Column("marks_negative", sa.Float(), nullable=False),
        sa.Column("has_image", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("has_table", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("has_passage", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("passage_text", sa.Text(), nullable=True),
        sa.Column("extraction_confidence", sa.Float(), nullable=True),
        sa.Column("verification_status", verification_status, server_default="unverified", nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("slot", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "extraction_confidence IS NULL OR (extraction_confidence >= 0 AND extraction_confidence <= 1)",
            name="ck_questions_extraction_confidence_range",
        ),
    )
    op.create_index("ix_questions_paper_id", "questions", ["paper_id"])
    op.create_index("ix_questions_user_id", "questions", ["user_id"])
    op.create_index("ix_questions_section", "questions", ["section"])
    op.create_index("ix_questions_year", "questions", ["year"])
    op.create_index("ix_questions_verification_status", "questions", ["verification_status"])

    # ── 7. question_options ────────────────────────────────────────────
    op.create_table(
        "question_options",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("question_id", PortableUUID, sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("option_label", sa.String(1), nullable=False),
        sa.Column("option_text", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_question_options_question_id", "question_options", ["question_id"])

    # ── 8. answer_keys ─────────────────────────────────────────────────
    op.create_table(
        "answer_keys",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("question_id", PortableUUID, sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("answer_source", sa.Text(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_answer_keys_question_id", "answer_keys", ["question_id"], unique=True)

    # ── 9. solutions ──────────────────────────────────────────────────
    op.create_table(
        "solutions",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("question_id", PortableUUID, sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("solution_text", sa.Text(), nullable=False),
        sa.Column("solution_source", sa.Text(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_solutions_question_id", "solutions", ["question_id"], unique=True)

    # ── 10. topics ─────────────────────────────────────────────────────
    op.create_table(
        "topics",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("section", section, nullable=False),
        sa.Column("topic_name", sa.String(256), nullable=False),
        sa.Column("subtopic_name", sa.String(256), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("section", "topic_name", "subtopic_name", name="uq_topics_section_topic_subtopic"),
    )
    op.create_index("ix_topics_section", "topics", ["section"])

    # ── 11. question_classifications ───────────────────────────────────
    op.create_table(
        "question_classifications",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("question_id", PortableUUID, sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic_id", PortableUUID, sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("archetype", sa.String(256), nullable=True),
        sa.Column("concept_tags", PortableArray, nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("classified_by", classified_by, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_question_classifications_confidence_range",
        ),
    )
    op.create_index("ix_question_classifications_question_id", "question_classifications", ["question_id"])
    op.create_index("ix_question_classifications_topic_id", "question_classifications", ["topic_id"])

    # ── 12. analysis_results ───────────────────────────────────────────
    op.create_table(
        "analysis_results",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section", section, nullable=False),
        sa.Column("analysis_type", sa.String(128), nullable=False),
        sa.Column("parameters", PortableJSON, nullable=True),
        sa.Column("result_data", PortableJSON, nullable=False),
        sa.Column("methodology", sa.Text(), nullable=True),
        sa.Column("data_coverage", PortableJSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_analysis_results_user_id", "analysis_results", ["user_id"])
    op.create_index("ix_analysis_results_section", "analysis_results", ["section"])
    op.create_index("ix_analysis_results_analysis_type", "analysis_results", ["analysis_type"])

    # ── 13. predictions ────────────────────────────────────────────────
    op.create_table(
        "predictions",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section", section, nullable=False),
        sa.Column("topic_id", PortableUUID, sa.ForeignKey("topics.id", ondelete="SET NULL"), nullable=False),
        sa.Column("predicted_archetype", sa.String(256), nullable=True),
        sa.Column("statistical_score", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("limitations", sa.Text(), nullable=True),
        sa.Column("methodology", sa.Text(), nullable=True),
        sa.Column("backtesting_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "statistical_score IS NULL OR (statistical_score >= 0 AND statistical_score <= 1)",
            name="ck_predictions_statistical_score_range",
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_predictions_confidence_range",
        ),
    )
    op.create_index("ix_predictions_user_id", "predictions", ["user_id"])
    op.create_index("ix_predictions_section", "predictions", ["section"])
    op.create_index("ix_predictions_topic_id", "predictions", ["topic_id"])

    # ── 14. prediction_evidence ────────────────────────────────────────
    op.create_table(
        "prediction_evidence",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("prediction_id", PortableUUID, sa.ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", PortableUUID, sa.ForeignKey("questions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("analysis_id", PortableUUID, sa.ForeignKey("analysis_results.id", ondelete="SET NULL"), nullable=True),
        sa.Column("evidence_type", sa.String(128), nullable=False),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prediction_evidence_prediction_id", "prediction_evidence", ["prediction_id"])
    op.create_index("ix_prediction_evidence_question_id", "prediction_evidence", ["question_id"])
    op.create_index("ix_prediction_evidence_analysis_id", "prediction_evidence", ["analysis_id"])

    # ── 15. mock_exams ─────────────────────────────────────────────────
    op.create_table(
        "mock_exams",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exam_type", exam_type, nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("section", section, nullable=True),
        sa.Column("topic_id", PortableUUID, sa.ForeignKey("topics.id", ondelete="SET NULL"), nullable=True),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("total_marks", sa.Float(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("marking_scheme", PortableJSON, nullable=True),
        sa.Column("verification_status", mock_verification_status, server_default="pending", nullable=False),
        sa.Column("questions_verified", sa.Integer(), server_default="0", nullable=False),
        sa.Column("questions_failed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_mock_exams_user_id", "mock_exams", ["user_id"])
    op.create_index("ix_mock_exams_topic_id", "mock_exams", ["topic_id"])

    # ── 16. mock_questions ─────────────────────────────────────────────
    op.create_table(
        "mock_questions",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("mock_exam_id", PortableUUID, sa.ForeignKey("mock_exams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", question_type, nullable=False),
        sa.Column("options", PortableJSON, nullable=True),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("solution_text", sa.Text(), nullable=True),
        sa.Column("topic", sa.String(256), nullable=True),
        sa.Column("subtopic", sa.String(256), nullable=True),
        sa.Column("difficulty", difficulty, nullable=True),
        sa.Column("estimated_time_seconds", sa.Integer(), nullable=True),
        sa.Column("marks_positive", sa.Float(), nullable=False),
        sa.Column("marks_negative", sa.Float(), nullable=False),
        sa.Column("verification_status", mock_verification_status, server_default="pending", nullable=False),
        sa.Column("verification_details", PortableJSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_mock_questions_mock_exam_id", "mock_questions", ["mock_exam_id"])

    # ── 17. exam_attempts ──────────────────────────────────────────────
    op.create_table(
        "exam_attempts",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mock_exam_id", PortableUUID, sa.ForeignKey("mock_exams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=True),
        sa.Column("responses", PortableJSON, nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("max_score", sa.Float(), nullable=False),
        sa.Column("section_scores", PortableJSON, nullable=True),
        sa.Column("status", attempt_status, server_default="in_progress", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_exam_attempts_user_id", "exam_attempts", ["user_id"])
    op.create_index("ix_exam_attempts_mock_exam_id", "exam_attempts", ["mock_exam_id"])

    # ── 18. verification_records ───────────────────────────────────────
    op.create_table(
        "verification_records",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("question_id", PortableUUID, sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=True),
        sa.Column("mock_question_id", PortableUUID, sa.ForeignKey("mock_questions.id", ondelete="CASCADE"), nullable=True),
        sa.Column("verification_type", verification_type_enum, nullable=False),
        sa.Column("result", verification_result, nullable=False),
        sa.Column("details", PortableJSON, nullable=True),
        sa.Column("verified_by", verified_by, nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_verification_records_question_id", "verification_records", ["question_id"])
    op.create_index("ix_verification_records_mock_question_id", "verification_records", ["mock_question_id"])

    # ── 19. audit_logs ─────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(256), nullable=False),
        sa.Column("entity_type", sa.String(128), nullable=True),
        sa.Column("entity_id", PortableUUID, nullable=True),
        sa.Column("details", PortableJSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    # Drop tables in reverse dependency order.
    op.drop_table("audit_logs")
    op.drop_table("verification_records")
    op.drop_table("exam_attempts")
    op.drop_table("mock_questions")
    op.drop_table("mock_exams")
    op.drop_table("prediction_evidence")
    op.drop_table("predictions")
    op.drop_table("analysis_results")
    op.drop_table("question_classifications")
    op.drop_table("topics")
    op.drop_table("solutions")
    op.drop_table("answer_keys")
    op.drop_table("question_options")
    op.drop_table("questions")
    op.drop_table("paper_sources")
    op.drop_table("papers")
    op.drop_table("encrypted_credentials")
    op.drop_table("user_settings")
    op.drop_table("users")

    # Drop enum types.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        verified_by.drop(bind, checkfirst=True)
        verification_result.drop(bind, checkfirst=True)
        verification_type_enum.drop(bind, checkfirst=True)
        attempt_status.drop(bind, checkfirst=True)
        mock_verification_status.drop(bind, checkfirst=True)
        exam_type.drop(bind, checkfirst=True)
        classified_by.drop(bind, checkfirst=True)
        verification_status.drop(bind, checkfirst=True)
        difficulty.drop(bind, checkfirst=True)
        section.drop(bind, checkfirst=True)
        question_type.drop(bind, checkfirst=True)
        source_type.drop(bind, checkfirst=True)
        paper_status.drop(bind, checkfirst=True)
