"""风控层 HTTP API。

通过 FastAPI 暴露风险概览、风险事件列表、单条事件和风险通知列表。
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from common.models import ApiResponse, PagedResult
from risk_control.services.risk_service import RiskEventService

router = APIRouter(prefix="/api/v1", tags=["风控"])

risk_service = RiskEventService()


def configure_risk_dependencies(service: RiskEventService) -> None:
    """在 main.py 中注入风控服务，保持 API 层与具体实现解耦。"""
    global risk_service
    risk_service = service


class ResolveRiskEventRequest(BaseModel):
    id: int
    account_id: str | None = None
    strategy_id: str | None = None


@router.get("/dashboard/risk-status", response_model=ApiResponse[dict])
async def get_dashboard_risk_status(
    account_id: str = Query("acc_main"),
    strategy_id: str = Query("manual"),
):
    overview = await risk_service.get_overview(account_id=account_id, strategy_id=strategy_id)
    return ApiResponse(
        data={
            "riskLevel": overview["riskLevel"],
            "riskScore": overview["riskScore"],
            "todayEvents": overview["todayEvents"],
            "unresolvedEvents": overview["unresolvedEvents"],
            "weekEvents": overview["weekEvents"],
            "maxDrawdown": overview["maxDrawdown"],
            "dailyLossLimit": 500000,
            "dailyLoss": 0,
            "consecutiveLosses": 0,
        }
    )


@router.get("/risk/overview", response_model=ApiResponse[dict])
async def get_risk_overview(
    account_id: str = Query("acc_main"),
    strategy_id: str = Query("manual"),
):
    return ApiResponse(data=await risk_service.get_overview(account_id=account_id, strategy_id=strategy_id))


@router.get("/risk/trend", response_model=ApiResponse[list[dict]])
async def get_risk_trend(days: int = Query(30, ge=1, le=365)):
    return ApiResponse(data=[])


@router.get("/risk/events", response_model=ApiResponse[PagedResult[dict]])
async def list_risk_events(
    account_id: str | None = Query(None),
    strategy_id: str | None = Query(None),
    type: str | None = Query(None),
    level: int | None = Query(None, ge=1, le=3),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    result = await risk_service.list_events(
        event_type=type,
        level=level,
        status=status,
        page=page,
        size=size,
        account_id=account_id,
        strategy_id=strategy_id,
    )
    return ApiResponse(data=result)


@router.post("/risk/events/resolve", response_model=ApiResponse[dict])
async def resolve_risk_event(request: ResolveRiskEventRequest):
    event = await risk_service.resolve_event(request.id, request.account_id, request.strategy_id)
    if event is None:
        raise HTTPException(status_code=404, detail="risk event not found")
    return ApiResponse(data=event)


@router.get("/risk/events/{event_id}", response_model=ApiResponse[dict])
async def get_risk_event(
    event_id: int,
    account_id: str | None = Query(None),
    strategy_id: str | None = Query(None),
):
    event = await risk_service.get_event(event_id, account_id, strategy_id)
    if event is None:
        raise HTTPException(status_code=404, detail="risk event not found")
    return ApiResponse(data=event)


@router.get("/risk/account-metrics", response_model=ApiResponse[dict])
async def get_account_metrics():
    return ApiResponse(data=await risk_service.get_account_metrics())


@router.get("/risk/notifications", response_model=ApiResponse[PagedResult[dict]])
async def list_risk_notifications(
    account_id: str | None = Query(None),
    strategy_id: str | None = Query(None),
    type: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    result = await risk_service.list_notifications(
        notification_type=type,
        page=page,
        size=size,
        account_id=account_id,
        strategy_id=strategy_id,
    )
    return ApiResponse(data=result)
