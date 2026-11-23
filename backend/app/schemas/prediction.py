"""
Prediction Engine Schemas.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PredictionEvidenceItem(BaseModel):
    evidence_type: str  # historical_frequency, trend, archetype_match, slot_correlation
    evidence_text: str
    weight: float
    reference_years: List[int] = []


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    section: str
    topic_name: str
    subtopic_name: Optional[str] = None
    predicted_archetype: str
    statistical_score: float = Field(..., ge=0.0, le=1.0)
    calibrated_confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    uncertainty_and_limitations: str
    historical_evidence: List[PredictionEvidenceItem] = []
    backtesting_baseline_comparison: Optional[str] = None
    created_at: datetime


class PredictionListResponse(BaseModel):
    predictions: List[PredictionResponse]
    total: int
    methodology_statement: str
    last_updated: datetime


class GeneratePredictionsRequest(BaseModel):
    section: Optional[str] = None
    target_year: int = 2026
    min_confidence: float = 0.50
