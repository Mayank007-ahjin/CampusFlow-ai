from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from ..core.database import get_db
from ..models import schemas
from ..services.recommendation_engine import RecommendationEngine

router = APIRouter()


@router.post("/recommend", response_model=schemas.RecommendationResponse)
async def get_recommendations(
    request: schemas.RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered facility recommendations based on natural language query.
    """
    try:
        engine = RecommendationEngine(db)
        result = await engine.get_recommendations(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/plan", response_model=schemas.RecommendationResponse)
async def plan_route(
    request: schemas.RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Plan an optimal multi-facility route (Multi-Agent Route Optimizer).
    """
    try:
        engine = RecommendationEngine(db)
        result = await engine.plan_multi_facility_route(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate route plan: {str(e)}"
        )


@router.get("/alerts", response_model=schemas.AlertListResponse)
async def get_alerts(
    db: Session = Depends(get_db)
):
    """
    Get proactive peak-hour advisor alerts and campus bottleneck warnings.
    """
    try:
        engine = RecommendationEngine(db)
        result = engine.get_proactive_alerts()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch proactive alerts: {str(e)}"
        )
