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

# ── Shared Corpus ──────────────────────────────────────────────────────
from .shared_corpus import (
    SharedHistoricalPaper,
    SharedVerifiedQuestion,
    SharedQuestionOption,
    SharedAnswerKey,
    SharedSolution,
    SharedQuestionSource,
    SharedQuestionTopic,
)

# ── Deduplication ──────────────────────────────────────────────────────
from .deduplication import (
    PaperFingerprint,
    QuestionFingerprint,
    DuplicateDetectionRecord,
    QuestionSimilarityReview,
    ReviewQueue,
)

# ── User History & Permissions ─────────────────────────────────────────
from .user_history import (
    UserUploadPermission,
    UserProcessingHistory,
)

# ── Statistics ─────────────────────────────────────────────────────────
from .statistics import (
    TopicFrequencyStatistic,
    YearlyTrend,
    DifficultyStatistic,
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
    # Shared Corpus
    "SharedHistoricalPaper",
    "SharedVerifiedQuestion",
    "SharedQuestionOption",
    "SharedAnswerKey",
    "SharedSolution",
    "SharedQuestionSource",
    "SharedQuestionTopic",
    # Deduplication
    "PaperFingerprint",
    "QuestionFingerprint",
    "DuplicateDetectionRecord",
    "QuestionSimilarityReview",
    "ReviewQueue",
    # User History & Permissions
    "UserUploadPermission",
    "UserProcessingHistory",
    # Statistics
    "TopicFrequencyStatistic",
    "YearlyTrend",
    "DifficultyStatistic",
]
