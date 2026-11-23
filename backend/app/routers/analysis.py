"""
Paper Analysis Router: VARC, DILR, QA section-wise analytics, topic frequencies, trends.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.analysis import RunAnalysisRequest, SectionAnalysisSummary
from app.services.analysis_service import run_section_analysis

router = APIRouter(prefix="/analysis", tags=["Paper Analysis"])


@router.get("/{section}", response_model=SectionAnalysisSummary)
async def get_section_analysis(
    section: str,
    decay_factor: float = Query(0.85, ge=0.5, le=1.0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve statistical topic frequencies and distribution for a section."""
    sec = section.upper()
    if sec not in ["VARC", "DILR", "QA"]:
        raise HTTPException(status_code=400, detail="Invalid section. Choose VARC, DILR, or QA.")

    summary = await run_section_analysis(
        db=db,
        user_id=current_user.id,
        section=sec,
        decay_factor=decay_factor,
    )
    return summary


@router.post("/run", response_model=SectionAnalysisSummary)
async def run_analysis(
    req: RunAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger recency-weighted analysis calculation."""
    sec = (req.section or "QA").upper()
    return await run_section_analysis(
        db=db,
        user_id=current_user.id,
        section=sec,
        decay_factor=req.recency_decay_factor,
    )
