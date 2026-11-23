"""
Structured Pydantic schemas for AI extraction, classification, and verification.
Guarantees strict type checking and deterministic parsing of LLM outputs.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ExtractedOptionSchema(BaseModel):
    """Option for an MCQ question."""

    label: str = Field(..., description="Option label: 'A', 'B', 'C', or 'D'")
    text: str = Field(..., description="The option text")
    is_correct: Optional[bool] = Field(default=False, description="Whether this is the correct answer")


class ExtractedQuestionSchema(BaseModel):
    """Structured question extracted by AI from raw CAT paper text."""

    question_number: int = Field(..., ge=1, le=100, description="Sequential question number in the paper")
    section: Literal["VARC", "DILR", "QA"] = Field(..., description="CAT section: VARC, DILR, or QA")
    question_type: Literal["MCQ", "TITA"] = Field(..., description="Format: Multiple Choice (MCQ) or Type-In-The-Answer (TITA)")
    question_text: str = Field(..., min_length=10, description="Complete question text with all figures/data/context")
    has_passage: bool = Field(default=False, description="Whether this question is tied to a reading comprehension passage")
    passage_text: Optional[str] = Field(default=None, description="The shared passage text if applicable")
    options: Optional[List[ExtractedOptionSchema]] = Field(
        default=None,
        description="List of options for MCQ questions. Exactly 4 for MCQ, null or empty for TITA.",
    )
    correct_answer: Optional[str] = Field(
        default=None,
        description="Correct answer ('A'-'D' for MCQ, number/string for TITA)",
    )
    solution_text: Optional[str] = Field(
        default=None,
        description="Detailed step-by-step mathematical or logical solution",
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="Estimated difficulty level",
    )
    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Model extraction confidence score (0.0 to 1.0)",
    )


class ExtractedPaperBatchSchema(BaseModel):
    """A batch of extracted questions from a paper."""

    year: int = Field(..., ge=2000, le=2026, description="CAT examination year")
    slot: Optional[str] = Field(default=None, description="Examination slot (e.g., Slot 1, Slot 2, Slot 3)")
    questions: List[ExtractedQuestionSchema] = Field(default_factory=list, description="Extracted questions")


class QuestionClassificationSchema(BaseModel):
    """Topic classification and syllabus mapping."""

    section: Literal["VARC", "DILR", "QA"] = Field(..., description="Section of the question")
    topic: str = Field(..., description="Primary topic (e.g. Arithmetic, Algebra, Reading Comprehension)")
    subtopic: str = Field(..., description="Fine-grained subtopic (e.g. Time Speed Distance, Logarithms)")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium", description="Estimated difficulty level")
    rationale: str = Field(..., description="Brief reasoning for classification")


class AIVerificationFeedbackSchema(BaseModel):
    """
    AI critique on question data consistency.
    NOTE: Even if AI reports valid, independent deterministic validation is mandatory.
    """

    mathematical_validity: bool = Field(..., description="Whether arithmetic and algebraic relations in the question are logically consistent")
    option_consistency: bool = Field(..., description="Whether options are mutually distinct and properly formatted")
    ambiguity_detected: bool = Field(..., description="Whether question text is ambiguous, incomplete, or contains conflicting statements")
    flaws_found: List[str] = Field(default_factory=list, description="Specific logical or mathematical contradictions detected")
    suggested_correction: Optional[str] = Field(default=None, description="Suggested resolution if flawed")
    critique_notes: str = Field(default="", description="Detailed analysis notes from AI")
