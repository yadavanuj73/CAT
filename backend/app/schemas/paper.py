"""
Paper and Provenance Schemas.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PaperUploadMeta(BaseModel):
    year: int = Field(..., ge=2000, le=2025, description="Authentic CAT examination year")
    slot: Optional[str] = Field(None, description="e.g., Slot 1, Slot 2, Slot 3")
    source_name: str = Field(..., description="e.g., IIM Official, Career Launcher, IMS, TIME")
    source_type: str = Field(default="official", description="official, coaching, community, other")
    source_url: Optional[str] = None
    allow_sharing: bool = Field(default=True, description="Consent to add verified questions to shared bank")
    terms_accepted: bool = Field(default=True, description="Confirmation of legal eligibility to contribute")
    notes: Optional[str] = None


class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    year: int
    slot: Optional[str] = None
    source_name: str
    original_filename: str
    file_path: str
    status: str
    extraction_confidence: float
    total_questions: int
    allow_sharing: bool = True
    sharing_status: str = "pending"
    is_duplicate: bool = False
    duplicate_of_id: Optional[uuid.UUID] = None
    shared_paper_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PaperListResponse(BaseModel):
    items: List[PaperResponse]
    total: int


class UserProcessingHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    paper_id: uuid.UUID
    stage: str
    status: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime


class PaperContributionSummary(BaseModel):
    paper_id: uuid.UUID
    year: int
    slot: Optional[str] = None
    status: str
    total_extracted: int
    total_verified: int
    total_duplicate: int
    total_rejected: int
    promoted_to_shared: int
    shared_paper_id: Optional[uuid.UUID] = None
    sharing_status: str
