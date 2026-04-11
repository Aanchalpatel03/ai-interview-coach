from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.performance import PerformanceAnalyticsResponse, PerformanceHistoryResponse
from app.services.performance_service import build_performance_analytics, build_performance_history

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/history", response_model=PerformanceHistoryResponse)
async def performance_history(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return build_performance_history(db, current_user.id)


@router.get("/analytics", response_model=PerformanceAnalyticsResponse)
async def performance_analytics(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return build_performance_analytics(db, current_user.id)
