"""Shared corpus, deduplication engine, and user processing history schema.

Revision ID: 002
Revises: 001
Create Date: 2026-11-23 01:00:00.000000+00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

PortableJSON = sa.JSON().with_variant(JSONB, "postgresql")
PortableArray = sa.JSON().with_variant(ARRAY(sa.Text()), "postgresql")
PortableUUID = sa.Uuid().with_variant(UUID(as_uuid=True), "postgresql")

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    # ── 1. shared_historical_papers ────────────────────────────────────
    op.create_table(
        "shared_historical_papers",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("slot", sa.String(32), nullable=True),
        sa.Column("paper_title", sa.String(256), nullable=False),
        sa.Column("file_fingerprint", sa.String(64), unique=True, nullable=False),
        sa.Column("total_questions", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("source_provenance", sa.String(256), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("year >= 2000 AND year <= 2025", name="ck_shared_papers_year_range"),
        sa.UniqueConstraint("year", "slot", name="uq_shared_papers_year_slot"),
    )
    op.create_index("ix_shared_historical_papers_year", "shared_historical_papers", ["year"])
    op.create_index("ix_shared_historical_papers_file_fingerprint", "shared_historical_papers", ["file_fingerprint"], unique=True)

    # ── 2. shared_verified_questions ───────────────────────────────────
    op.create_table(
        "shared_verified_questions",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("shared_paper_id", PortableUUID, sa.ForeignKey("shared_historical_papers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("canonical_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("canonical_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(16), nullable=False),
        sa.Column("section", sa.String(16), nullable=False),
        sa.Column("difficulty", sa.String(16), server_default="medium", nullable=False),
        sa.Column("marks_positive", sa.Float(), server_default="3.0", nullable=False),
        sa.Column("marks_negative", sa.Float(), server_default="-1.0", nullable=False),
        sa.Column("has_image", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("has_table", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("has_passage", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("passage_text", sa.Text(), nullable=True),
        sa.Column("dataset_text", sa.Text(), nullable=True),
        sa.Column("primary_year", sa.Integer(), nullable=False),
        sa.Column("primary_slot", sa.String(32), nullable=True),
        sa.Column("verification_status", sa.String(32), server_default="verified", nullable=False),
        sa.Column("verification_confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("primary_year >= 2000 AND primary_year <= 2025", name="ck_shared_q_year_range"),
    )
    op.create_index("ix_shared_verified_questions_canonical_hash", "shared_verified_questions", ["canonical_hash"], unique=True)
    op.create_index("ix_shared_verified_questions_primary_year", "shared_verified_questions", ["primary_year"])
    op.create_index("ix_shared_verified_questions_section", "shared_verified_questions", ["section"])
    op.create_index("ix_shared_verified_questions_shared_paper_id", "shared_verified_questions", ["shared_paper_id"])

    # ── 3. shared_question_options ─────────────────────────────────────
    op.create_table(
        "shared_question_options",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("shared_question_id", PortableUUID, sa.ForeignKey("shared_verified_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("option_label", sa.String(1), nullable=False),
        sa.Column("option_text", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("shared_question_id", "option_label", name="uq_shared_option_question_label"),
    )
    op.create_index("ix_shared_question_options_shared_question_id", "shared_question_options", ["shared_question_id"])

    # ── 4. shared_answer_keys ──────────────────────────────────────────
    op.create_table(
        "shared_answer_keys",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("shared_question_id", PortableUUID, sa.ForeignKey("shared_verified_questions.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("answer_type", sa.String(16), server_default="MCQ", nullable=False),
        sa.Column("provenance", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── 5. shared_solutions ────────────────────────────────────────────
    op.create_table(
        "shared_solutions",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("shared_question_id", PortableUUID, sa.ForeignKey("shared_verified_questions.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("solution_text", sa.Text(), nullable=False),
        sa.Column("approach_type", sa.String(64), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── 6. shared_question_sources ─────────────────────────────────────
    op.create_table(
        "shared_question_sources",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("shared_question_id", PortableUUID, sa.ForeignKey("shared_verified_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shared_paper_id", PortableUUID, sa.ForeignKey("shared_historical_papers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("slot", sa.String(32), nullable=True),
        sa.Column("question_number", sa.Integer(), nullable=True),
        sa.Column("source_name", sa.String(256), nullable=True),
        sa.Column("source_type", sa.String(64), server_default="official", nullable=False),
        sa.Column("provenance_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("shared_question_id", "year", "slot", "question_number", name="uq_shared_question_source_instance"),
    )
    op.create_index("ix_shared_question_sources_shared_question_id", "shared_question_sources", ["shared_question_id"])

    # ── 7. shared_question_topics ──────────────────────────────────────
    op.create_table(
        "shared_question_topics",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("shared_question_id", PortableUUID, sa.ForeignKey("shared_verified_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic_id", PortableUUID, sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("classified_by", sa.String(32), server_default="rule", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("shared_question_id", "topic_id", name="uq_shared_question_topic"),
    )
    op.create_index("ix_shared_question_topics_shared_question_id", "shared_question_topics", ["shared_question_id"])

    # ── 8. paper_fingerprints ──────────────────────────────────────────
    op.create_table(
        "paper_fingerprints",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("file_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("shared_paper_id", PortableUUID, sa.ForeignKey("shared_historical_papers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("times_seen", sa.Integer(), server_default="1", nullable=False),
    )
    op.create_index("ix_paper_fingerprints_file_hash", "paper_fingerprints", ["file_hash"], unique=True)

    # ── 9. question_fingerprints ───────────────────────────────────────
    op.create_table(
        "question_fingerprints",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("canonical_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("shared_question_id", PortableUUID, sa.ForeignKey("shared_verified_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_question_fingerprints_canonical_hash", "question_fingerprints", ["canonical_hash"], unique=True)

    # ── 10. duplicate_detection_records ────────────────────────────────
    op.create_table(
        "duplicate_detection_records",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("source_id", PortableUUID, nullable=False),
        sa.Column("target_id", PortableUUID, nullable=True),
        sa.Column("detection_level", sa.String(32), nullable=False),
        sa.Column("similarity_score", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("match_metadata", PortableJSON, nullable=True),
        sa.Column("action_taken", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_duplicate_detection_records_source_id", "duplicate_detection_records", ["source_id"])
    op.create_index("ix_duplicate_detection_records_target_id", "duplicate_detection_records", ["target_id"])

    # ── 11. question_similarity_reviews ────────────────────────────────
    op.create_table(
        "question_similarity_reviews",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("candidate_question_id", PortableUUID, nullable=False),
        sa.Column("existing_shared_question_id", PortableUUID, sa.ForeignKey("shared_verified_questions.id", ondelete="CASCADE"), nullable=True),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), server_default="pending", nullable=False),
        sa.Column("reviewed_by", sa.String(128), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_question_similarity_reviews_candidate", "question_similarity_reviews", ["candidate_question_id"])

    # ── 12. review_queue ───────────────────────────────────────────────
    op.create_table(
        "review_queue",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", PortableUUID, nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(16), server_default="medium", nullable=False),
        sa.Column("status", sa.String(32), server_default="pending", nullable=False),
        sa.Column("assigned_to", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_review_queue_entity_id", "review_queue", ["entity_id"])

    # ── 13. user_upload_permissions ────────────────────────────────────
    op.create_table(
        "user_upload_permissions",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paper_id", PortableUUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("allow_sharing", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("terms_accepted", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("legal_eligibility_confirmed", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_upload_permissions_user_id", "user_upload_permissions", ["user_id"])
    op.create_index("ix_user_upload_permissions_paper_id", "user_upload_permissions", ["paper_id"])

    # ── 14. user_processing_history ────────────────────────────────────
    op.create_table(
        "user_processing_history",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("user_id", PortableUUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paper_id", PortableUUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("details", PortableJSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_processing_history_user_id", "user_processing_history", ["user_id"])
    op.create_index("ix_user_processing_history_paper_id", "user_processing_history", ["paper_id"])

    # ── 15. topic_frequency_statistics ─────────────────────────────────
    op.create_table(
        "topic_frequency_statistics",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("section", sa.String(16), nullable=False),
        sa.Column("topic", sa.String(128), nullable=False),
        sa.Column("subtopic", sa.String(128), nullable=True),
        sa.Column("total_occurrences", sa.Integer(), server_default="0", nullable=False),
        sa.Column("recent_occurrences", sa.Integer(), server_default="0", nullable=False),
        sa.Column("frequency_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("recency_weighted_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("last_calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("section", "topic", "subtopic", name="uq_topic_freq_sec_topic_sub"),
    )
    op.create_index("ix_topic_frequency_statistics_section", "topic_frequency_statistics", ["section"])
    op.create_index("ix_topic_frequency_statistics_topic", "topic_frequency_statistics", ["topic"])

    # ── 16. yearly_trends ──────────────────────────────────────────────
    op.create_table(
        "yearly_trends",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(16), nullable=False),
        sa.Column("total_questions", sa.Integer(), server_default="0", nullable=False),
        sa.Column("mcq_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("tita_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("easy_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("medium_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("hard_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("year", "section", name="uq_yearly_trend_year_section"),
    )
    op.create_index("ix_yearly_trends_year", "yearly_trends", ["year"])
    op.create_index("ix_yearly_trends_section", "yearly_trends", ["section"])

    # ── 17. difficulty_statistics ──────────────────────────────────────
    op.create_table(
        "difficulty_statistics",
        sa.Column("id", PortableUUID, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("section", sa.String(16), nullable=False),
        sa.Column("difficulty", sa.String(16), nullable=False),
        sa.Column("count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("percentage", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("last_calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("section", "difficulty", name="uq_diff_stat_section_diff"),
    )
    op.create_index("ix_difficulty_statistics_section", "difficulty_statistics", ["section"])

    # ── 18. Add columns to papers table ────────────────────────────────
    with op.batch_alter_table("papers") as batch_op:
        batch_op.add_column(sa.Column("allow_sharing", sa.Boolean(), server_default="true", nullable=False))
        batch_op.add_column(sa.Column("sharing_status", sa.String(32), server_default="pending", nullable=False))
        batch_op.add_column(sa.Column("error_details", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("is_duplicate", sa.Boolean(), server_default="false", nullable=False))
        batch_op.add_column(sa.Column("duplicate_of_id", PortableUUID, nullable=True))
        batch_op.add_column(sa.Column("shared_paper_id", PortableUUID, nullable=True))

    # ── 19. Add columns to questions table ─────────────────────────────
    with op.batch_alter_table("questions") as batch_op:
        batch_op.add_column(sa.Column("canonical_hash", sa.String(64), nullable=True))
        batch_op.add_column(sa.Column("shared_question_id", PortableUUID, nullable=True))
        batch_op.add_column(sa.Column("rejection_reason", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("dataset_text", sa.Text(), nullable=True))
        batch_op.create_index("ix_questions_canonical_hash", ["canonical_hash"])


def downgrade() -> None:
    with op.batch_alter_table("questions") as batch_op:
        batch_op.drop_index("ix_questions_canonical_hash")
        batch_op.drop_column("dataset_text")
        batch_op.drop_column("rejection_reason")
        batch_op.drop_column("shared_question_id")
        batch_op.drop_column("canonical_hash")

    with op.batch_alter_table("papers") as batch_op:
        batch_op.drop_column("shared_paper_id")
        batch_op.drop_column("duplicate_of_id")
        batch_op.drop_column("is_duplicate")
        batch_op.drop_column("error_details")
        batch_op.drop_column("sharing_status")
        batch_op.drop_column("allow_sharing")

    op.drop_table("difficulty_statistics")
    op.drop_table("yearly_trends")
    op.drop_table("topic_frequency_statistics")
    op.drop_table("user_processing_history")
    op.drop_table("user_upload_permissions")
    op.drop_table("review_queue")
    op.drop_table("question_similarity_reviews")
    op.drop_table("duplicate_detection_records")
    op.drop_table("question_fingerprints")
    op.drop_table("paper_fingerprints")
    op.drop_table("shared_question_topics")
    op.drop_table("shared_question_sources")
    op.drop_table("shared_solutions")
    op.drop_table("shared_answer_keys")
    op.drop_table("shared_question_options")
    op.drop_table("shared_verified_questions")
    op.drop_table("shared_historical_papers")
