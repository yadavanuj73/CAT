"""
Pydantic Schemas for Global Shared Verified Question Bank.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SharedQuestionOptionSchema(BaseModel):
    id: uuid.UUID
    option_label: str
    option_text: str
    is_correct: bool = False


class SharedQuestionSourceSchema(BaseModel):
    id: uuid.UUID
    year: int
    slot: Optional[str] = None
    question_number: Optional[int] = None
    source_name: Optional[str] = None
    source_type: str = "official"
    provenance_notes: Optional[str] = None


class SharedQuestionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    canonical_hash: str
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
    dataset_text: Optional[str] = None
    primary_year: int
    primary_slot: Optional[str] = None
    verification_status: str
    verification_confidence: float
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    options: List[SharedQuestionOptionSchema] = []
    correct_answer: Optional[str] = None
    solution_text: Optional[str] = None
    sources: List[SharedQuestionSourceSchema] = []
    created_at: datetime


class SharedQuestionReviewRequest(BaseModel):
    status: str = Field(..., description="verified, needs_review, or rejected")
    notes: Optional[str] = None


class SharedQuestionReviewResponse(BaseModel):
    id: uuid.UUID
    verification_status: str
    message: str


class SharedQuestionListResponse(BaseModel):
    items: List[SharedQuestionDetail]
    total: int


class SharedHistoricalPaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    year: int
    slot: Optional[str] = None
    paper_title: str
    file_fingerprint: str
    total_questions: int
    is_verified: bool
    source_provenance: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SharedHistoricalPaperListResponse(BaseModel):
    items: List[SharedHistoricalPaperResponse]
    total: int


class SharedCorpusStatsResponse(BaseModel):
    total_verified_papers: int
    total_unique_verified_questions: int
    total_duplicates_prevented: int
    total_sources_linked: int
    section_breakdown: Dict[str, int]
    year_breakdown: Dict[int, int]
    topic_breakdown: List[Dict[str, Any]]
    difficulty_breakdown: Dict[str, int] = Field(default_factory=dict)
    recent_approved_questions: List[SharedQuestionDetail]
