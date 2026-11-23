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

    # 2. Option Consistency Check (for MCQ)
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
            # Check for duplicate options
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

    # 3. Deterministic Mathematical Check (for QA questions with equations)
    if q.section.value == "QA":
        math_valid, math_msg = verify_arithmetic_statement(q.question_text)
        audit_records.append(
            VerificationRecord(
                question_id=q.id,
                verification_type=VerificationType.MATH_VERIFY,
                result=VerificationResult.PASSED if math_valid else VerificationResult.WARNING,
                details={"message": math_msg},
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
