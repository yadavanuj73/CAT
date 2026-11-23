"""
CAT Intelligence 2026 — ORM models package.

Importing this module registers every model with the shared ``Base.metadata``
so that Alembic auto-generation and ``Base.metadata.create_all()`` work correctly.
"""

from .base import Base, TimestampMixin

# ── User & auth ────────────────────────────────────────────────────────
from .user import EncryptedCredential, User, UserSetting

# ── Paper pipeline ─────────────────────────────────────────────────────
from .paper import Paper, PaperSource, PaperStatus, SourceType

# ── Questions ──────────────────────────────────────────────────────────
from .question import (
    AnswerKey,
    Difficulty,
    Question,
    QuestionOption,
    QuestionType,
    Section,
    Solution,
    VerificationStatus,
)

# ── Topics & classification ────────────────────────────────────────────
from .topic import ClassifiedBy, QuestionClassification, Topic

# ── Analysis ───────────────────────────────────────────────────────────
from .analysis import AnalysisResult

# ── Predictions ────────────────────────────────────────────────────────
from .prediction import Prediction, PredictionEvidence

# ── Mock exams ─────────────────────────────────────────────────────────
from .mock_exam import (
    AttemptStatus,
    ExamAttempt,
    ExamType,
    MockExam,
    MockQuestion,
    MockVerificationStatus,
)

# ── Audit & verification ──────────────────────────────────────────────
from .audit import (
    AuditLog,
    VerificationRecord,
    VerificationResult,
    VerificationType,
    VerifiedBy,
)

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    # User
    "User",
    "UserSetting",
    "EncryptedCredential",
    # Paper
    "Paper",
    "PaperSource",
    "PaperStatus",
    "SourceType",
    # Question
    "Question",
    "QuestionOption",
    "AnswerKey",
    "Solution",
    "QuestionType",
    "Section",
    "Difficulty",
    "VerificationStatus",
    # Topic
    "Topic",
    "QuestionClassification",
    "ClassifiedBy",
    # Analysis
    "AnalysisResult",
    # Prediction
    "Prediction",
    "PredictionEvidence",
    # Mock exam
    "MockExam",
    "MockQuestion",
    "ExamAttempt",
    "ExamType",
    "MockVerificationStatus",
    "AttemptStatus",
    # Audit
    "VerificationRecord",
    "VerificationType",
    "VerificationResult",
    "VerifiedBy",
    "AuditLog",
]
