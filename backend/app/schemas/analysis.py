"""
Analytical Engine Schemas.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TopicFrequency(BaseModel):
    topic: str
    subtopic: Optional[str] = None
    total_count: int
    percentage: float
    year_distribution: Dict[str, int]
    recency_weighted_score: float
    avg_difficulty: str


class DifficultyDistribution(BaseModel):
    easy_count: int
    medium_count: int
    hard_count: int
    easy_pct: float
    medium_pct: float
    hard_pct: float


class QuestionTypeDistribution(BaseModel):
    mcq_count: int
    tita_count: int
    mcq_pct: float
    tita_pct: float


class SectionAnalysisSummary(BaseModel):
    section: str
    total_verified_questions: int
    years_covered: List[int]
    top_topics: List[TopicFrequency]
    difficulty_distribution: DifficultyDistribution
    question_type_distribution: QuestionTypeDistribution
    recurring_archetypes: List[str]
    methodology: str


class RunAnalysisRequest(BaseModel):
    section: Optional[str] = Field(None, description="VARC, DILR, QA or null for all")
    recency_decay_factor: float = Field(default=0.85, ge=0.5, le=1.0)
