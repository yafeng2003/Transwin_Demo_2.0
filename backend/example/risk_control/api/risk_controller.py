
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from common.models.risk_event import RiskEvent, RiskEventResponse

router = APIRouter(prefix="/api/v1/risk", tags=["风控"])


@router.get("/events", response_model=list[RiskEvent])
async def list_risk_events(
    account_id: str | None = Query(None, description="按账户筛选"),
    min_level: int = Query(1, ge=1, le=5, description="最小事件等级"),
    start_time: datetime | None = Query(None, description="起始时间"),
    end_time: datetime | None = Query(None, description="结束时间"),
):
    return []


@router.get("/events/summary")
async def get_risk_summary():
    return {
        "total_events": 0,
        "alert_count": 0,
        "critical_count": 0,
    }
