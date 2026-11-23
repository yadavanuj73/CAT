"""
Three-Level Deduplication Engine for CAT Intelligence 2026.

Level 1: Exact PDF Duplicate Detection (SHA-256 file fingerprint)
Level 2: Canonical Question Normalization & Fingerprinting (SHA-256 canonical hash with DB UNIQUE constraint)
Level 3: Semantic Duplicate Detection & Review Queue (Lexical/numerical/option comparison with safe review flagging)

Enforces database-level uniqueness, atomic source linking, and non-destructive merging.
"""

import difflib
import hashlib
import re
import unicodedata
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deduplication import (
    DuplicateDetectionRecord,
    PaperFingerprint,
    QuestionFingerprint,
    QuestionSimilarityReview,
    ReviewQueue,
)
from app.models.shared_corpus import (
    SharedHistoricalPaper,
    SharedQuestionSource,
    SharedVerifiedQuestion,
)

# Regex patterns for normalization
HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
HYPHENATED_LINEBREAK_RE = re.compile(r"(\w+)-\s*\n\s*(\w+)")
PAGE_NUMBER_RE = re.compile(r"(?:page\s*\d+(?:\s*of\s*\d+)?|\bcat\s*\d{4}\s*(?:slot\s*\d+)?\b)", re.IGNORECASE)
NUMBER_EXTRACT_RE = re.compile(r"(?<![a-zA-Z_])[-+]?\b\d+(?:\.\d+)?\b(?![a-zA-Z_])")

# Mathematical symbol standardizations
MATH_REPLACEMENTS = {
    "×": "*",
    "÷": "/",
    "−": "-",
    "—": "-",
    "–": "-",
    "≤": "<=",
    "≥": ">=",
    "≠": "!=",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "²": "^2",
    "³": "^3",
}


def normalize_canonical_text(text: str) -> str:
    """
    Transform raw extracted text into canonical representation:
    - Unicode NFKC normalization
    - Math & typographical character standardization
    - Removal of HTML formatting and page artifact tokens
    - De-hyphenation across line-breaks
    - Case folding and whitespace collapsing
    """
    if not text:
        return ""

    # 1. Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", text)

    # 2. Mathematical symbol replacement
    for orig, repl in MATH_REPLACEMENTS.items():
        text = text.replace(orig, repl)

    # 3. Strip HTML tags
    text = HTML_TAG_RE.sub(" ", text)

    # 4. De-hyphenate words broken by line-breaks (e.g. "com-\nputation" -> "computation")
    text = HYPHENATED_LINEBREAK_RE.sub(r"\1\2", text)

    # 5. Remove common PDF header/footer artifacts
    text = PAGE_NUMBER_RE.sub(" ", text)

    # 6. Lowercase & collapse all consecutive whitespaces
    text = text.lower()
    text = WHITESPACE_RE.sub(" ", text).strip()

    return text


def extract_numerical_tokens(text: str) -> List[float]:
    """Extract ordered list of floating point values from text for numerical comparison."""
    tokens = NUMBER_EXTRACT_RE.findall(text)
    nums = []
    for t in tokens:
        try:
            nums.append(float(t))
        except ValueError:
            pass
    return nums


def compute_canonical_question_representation(
    question_text: str,
    question_type: str,
    section: str,
    options: Optional[List[Dict[str, Any]]] = None,
    dataset_text: Optional[str] = None,
    passage_text: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Generate stable canonical representation and SHA-256 fingerprint.
    Returns: (canonical_hash, canonical_text)
    """
    norm_q = normalize_canonical_text(question_text)
    norm_type = (question_type or "MCQ").upper().strip()
    norm_sec = (section or "QA").upper().strip()

    # Normalize options deterministically (sorted by normalized option text)
    norm_opts = ""
    if options and norm_type == "MCQ":
        opt_texts = []
        for opt in options:
            t = normalize_canonical_text(opt.get("text", opt.get("option_text", "")))
            if t:
                opt_texts.append(t)
        opt_texts.sort()
        norm_opts = "|".join(opt_texts)

    norm_passage = normalize_canonical_text(passage_text or "")
    norm_dataset = normalize_canonical_text(dataset_text or "")

    canonical_repr = (
        f"SEC:{norm_sec}#"
        f"TYPE:{norm_type}#"
        f"Q:{norm_q}#"
        f"OPTS:{norm_opts}#"
        f"PASS:{norm_passage}#"
        f"DATA:{norm_dataset}"
    )

    canonical_hash = hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()
    return canonical_hash, canonical_repr


# ─── Level 1: Exact PDF Duplicate Detection ───────────────────────────────────

async def check_exact_paper_duplicate(
    db: AsyncSession,
    file_hash: str,
) -> Optional[SharedHistoricalPaper]:
    """
    Check if an identical PDF has already been processed into the shared bank.
    Returns existing SharedHistoricalPaper if found, else None.
    """
    # 1. Check paper_fingerprints
    fp_stmt = select(PaperFingerprint).where(PaperFingerprint.file_hash == file_hash)
    fp_res = await db.execute(fp_stmt)
    fp = fp_res.scalar_one_or_none()

    if fp and fp.shared_paper_id:
        paper_stmt = select(SharedHistoricalPaper).where(SharedHistoricalPaper.id == fp.shared_paper_id)
        paper_res = await db.execute(paper_stmt)
        return paper_res.scalar_one_or_none()

    # 2. Check shared_historical_papers directly
    p_stmt = select(SharedHistoricalPaper).where(SharedHistoricalPaper.file_fingerprint == file_hash)
    p_res = await db.execute(p_stmt)
    return p_res.scalar_one_or_none()


async def register_paper_fingerprint(
    db: AsyncSession,
    file_hash: str,
    shared_paper_id: Optional[uuid.UUID] = None,
) -> PaperFingerprint:
    """Register or update an exact PDF fingerprint."""
    stmt = select(PaperFingerprint).where(PaperFingerprint.file_hash == file_hash)
    res = await db.execute(stmt)
    fp = res.scalar_one_or_none()

    if fp:
        fp.times_seen += 1
        if shared_paper_id and not fp.shared_paper_id:
            fp.shared_paper_id = shared_paper_id
        await db.commit()
        return fp

    new_fp = PaperFingerprint(
        file_hash=file_hash,
        shared_paper_id=shared_paper_id,
        times_seen=1,
    )
    db.add(new_fp)
    try:
        await db.commit()
        await db.refresh(new_fp)
        return new_fp
    except IntegrityError:
        await db.rollback()
        res = await db.execute(stmt)
        return res.scalar_one()


# ─── Level 2: Exact Question Canonical Duplicate Detection ────────────────────

async def check_exact_question_duplicate(
    db: AsyncSession,
    canonical_hash: str,
) -> Optional[SharedVerifiedQuestion]:
    """
    Level 2 Check: Query shared question bank for identical canonical hash.
    Enforces DB-level uniqueness constraint.
    """
    stmt = select(SharedVerifiedQuestion).where(SharedVerifiedQuestion.canonical_hash == canonical_hash)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


# ─── Level 3: Semantic Duplicate Detection & Review ───────────────────────────

def compute_text_similarity(a: str, b: str) -> float:
    """Compute lexical token similarity between two strings using SequenceMatcher."""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def token_set_jaccard_similarity(a: str, b: str) -> float:
    """Compute token Jaccard similarity for word overlap."""
    tokens_a = set(WHITESPACE_RE.split(a))
    tokens_b = set(WHITESPACE_RE.split(b))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(intersection) / len(union)


async def check_semantic_similarity(
    db: AsyncSession,
    candidate_text: str,
    section: str,
    threshold: float = 0.82,
) -> List[Tuple[SharedVerifiedQuestion, float, str]]:
    """
    Level 3 Detection: Compare candidate question with existing shared questions
    in the same section.
    Flags candidates for review if similarity is high but canonical hashes differ.
    Never auto-merges semantic candidates.
    """
    norm_candidate = normalize_canonical_text(candidate_text)
    candidate_nums = extract_numerical_tokens(norm_candidate)

    # Query existing shared questions in the same section
    stmt = select(SharedVerifiedQuestion).where(SharedVerifiedQuestion.section == section)
    res = await db.execute(stmt)
    existing_questions = res.scalars().all()

    matches = []
    for eq in existing_questions:
        norm_eq = normalize_canonical_text(eq.question_text)
        sim = compute_text_similarity(norm_candidate, norm_eq)
        jaccard = token_set_jaccard_similarity(norm_candidate, norm_eq)
        combined_score = (sim * 0.6) + (jaccard * 0.4)

        if combined_score >= threshold:
            eq_nums = extract_numerical_tokens(norm_eq)
            # Check numerical equivalence
            if candidate_nums != eq_nums:
                reason = (
                    f"High text similarity ({combined_score:.2f}) but differing numerical values. "
                    f"Candidate nums: {candidate_nums[:5]}, Existing nums: {eq_nums[:5]}. May be distinct problem."
                )
            else:
                reason = (
                    f"Potential identical question with OCR/layout variations ({combined_score:.2f}). "
                    f"Identical numerical values detected."
                )
            matches.append((eq, round(combined_score, 4), reason))

    # Sort descending by similarity score
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


async def flag_for_similarity_review(
    db: AsyncSession,
    candidate_question_id: uuid.UUID,
    existing_shared_question_id: uuid.UUID,
    similarity_score: float,
    reason: str,
) -> QuestionSimilarityReview:
    """Create a record in question_similarity_reviews and review_queue."""
    review = QuestionSimilarityReview(
        candidate_question_id=candidate_question_id,
        existing_shared_question_id=existing_shared_question_id,
        similarity_score=similarity_score,
        reason=reason,
        status="pending",
    )
    db.add(review)

    queue_item = ReviewQueue(
        entity_type="similarity",
        entity_id=candidate_question_id,
        reason=reason,
        severity="medium" if similarity_score < 0.90 else "high",
        status="pending",
    )
    db.add(queue_item)

    # Record duplicate detection record
    dup_record = DuplicateDetectionRecord(
        entity_type="question",
        source_id=candidate_question_id,
        target_id=existing_shared_question_id,
        detection_level="semantic",
        similarity_score=similarity_score,
        match_metadata={"reason": reason},
        action_taken="needs_review",
    )
    db.add(dup_record)
    await db.commit()
    await db.refresh(review)
    return review


# ─── Multi-Source Mapping Without Duplication ─────────────────────────────────

async def link_question_source(
    db: AsyncSession,
    shared_question_id: uuid.UUID,
    year: int,
    slot: Optional[str] = None,
    question_number: Optional[int] = None,
    source_name: Optional[str] = None,
    source_type: str = "official",
    shared_paper_id: Optional[uuid.UUID] = None,
    provenance_notes: Optional[str] = None,
) -> SharedQuestionSource:
    """
    Add a verified examination appearance source to an existing shared question.
    Ensures a single question can link to multiple exams (e.g., CAT 2018 Slot 1 and CAT 2020 Slot 2)
    without creating a duplicate question record.
    """
    # Check if exact source relation already exists
    stmt = select(SharedQuestionSource).where(
        SharedQuestionSource.shared_question_id == shared_question_id,
        SharedQuestionSource.year == year,
        SharedQuestionSource.slot == slot,
        SharedQuestionSource.question_number == question_number,
    )
    res = await db.execute(stmt)
    existing_src = res.scalar_one_or_none()
    if existing_src:
        return existing_src

    new_source = SharedQuestionSource(
        shared_question_id=shared_question_id,
        shared_paper_id=shared_paper_id,
        year=year,
        slot=slot,
        question_number=question_number,
        source_name=source_name or "CAT Authentic",
        source_type=source_type,
        provenance_notes=provenance_notes,
    )
    db.add(new_source)
    try:
        await db.commit()
        await db.refresh(new_source)
        return new_source
    except IntegrityError:
        await db.rollback()
        res = await db.execute(stmt)
        return res.scalar_one()
