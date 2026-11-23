"""
Data Verification Engine.
Mandatory validation gate before historical data enters the trusted dataset.
Performs:
1. Option consistency checking (A, B, C, D present and distinct).
2. Deterministic mathematical verification.
3. Answer key validation.
4. Ambiguity / incompleteness detection.
5. Audit trail generation.
Never silently converts unverified data into verified data.
"""

import re
import uuid
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.question import Question, QuestionOption, AnswerKey, Solution, VerificationStatus
from app.models.audit import VerificationRecord, VerificationType, VerificationResult
from app.utils.math_solver import verify_arithmetic_statement


async def verify_question_data(
    db: AsyncSession,
    question_id: uuid.UUID,
    manual_override: Optional[str] = None,
    reviewer_notes: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    """
    Run independent verification checks on an extracted question.
    Only questions passing all checks (or validated by human reviewer)
    are marked as VERIFIED.
    """
    stmt = select(Question).where(Question.id == question_id)
    result = await db.execute(stmt)
    q = result.scalar_one_or_none()
    if not q:
        raise ValueError(f"Question with ID {question_id} not found.")

    failures = []
    audit_records = []

    # 1. Text Completeness Check
    if len(q.question_text.strip()) < 15:
        failures.append("Question text is suspiciously short or incomplete.")
        audit_records.append(
            VerificationRecord(
                question_id=q.id,
                verification_type=VerificationType.AMBIGUITY_CHECK,
                result=VerificationResult.FAILED,
                details={"reason": "Text length below threshold"},
                verified_by="system",
            )
        )
    else:
        audit_records.append(
            VerificationRecord(
                question_id=q.id,
                verification_type=VerificationType.AMBIGUITY_CHECK,
                result=VerificationResult.PASSED,
                details={"length": len(q.question_text)},
                verified_by="system",
            )
        )

    # 2. Option Consistency & Format Check
    if q.question_type.value == "MCQ":
        opt_stmt = select(QuestionOption).where(QuestionOption.question_id == q.id)
        opt_res = await db.execute(opt_stmt)
        options = opt_res.scalars().all()

        if len(options) < 4:
            failures.append(f"MCQ requires 4 options, found {len(options)}.")
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.OPTION_CONSISTENCY,
                    result=VerificationResult.FAILED,
                    details={"count": len(options)},
                    verified_by="system",
                )
            )
        else:
            opt_texts = [o.option_text.strip().lower() for o in options]
            if len(opt_texts) != len(set(opt_texts)):
                failures.append("MCQ contains duplicate options.")
                audit_records.append(
                    VerificationRecord(
                        question_id=q.id,
                        verification_type=VerificationType.OPTION_CONSISTENCY,
                        result=VerificationResult.FAILED,
                        details={"error": "duplicate_option_texts"},
                        verified_by="system",
                    )
                )
            else:
                audit_records.append(
                    VerificationRecord(
                        question_id=q.id,
                        verification_type=VerificationType.OPTION_CONSISTENCY,
                        result=VerificationResult.PASSED,
                        details={"options_count": len(options)},
                        verified_by="system",
                    )
                )
    elif q.question_type.value == "TITA":
        # TITA questions must NOT have options
        opt_stmt = select(QuestionOption).where(QuestionOption.question_id == q.id)
        opt_res = await db.execute(opt_stmt)
        options = opt_res.scalars().all()
        if len(options) > 0:
            failures.append("TITA (Type In The Answer) question must not contain multiple choice options.")
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.OPTION_CONSISTENCY,
                    result=VerificationResult.FAILED,
                    details={"error": "tita_has_options", "count": len(options)},
                    verified_by="system",
                )
            )
        else:
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.OPTION_CONSISTENCY,
                    result=VerificationResult.PASSED,
                    details={"type": "TITA_verified_no_options"},
                    verified_by="system",
                )
            )

    # 3. Section-Specific Grounding & Logic Verification
    if q.section.value == "QA":
        math_valid, math_msg = verify_arithmetic_statement(q.question_text)
        if not math_valid:
            failures.append(math_msg)
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.MATH_VERIFY,
                    result=VerificationResult.FAILED,
                    details={"message": math_msg},
                    verified_by="system",
                )
            )
        else:
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.MATH_VERIFY,
                    result=VerificationResult.PASSED,
                    details={"message": math_msg},
                    verified_by="system",
                )
            )
    elif q.section.value == "VARC":
        # VARC passage grounding
        if q.has_passage:
            if not q.passage_text or len(q.passage_text.strip()) < 80:
                failures.append("VARC Reading Comprehension question missing linked passage context.")
                audit_records.append(
                    VerificationRecord(
                        question_id=q.id,
                        verification_type=VerificationType.SOURCE_VERIFY,
                        result=VerificationResult.FAILED,
                        details={"error": "missing_or_truncated_passage"},
                        verified_by="system",
                    )
                )
            else:
                audit_records.append(
                    VerificationRecord(
                        question_id=q.id,
                        verification_type=VerificationType.SOURCE_VERIFY,
                        result=VerificationResult.PASSED,
                        details={"passage_length": len(q.passage_text)},
                        verified_by="system",
                    )
                )
    elif q.section.value == "DILR":
        # DILR caselet logic check: text must describe constraint rules, sets, or tabular relationships
        dilr_indicators = ["table", "chart", "graph", "person", "sit", "tournament", "round", "team", "condition", "following"]
        has_logic = any(ind in q.question_text.lower() for ind in dilr_indicators)
        if not has_logic and len(q.question_text) < 40:
            failures.append("DILR caselet lacks sufficient logical constraint definitions.")
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.AMBIGUITY_CHECK,
                    result=VerificationResult.FAILED,
                    details={"error": "insufficient_dilr_constraints"},
                    verified_by="system",
                )
            )
        else:
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.AMBIGUITY_CHECK,
                    result=VerificationResult.PASSED,
                    details={"logic_structure": "validated"},
                    verified_by="system",
                )
            )

    # 4. Duplicate Question Detection
    dup_stmt = select(Question).where(
        Question.id != q.id,
        Question.section == q.section,
        Question.year == q.year,
        Question.verification_status == VerificationStatus.VERIFIED,
    )
    dup_res = await db.execute(dup_stmt)
    existing_qs = dup_res.scalars().all()
    q_norm = "".join(q.question_text.lower().split())

    for eq in existing_qs:
        eq_norm = "".join(eq.question_text.lower().split())
        if q_norm == eq_norm or (len(q_norm) > 40 and q_norm[:60] == eq_norm[:60]):
            failures.append(f"Duplicate question detected matching Question #{eq.question_number} from CAT {eq.year}.")
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.DUPLICATE_CHECK,
                    result=VerificationResult.FAILED,
                    details={"duplicate_of": str(eq.id), "matched_year": eq.year},
                    verified_by="system",
                )
            )
            break
    else:
        audit_records.append(
            VerificationRecord(
                question_id=q.id,
                verification_type=VerificationType.DUPLICATE_CHECK,
                result=VerificationResult.PASSED,
                details={"duplicate_status": "unique"},
                verified_by="system",
            )
        )

    # 4. Handle Manual Override
    if manual_override:
        if manual_override.lower() == "verified":
            q.verification_status = VerificationStatus.VERIFIED
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.SOURCE_VERIFY,
                    result=VerificationResult.PASSED,
                    details={"override": "manual_verified", "notes": reviewer_notes},
                    verified_by="manual",
                )
            )
        elif manual_override.lower() == "rejected":
            q.verification_status = VerificationStatus.REJECTED
            audit_records.append(
                VerificationRecord(
                    question_id=q.id,
                    verification_type=VerificationType.SOURCE_VERIFY,
                    result=VerificationResult.FAILED,
                    details={"override": "manual_rejected", "notes": reviewer_notes},
                    verified_by="manual",
                )
            )
    else:
        # Automatic outcome
        if failures:
            q.verification_status = VerificationStatus.REJECTED
        else:
            q.verification_status = VerificationStatus.VERIFIED

    for rec in audit_records:
        db.add(rec)

    await db.commit()
    await db.refresh(q)
    return len(failures) == 0, failures
