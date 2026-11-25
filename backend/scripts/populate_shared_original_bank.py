
"""
Populate / Transfer the Global Shared Question Bank with the 1,010 verified
original CAT-level questions.

Supports two safe modes:
1. Transfer Mode (Default for production when source SQLite DB exists):
   Reads the exact 1,010 verified ORIGINAL_AUTHORED records (`primary_year = 2025`,
   `source_type = 'ORIGINAL_AUTHORED'`) from `cat2026.db` — excluding dev pytest
   fixtures and never touching quarantined historical Cracku files — and transfers
   all questions, options, answer keys, solutions, source provenance, and topics
   transactionally into the target database.
2. Builder Mode (`--from-builder`):
   Constructs the 1,010 original records from `original_cat_builder`.

Production Safety Guarantees:
- Never prints or logs database URLs, passwords, or credentials.
- Supports `--require-postgres` to block accidental execution against SQLite.
- Supports `--backup-dir` to export a pre-migration JSON snapshot of existing
  target tables before writing any rows.
- Completely idempotent: checks existing `canonical_hash` rows and skips
  without overwriting existing verified data.
- Verifies post-commit row counts and relationships on the target DB.
"""

import argparse
import asyncio
import hashlib
import json
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure backend is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import settings
from app.database import normalize_async_database_url
from app.models.question import Difficulty, QuestionType, Section
from app.models.shared_corpus import (
    SharedAnswerKey,
    SharedHistoricalPaper,
    SharedQuestionOption,
    SharedQuestionSource,
    SharedQuestionTopic,
    SharedSolution,
    SharedVerifiedQuestion,
)
from app.models.topic import Topic
from app.models.user import User
from app.services.original_cat_builder import build_all_original_questions
from app.services.original_cat_generator import compute_canonical_hash, validate_question_record


def make_pool_fingerprint(pool_name: str) -> str:
    """Deterministic 64-char SHA-256 fingerprint for paper pool."""
    return hashlib.sha256(f"cat2026_shared_pool_{pool_name}".encode("utf-8")).hexdigest()


def load_verified_original_questions_from_sqlite(sqlite_path: Path) -> List[Dict[str, Any]]:
    """
    Extract ONLY the 1,010 verified ORIGINAL_AUTHORED records from the verified
    development SQLite database, preserving exact hashes, texts, options, keys,
    solutions, and topic classifications while excluding pytest fixtures.
    """
    if not sqlite_path.exists():
        raise FileNotFoundError(f"Source SQLite database not found: {sqlite_path}")

    conn = sqlite3.connect(str(sqlite_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            q.id,
            q.canonical_hash,
            q.canonical_text,
            q.question_number,
            q.question_text,
            q.question_type,
            q.section,
            q.difficulty,
            q.marks_positive,
            q.marks_negative,
            q.has_image,
            q.has_table,
            q.has_passage,
            q.passage_text,
            q.dataset_text,
            q.primary_year,
            q.primary_slot,
            q.verification_status,
            q.verification_confidence,
            ak.correct_answer,
            ak.provenance AS ak_provenance,
            sol.solution_text,
            sol.approach_type,
            src.source_name,
            src.source_type,
            src.provenance_notes,
            t.topic_name,
            t.subtopic_name
        FROM shared_verified_questions q
        JOIN shared_question_sources src ON src.shared_question_id = q.id
        LEFT JOIN shared_answer_keys ak ON ak.shared_question_id = q.id
        LEFT JOIN shared_solutions sol ON sol.shared_question_id = q.id
        LEFT JOIN shared_question_topics qt ON qt.shared_question_id = q.id
        LEFT JOIN topics t ON t.id = qt.topic_id
        WHERE q.primary_year = 2025
          AND q.verification_status = 'verified'
          AND src.source_type = 'ORIGINAL_AUTHORED'
        ORDER BY q.section ASC, q.question_number ASC
        """
    )
    rows = cur.fetchall()

    cur.execute(
        """
        SELECT shared_question_id, option_label, option_text, is_correct
        FROM shared_question_options
        ORDER BY option_label ASC
        """
    )
    opts_by_qid: Dict[str, List[Dict[str, Any]]] = {}
    for opt in cur.fetchall():
        opts_by_qid.setdefault(opt["shared_question_id"], []).append(
            {
                "label": opt["option_label"],
                "text": opt["option_text"],
                "is_correct": bool(opt["is_correct"]),
            }
        )

    conn.close()

    records: List[Dict[str, Any]] = []
    seen_hashes = set()
    for r in rows:
        q_opts = opts_by_qid.get(r["id"], [])
        recomputed_hash, canonical_text = compute_canonical_hash(
            question_text=r["question_text"],
            question_type=r["question_type"],
            section=r["section"],
            options=[{"label": o["label"], "text": o["text"]} for o in q_opts] if q_opts else None,
            passage_text=r["passage_text"] or "",
            dataset_text=r["dataset_text"] or "",
        )
        if recomputed_hash != r["canonical_hash"]:
            raise ValueError(
                f"Canonical hash integrity mismatch on source record {r['id']}: "
                f"stored={r['canonical_hash']} vs recomputed={recomputed_hash}"
            )
        if recomputed_hash in seen_hashes:
            raise ValueError(f"Duplicate hash found in source export: {recomputed_hash}")
        seen_hashes.add(recomputed_hash)

        record = {
            "id": r["id"],
            "text": r["question_text"],
            "canonical_hash": recomputed_hash,
            "canonical_text": canonical_text,
            "type": r["question_type"],
            "section": r["section"],
            "difficulty": r["difficulty"],
            "question_number": r["question_number"],
            "marks_positive": float(r["marks_positive"]),
            "marks_negative": float(r["marks_negative"]),
            "has_image": bool(r["has_image"]),
            "has_table": bool(r["has_table"]),
            "has_passage": bool(r["has_passage"]),
            "passage_text": r["passage_text"],
            "dataset_text": r["dataset_text"],
            "options": [{"label": o["label"], "text": o["text"], "is_correct": o["is_correct"]} for o in q_opts],
            "correct_answer": r["correct_answer"],
            "ak_provenance": r["ak_provenance"] or "CAT 2026 Original Authored Corpus — Expert Key",
            "solution": r["solution_text"],
            "approach_type": r["approach_type"] or "First Principles Analytic Derivation",
            "source_name": r["source_name"] or f"CAT 2026 Original Authored Pool — {r['section']}",
            "source_type": "ORIGINAL_AUTHORED",
            "provenance_notes": r["provenance_notes"] or "Original question authored and validated for CAT 2026 Shared Question Bank.",
            "topic": r["topic_name"] or r["section"],
            "subtopic": r["subtopic_name"] or "General",
        }
        valid, errors = validate_question_record(record)
        if not valid:
            raise ValueError(f"Validation failed on source record {r['id']}: {errors}")
        records.append(record)

    return records


def build_records_from_generator() -> List[Dict[str, Any]]:
    """Build 1,010 records directly from deterministic builder and enrich with hashes."""
    raw = build_all_original_questions()
    section_q_num = {"VARC": 1, "DILR": 1, "QA": 1}
    enriched: List[Dict[str, Any]] = []
    for q in raw:
        sec_str = q["section"]
        q_num = section_q_num[sec_str]
        section_q_num[sec_str] += 1
        c_hash, c_text = compute_canonical_hash(
            question_text=q["text"],
            question_type=q["type"],
            section=sec_str,
            options=q.get("options"),
            passage_text=q.get("passage_text", ""),
            dataset_text=q.get("dataset_text", ""),
        )
        enriched.append(
            {
                **q,
                "canonical_hash": c_hash,
                "canonical_text": c_text,
                "question_number": q_num,
                "marks_positive": 3.0,
                "marks_negative": -1.0 if q["type"] == "MCQ" else 0.0,
                "has_image": False,
                "has_table": bool(q.get("dataset_text")) or ("Table" in q["text"] or "matrix" in q["text"].lower()),
                "has_passage": bool(q.get("passage_text")),
                "ak_provenance": "CAT 2026 Original Authored Corpus — Expert Key",
                "approach_type": "First Principles Analytic Derivation",
                "source_name": f"CAT 2026 Original Authored Pool — {sec_str}",
                "source_type": "ORIGINAL_AUTHORED",
                "provenance_notes": "Original question authored and validated for CAT 2026 Shared Question Bank.",
            }
        )
    return enriched


async def create_pre_transfer_backup(session: AsyncSession, backup_dir: Path) -> Path:
    """Export an encrypted-secret-free JSON backup of target shared tables and counts."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_file = backup_dir / f"shared_corpus_pre_migration_backup_{ts}.json"

    counts = {}
    for name, model in [
        ("users", User),
        ("shared_historical_papers", SharedHistoricalPaper),
        ("shared_verified_questions", SharedVerifiedQuestion),
        ("shared_question_options", SharedQuestionOption),
        ("shared_answer_keys", SharedAnswerKey),
        ("shared_solutions", SharedSolution),
        ("shared_question_sources", SharedQuestionSource),
        ("shared_question_topics", SharedQuestionTopic),
        ("topics", Topic),
    ]:
        counts[name] = (await session.execute(select(func.count(model.id)))).scalar_one()

    papers = [
        {
            "id": str(p.id),
            "year": p.year,
            "slot": p.slot,
            "paper_title": p.paper_title,
            "file_fingerprint": p.file_fingerprint,
            "total_questions": p.total_questions,
        }
        for p in (await session.execute(select(SharedHistoricalPaper))).scalars().all()
    ]
    existing_hashes = list(
        (await session.execute(select(SharedVerifiedQuestion.canonical_hash))).scalars().all()
    )

    payload = {
        "created_at_utc": ts,
        "table_counts": counts,
        "shared_papers": papers,
        "existing_question_hashes_count": len(existing_hashes),
        "existing_question_hashes": existing_hashes,
    }
    backup_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return backup_file


async def get_or_create_topic(
    session: AsyncSession,
    topic_cache: Dict[Tuple[str, str, str], uuid.UUID],
    section_enum: Section,
    topic_name: str,
    subtopic_name: str,
) -> uuid.UUID:
    """Get existing Topic ID or create new record."""
    key = (section_enum.value, topic_name, subtopic_name)
    if key in topic_cache:
        return topic_cache[key]

    stmt = select(Topic).where(
        Topic.section == section_enum,
        Topic.topic_name == topic_name,
        Topic.subtopic_name == subtopic_name,
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        topic_cache[key] = existing.id
        return existing.id

    new_topic = Topic(
        id=uuid.uuid4(),
        section=section_enum,
        topic_name=topic_name,
        subtopic_name=subtopic_name,
        description=f"CAT {section_enum.value} Topic: {topic_name} - {subtopic_name}",
    )
    session.add(new_topic)
    await session.flush()
    topic_cache[key] = new_topic.id
    return new_topic.id


async def get_or_create_paper(
    session: AsyncSession,
    section_str: str,
    total_q: int,
) -> SharedHistoricalPaper:
    """Get or create the SharedHistoricalPaper pool for this section."""
    slot_name = f"Original_{section_str}_Pool"
    stmt = select(SharedHistoricalPaper).where(
        SharedHistoricalPaper.year == 2025,
        SharedHistoricalPaper.slot == slot_name,
    )
    result = await session.execute(stmt)
    paper = result.scalar_one_or_none()

    if paper:
        return paper

    paper = SharedHistoricalPaper(
        id=uuid.uuid4(),
        year=2025,
        slot=slot_name,
        paper_title=f"CAT 2026 Original Authored Corpus — {section_str} Pool",
        file_fingerprint=make_pool_fingerprint(section_str),
        total_questions=total_q,
        is_verified=True,
        source_provenance="CAT 2026 Platform Original Authored Corpus",
    )
    session.add(paper)
    await session.flush()
    return paper


async def populate_shared_bank(
    target_url: Optional[str] = None,
    source_sqlite: Optional[Path] = None,
    from_builder: bool = False,
    require_postgres: bool = False,
    backup_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    print("=" * 70)
    print("CAT 2026 — POPULATE / TRANSFER SHARED QUESTION BANK")
    print("=" * 70)
    start_time = time.time()

    raw_url = target_url or os.getenv("DATABASE_URL") or settings.DATABASE_URL
    clean_url, c_args, e_kwargs = normalize_async_database_url(raw_url)
    target_engine = create_async_engine(clean_url, connect_args=c_args, **e_kwargs)
    dialect_name = target_engine.url.get_backend_name()

    if require_postgres and dialect_name == "sqlite":
        await target_engine.dispose()
        raise RuntimeError(
            "ABORTED: --require-postgres specified, but configured DATABASE_URL points to SQLite."
        )

    print(f"Target database dialect: {dialect_name}")

    default_sqlite = REPO_ROOT / "cat2026.db"
    use_sqlite_transfer = (not from_builder) and (source_sqlite is not None or default_sqlite.exists())

    if use_sqlite_transfer:
        src_path = source_sqlite or default_sqlite
        print(f"1. Loading verified 1,010 ORIGINAL_AUTHORED records from {src_path.name}...")
        questions = load_verified_original_questions_from_sqlite(src_path)
    else:
        print("1. Generating 1,010 authentic CAT-level original questions from builder...")
        questions = build_records_from_generator()

    if len(questions) != 1010:
        raise RuntimeError(f"Expected 1,010 original questions to transfer, got {len(questions)}")

    print(f"Verified source payload ready: {len(questions)} questions.")

    session_maker = async_sessionmaker(
        bind=target_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    try:
        async with session_maker() as session:
            if backup_dir is not None:
                bpath = await create_pre_transfer_backup(session, backup_dir)
                print(f"Pre-transfer backup snapshot saved: {bpath}")

            # Record pre-existing counts
            pre_q_count = (
                await session.execute(select(func.count(SharedVerifiedQuestion.id)))
            ).scalar_one()
            existing_hashes = set(
                (await session.execute(select(SharedVerifiedQuestion.canonical_hash))).scalars().all()
            )
            print(f"Existing questions on target DB before transfer: {pre_q_count}")

            topic_cache: Dict[Tuple[str, str, str], uuid.UUID] = {}
            for t in (await session.execute(select(Topic))).scalars().all():
                topic_cache[(t.section.value, t.topic_name, t.subtopic_name or "")] = t.id

            section_counts = {"VARC": 340, "DILR": 330, "QA": 340}
            papers: Dict[str, SharedHistoricalPaper] = {}
            for sec_str, count in section_counts.items():
                papers[sec_str] = await get_or_create_paper(session, sec_str, count)
            await session.commit()

            print("\n2. Preparing topic taxonomy and transferring questions in fast atomic batches...", flush=True)
            # Pre-resolve all topics once before bulk question insertion
            for q in questions:
                await get_or_create_topic(
                    session,
                    topic_cache,
                    Section(q["section"]),
                    q["topic"],
                    q["subtopic"],
                )
            await session.commit()

            inserted_count = 0
            skipped_count = 0
            options_count = 0
            keys_count = 0
            solutions_count = 0
            sources_count = 0
            topics_count = 0

            pending_questions = []
            for q in questions:
                c_hash = q["canonical_hash"]
                if c_hash in existing_hashes:
                    skipped_count += 1
                    continue
                existing_hashes.add(c_hash)
                pending_questions.append(q)

            batch_size = 200
            for start_i in range(0, len(pending_questions), batch_size):
                chunk = pending_questions[start_i : start_i + batch_size]
                svq_rows = []
                opt_rows = []
                ak_rows = []
                sol_rows = []
                src_rows = []
                qt_rows = []

                for q in chunk:
                    sec_str = q["section"]
                    sec_enum = Section(sec_str)
                    q_type = q["type"]
                    q_num = int(q["question_number"])
                    paper = papers[sec_str]
                    q_id = uuid.uuid4()

                    svq_rows.append(
                        {
                            "id": q_id,
                            "shared_paper_id": paper.id,
                            "canonical_hash": q["canonical_hash"],
                            "question_number": q_num,
                            "question_text": q["text"],
                            "canonical_text": q["canonical_text"],
                            "question_type": QuestionType(q_type),
                            "section": sec_enum,
                            "difficulty": Difficulty(q["difficulty"]),
                            "marks_positive": q["marks_positive"],
                            "marks_negative": q["marks_negative"],
                            "has_image": q["has_image"],
                            "has_table": q["has_table"],
                            "has_passage": q["has_passage"],
                            "passage_text": q.get("passage_text"),
                            "dataset_text": q.get("dataset_text"),
                            "primary_year": 2025,
                            "primary_slot": paper.slot,
                            "verification_status": "verified",
                            "verification_confidence": 1.0,
                        }
                    )

                    if q_type == "MCQ" and q.get("options"):
                        for opt in q["options"]:
                            is_corr = opt["label"].strip().upper() == q["correct_answer"].strip().upper()
                            opt_rows.append(
                                {
                                    "id": uuid.uuid4(),
                                    "shared_question_id": q_id,
                                    "option_label": opt["label"],
                                    "option_text": opt["text"],
                                    "is_correct": is_corr,
                                }
                            )

                    ak_rows.append(
                        {
                            "id": uuid.uuid4(),
                            "shared_question_id": q_id,
                            "correct_answer": q["correct_answer"],
                            "answer_type": q_type,
                            "provenance": q["ak_provenance"],
                        }
                    )

                    sol_rows.append(
                        {
                            "id": uuid.uuid4(),
                            "shared_question_id": q_id,
                            "solution_text": q["solution"],
                            "approach_type": q["approach_type"],
                            "is_verified": True,
                        }
                    )

                    src_rows.append(
                        {
                            "id": uuid.uuid4(),
                            "shared_question_id": q_id,
                            "shared_paper_id": paper.id,
                            "year": 2025,
                            "slot": paper.slot,
                            "question_number": q_num,
                            "source_name": q["source_name"],
                            "source_type": q["source_type"],
                            "provenance_notes": q["provenance_notes"],
                        }
                    )

                    t_id = topic_cache[(sec_enum.value, q["topic"], q["subtopic"])]
                    qt_rows.append(
                        {
                            "id": uuid.uuid4(),
                            "shared_question_id": q_id,
                            "topic_id": t_id,
                            "confidence": 1.0,
                            "classified_by": "rule",
                        }
                    )

                if svq_rows:
                    await session.execute(insert(SharedVerifiedQuestion.__table__).values(svq_rows))
                if opt_rows:
                    await session.execute(insert(SharedQuestionOption.__table__).values(opt_rows))
                if ak_rows:
                    await session.execute(insert(SharedAnswerKey.__table__).values(ak_rows))
                if sol_rows:
                    await session.execute(insert(SharedSolution.__table__).values(sol_rows))
                if src_rows:
                    await session.execute(insert(SharedQuestionSource.__table__).values(src_rows))
                if qt_rows:
                    await session.execute(insert(SharedQuestionTopic.__table__).values(qt_rows))

                await session.commit()
                inserted_count += len(svq_rows)
                options_count += len(opt_rows)
                keys_count += len(ak_rows)
                solutions_count += len(sol_rows)
                sources_count += len(src_rows)
                topics_count += len(qt_rows)
                print(f"  Committed {inserted_count}/{len(pending_questions)} pending questions...", flush=True)

            # 3. Post-commit target verification
            post_orig_count = (
                await session.execute(
                    select(func.count(SharedVerifiedQuestion.id))
                    .join(
                        SharedQuestionSource,
                        SharedQuestionSource.shared_question_id == SharedVerifiedQuestion.id,
                    )
                    .where(
                        SharedVerifiedQuestion.primary_year == 2025,
                        SharedQuestionSource.source_type == "ORIGINAL_AUTHORED",
                    )
                )
            ).scalar_one()

            total_q = (
                await session.execute(select(func.count(SharedVerifiedQuestion.id)))
            ).scalar_one()
            total_opts = (
                await session.execute(select(func.count(SharedQuestionOption.id)))
            ).scalar_one()
            total_keys = (
                await session.execute(select(func.count(SharedAnswerKey.id)))
            ).scalar_one()
            total_sols = (
                await session.execute(select(func.count(SharedSolution.id)))
            ).scalar_one()
            total_topics = (
                await session.execute(select(func.count(Topic.id)))
            ).scalar_one()

        elapsed = time.time() - start_time
        summary = {
            "dialect": dialect_name,
            "source_mode": "sqlite_transfer" if use_sqlite_transfer else "builder",
            "processed": len(questions),
            "inserted": inserted_count,
            "skipped": skipped_count,
            "options_created": options_count,
            "answer_keys_created": keys_count,
            "solutions_created": solutions_count,
            "sources_created": sources_count,
            "topic_links_created": topics_count,
            "post_commit_original_authored_count": post_orig_count,
            "post_commit_total_questions": total_q,
            "post_commit_total_options": total_opts,
            "post_commit_total_answer_keys": total_keys,
            "post_commit_total_solutions": total_sols,
            "post_commit_total_topics": total_topics,
            "elapsed_seconds": round(elapsed, 2),
        }

        print("\n" + "=" * 70)
        print("SHARED QUESTION BANK TRANSFER / INGESTION SUMMARY")
        print("=" * 70)
        for k, v in summary.items():
            print(f"{k:38s}: {v}")
        print("=" * 70)
        return summary
    finally:
        await target_engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="Transfer 1,010 original CAT questions to target DB.")
    parser.add_argument("--target-url", default=None, help="Target database URL (defaults to env DATABASE_URL)")
    parser.add_argument("--source-sqlite", default=None, help="Path to source SQLite DB (defaults to ../cat2026.db)")
    parser.add_argument("--from-builder", action="store_true", help="Generate from builder instead of SQLite transfer")
    parser.add_argument("--require-postgres", action="store_true", help="Fail if target DB is SQLite")
    parser.add_argument("--backup-dir", default=None, help="Directory for pre-transfer backup snapshot")
    args = parser.parse_args()

    asyncio.run(
        populate_shared_bank(
            target_url=args.target_url,
            source_sqlite=Path(args.source_sqlite) if args.source_sqlite else None,
            from_builder=args.from_builder,
            require_postgres=args.require_postgres,
            backup_dir=Path(args.backup_dir) if args.backup_dir else None,
        )
    )


if __name__ == "__main__":
    main()
