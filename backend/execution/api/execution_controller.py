"""执行层 HTTP API。

通过 FastAPI 暴露订单、成交、持仓、账户资产和手工交易接口。
"""

from datetime import datetime, time
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, model_validator

from common.models import ApiResponse, PagedResult
from common.utils import app_logger
from execution.adapters.mock_adapter import MockBrokerAdapter
from execution.services.execution_repository import InMemoryExecutionRepository
from execution.services.manual_execution_service import ManualExecutionService
from execution.services.position_service import PositionService

router = APIRouter(prefix="/api/v1", tags=["执行"])

execution_repository = InMemoryExecutionRepository()
_adapter = MockBrokerAdapter()
manual_service = ManualExecutionService(_adapter, repository=execution_repository)
position_service = PositionService(_adapter, execution_repository)


def configure_execution_dependencies(
    repository: InMemoryExecutionRepository,
    service: ManualExecutionService,
    positions: PositionService | None = None,
) -> None:
    """在 main.py 中注入执行层依赖，避免 API 层直接组装具体实现。"""
    global execution_repository, manual_service, position_service
    execution_repository = repository
    manual_service = service
    if positions is not None:
        position_service = positions


class ManualOrderRequest(BaseModel):
    """手工买卖请求体。"""

    marketId: int = 1
    accountId: str
    symbolCode: str
    orderType: int = Field(ge=1, le=2)
    price: Decimal | None = None
    quantity: Decimal = Field(ge=0)


class ModifyManualOrderRequest(BaseModel):
    """手工改单请求体。"""

    orderId: str
    accountId: str = "acc_main"
    price: Decimal | None = None
    quantity: Decimal | None = None

    @model_validator(mode="after")
    def validate_change(self):
        """确保改单请求至少包含价格或数量中的一项。"""
        if self.price is None and self.quantity is None:
            raise ValueError("price or quantity is required")
        return self


@router.get("/orders", response_model=ApiResponse[PagedResult[dict]])
async def list_orders(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
    strategy_id: str = Query("manual"),
    status: int | None = Query(None),
    symbol: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return ApiResponse(
        data=await execution_repository.list_orders(
            page=page,
            size=size,
            market_id=market_id,
            account_id=account_id,
            strategy_id=strategy_id,
            status=status,
            symbol=symbol,
        )
    )


@router.get("/deals", response_model=ApiResponse[PagedResult[dict]])
async def list_deals(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
    strategy_id: str = Query("manual"),
    date_range: str | None = Query(None),
    symbol: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    start_time, end_time = _parse_date_range(date_range)
    return ApiResponse(
        data=await execution_repository.list_deals(
            page=page,
            size=size,
            market_id=market_id,
            account_id=account_id,
            strategy_id=strategy_id,
            start_time=start_time,
            end_time=end_time,
            symbol=symbol,
        )
    )


@router.get("/deals/stats", response_model=ApiResponse[dict])
async def get_deal_stats(
    account_id: str = Query("acc_main"),
    strategy_id: str = Query("manual"),
    date_range: str | None = Query(None),
):
    start_time, end_time = _parse_date_range(date_range)
    return ApiResponse(
        data=await execution_repository.get_deal_stats(account_id, strategy_id, start_time, end_time)
    )


@router.get("/positions/current", response_model=ApiResponse[list[dict]])
async def list_current_positions(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
    strategy_id: str = Query("manual"),
):
    return ApiResponse(
        data=await position_service.list_strategy_positions(
            market_id=market_id,
            account_id=account_id,
            strategy_id=strategy_id,
        )
    )


@router.get("/account/positions", response_model=ApiResponse[list[dict]])
async def list_account_positions(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
):
    return ApiResponse(data=await position_service.list_account_positions(account_id, market_id))


@router.get("/positions/history", response_model=ApiResponse[list[dict]])
async def list_history_positions():
    return ApiResponse(data=[])


@router.get("/account/assets", response_model=ApiResponse[dict])
async def get_account_assets(
    market_id: int | None = Query(None),
    account_id: str | None = Query(None),
    days: int | None = Query(None, ge=1),
):
    return ApiResponse(data=await execution_repository.get_account_assets(account_id, market_id, days))


@router.get("/dashboard/asset-summary", response_model=ApiResponse[dict])
async def get_asset_summary(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
):
    return ApiResponse(data=await execution_repository.get_asset_summary(market_id, account_id))


@router.get("/dashboard/position-overview", response_model=ApiResponse[dict])
async def get_position_overview(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
    strategy_id: str = Query("manual"),
    limit: int = Query(5, ge=1, le=100),
):
    raw = await position_service.list_strategy_positions(market_id, account_id, strategy_id)
    total_market_value = sum(Decimal(str(p["holdingAmount"])) for p in raw)
    overview_positions = []
    for p in raw[:limit]:
        mv = Decimal(str(p["holdingAmount"]))
        weight = (
            mv / total_market_value * Decimal("100")
            if total_market_value != Decimal("0")
            else Decimal("0")
        )
        overview_positions.append(
            {
                "symbolCode": p["symbolCode"],
                "symbolName": p["symbolName"],
                "direction": p["direction"],
                "quantity": p["holdingQuantity"],
                "avgPrice": p["openPrice"],
                "marketValue": float(mv),
                "unrealizedPnl": p["unrealizedPnl"],
                "weight": float(weight),
            }
        )
    return ApiResponse(
        data={
            "positions": overview_positions,
            "totalMarketValue": float(total_market_value),
        }
    )


@router.get("/dashboard/recent-deals", response_model=ApiResponse[list[dict]])
async def list_recent_deals(
    market_id: int | None = Query(None),
    account_id: str | None = Query(None),
    strategy_id: str | None = Query(None),
    limit: int = Query(10, ge=1, le=100),
):
    deals = await execution_repository.list_deals(
        page=1,
        size=limit,
        market_id=market_id,
        account_id=account_id,
        strategy_id=strategy_id,
    )
    return ApiResponse(data=deals.list)


@router.post("/manual/buy", response_model=ApiResponse[dict])
async def manual_buy(request: ManualOrderRequest):
    result = await manual_service.buy(
        request.marketId,
        request.accountId,
        request.symbolCode,
        request.orderType,
        request.price,
        request.quantity,
    )
    app_logger.log_trading("order", request.symbolCode, "", f"手动买入: {request.symbolCode} x{request.quantity}")
    return ApiResponse(data=result)


@router.post("/manual/sell", response_model=ApiResponse[dict])
async def manual_sell(request: ManualOrderRequest):
    try:
        result = await manual_service.sell(
            request.marketId,
            request.accountId,
            request.symbolCode,
            request.orderType,
            request.price,
            request.quantity,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(data=result)


@router.post("/manual/modify-order", response_model=ApiResponse[dict])
async def manual_modify_order(request: ModifyManualOrderRequest):
    try:
        result = await manual_service.modify_order(request.orderId, request.accountId, request.price, request.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(data=result)


@router.get("/logs/trading", response_model=ApiResponse[PagedResult[dict]])
async def list_trading_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    type: str | None = Query(None, description="类型：order / cancel / deal"),
):
    return ApiResponse(data=app_logger.list_trading_logs(log_type=type, page=page, size=size))


@router.get("/logs/system", response_model=ApiResponse[PagedResult[dict]])
async def list_system_logs(
    level: str | None = Query(None, description="级别：INFO / WARN / ERROR"),
    module: str | None = Query(None, description="模块：strategy / executor / risk / analysis / system"),
    stage: str | None = Query(None),
    action: str | None = Query(None),
    errorType: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return ApiResponse(data=app_logger.list_system_logs(level=level, module=module, page=page, size=size))


def _parse_date_range(date_range: str | None) -> tuple[datetime | None, datetime | None]:
    if not date_range:
        return None, None
    parts = [part.strip() for part in date_range.split(",") if part.strip()]
    if len(parts) != 2:
        raise HTTPException(status_code=422, detail="date_range must be 'YYYY-MM-DD,YYYY-MM-DD'")
    try:
        start_date = datetime.fromisoformat(parts[0]).date()
        end_date = datetime.fromisoformat(parts[1]).date()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="date_range must be 'YYYY-MM-DD,YYYY-MM-DD'") from exc
    return datetime.combine(start_date, time.min), datetime.combine(end_date, time.max)
