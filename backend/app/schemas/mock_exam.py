"""
Mock Exam & Question Generation Schemas.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MockQuestionOption(BaseModel):
    label: str
    text: str


class MockQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mock_exam_id: uuid.UUID
    question_number: int
    question_text: str
    question_type: str  # MCQ / TITA
    options: Optional[List[MockQuestionOption]] = None
    correct_answer: str
    solution_text: str
    topic: str
    subtopic: Optional[str] = None
    difficulty: str
    estimated_time_seconds: int
    marks_positive: float
    marks_negative: float
    verification_status: str
    verification_details: Optional[Dict[str, Any]] = None


class MockExamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    exam_type: str  # full, sectional, topic, predicted
    title: str
    description: Optional[str] = None
    section: Optional[str] = None
    total_questions: int
    total_marks: float
    duration_minutes: int
    verification_status: str
    questions_verified: int
    questions_failed: int
    questions: Optional[List[MockQuestionResponse]] = None
    created_at: datetime


class MockGenerateRequest(BaseModel):
    exam_type: str = Field(..., description="full, sectional, topic, predicted")
    title: Optional[str] = None
    section: Optional[str] = None  # VARC, DILR, QA
    topic_name: Optional[str] = None
    question_count: int = Field(default=22, ge=5, le=66)
    duration_minutes: int = Field(default=40, ge=10, le=120)


class AttemptSubmission(BaseModel):
    responses: Dict[str, str]  # question_id -> user answer
    time_spent_seconds: int


class AttemptResult(BaseModel):
    attempt_id: uuid.UUID
    mock_exam_id: uuid.UUID
    total_score: float
    max_score: float
    percentage: float
    accuracy_percentage: float
    total_attempted: int
    correct_count: int
    incorrect_count: int
    section_breakdown: Dict[str, Dict[str, float]]
    detailed_feedback: List[Dict[str, Any]]
