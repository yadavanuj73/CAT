"""
CAT 2026 Predictions Router.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.prediction import (
    GeneratePredictionsRequest,
    PredictionListResponse,
)
from app.services.prediction_service import get_or_generate_predictions

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("", response_model=PredictionListResponse)
async def list_predictions(
    section: Optional[str] = Query(None, description="VARC, DILR, QA"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve calibrated CAT 2026 predictions with historical evidence."""
    return await get_or_generate_predictions(db, current_user.id, section)


@router.post("/generate", response_model=PredictionListResponse)
async def generate_predictions(
    req: GeneratePredictionsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-compute statistical predictions with evidence weights."""
    return await get_or_generate_predictions(db, current_user.id, req.section)
