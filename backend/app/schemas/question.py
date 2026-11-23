"""
Question and Verification Schemas.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class QuestionOptionSchema(BaseModel):
    option_label: str
    option_text: str
    is_correct: bool = False


class QuestionCreate(BaseModel):
    paper_id: uuid.UUID
    question_number: int
    question_text: str
    question_type: str = "MCQ"  # MCQ or TITA
    section: str  # VARC, DILR, QA
    difficulty: str = "medium"  # easy, medium, hard
    options: List[QuestionOptionSchema] = []
    correct_answer: Optional[str] = None
    solution_text: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    has_passage: bool = False
    passage_text: Optional[str] = None


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    paper_id: uuid.UUID
    user_id: uuid.UUID
    question_number: int
    question_text: str
    question_type: str
    section: str
    difficulty: str
    marks_positive: float
    marks_negative: float
    has_image: bool
    has_table: bool
    has_passage: bool
    passage_text: Optional[str] = None
    extraction_confidence: float
    verification_status: str
    year: int
    slot: Optional[str] = None
    options: List[QuestionOptionSchema] = []
    correct_answer: Optional[str] = None
    solution_text: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    created_at: datetime


class QuestionListResponse(BaseModel):
    items: List[QuestionResponse]
    total: int


class VerifyQuestionRequest(BaseModel):
    manual_review: bool = False
    status_override: Optional[str] = None  # verified or rejected
    notes: Optional[str] = None


class VerificationRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_id: Optional[uuid.UUID]
    verification_type: str
    result: str
    details: Optional[Dict] = None
    verified_by: str
    verified_at: datetime
