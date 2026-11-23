"""
Paper and Provenance Schemas.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PaperUploadMeta(BaseModel):
    year: int = Field(..., ge=2000, le=2025, description="Authentic CAT examination year")
    slot: Optional[str] = Field(None, description="e.g., Slot 1, Slot 2, Slot 3")
    source_name: str = Field(..., description="e.g., IIM Official, Career Launcher, IMS, TIME")
    source_type: str = Field(default="official", description="official, coaching, community, other")
    source_url: Optional[str] = None
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
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PaperListResponse(BaseModel):
    items: List[PaperResponse]
    total: int
