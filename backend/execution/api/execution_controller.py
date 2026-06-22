"""执行层 HTTP API。

通过 FastAPI 暴露订单、成交、持仓、账户资产和手工交易接口。
"""

from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, model_validator

from common.models import ApiResponse, PagedResult
from execution.adapters.mock_adapter import MockBrokerAdapter
from execution.services.execution_repository import InMemoryExecutionRepository
from execution.services.manual_execution_service import ManualExecutionService

router = APIRouter(prefix="/api/v1", tags=["执行"])

execution_repository = InMemoryExecutionRepository()
manual_service = ManualExecutionService(MockBrokerAdapter(), repository=execution_repository)


def configure_execution_dependencies(
    repository: InMemoryExecutionRepository,
    service: ManualExecutionService,
) -> None:
    """在 main.py 中注入执行层依赖，避免 API 层直接组装具体实现。"""
    global execution_repository, manual_service
    execution_repository = repository
    manual_service = service


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
    price: Decimal | None = None
    quantity: Decimal | None = None

    @model_validator(mode="after")
    def validate_change(self):
        """确保改单请求至少包含价格或数量中的一项。"""
        if self.price is None and self.quantity is None:
            raise ValueError("price or quantity is required")
        return self


@router.get("/orders", response_model=ApiResponse[PagedResult[dict]])
async def list_orders(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    return ApiResponse(data=await execution_repository.list_orders(page, size))


@router.get("/deals", response_model=ApiResponse[PagedResult[dict]])
async def list_deals(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    return ApiResponse(data=await execution_repository.list_deals(page, size))


@router.get("/deals/stats", response_model=ApiResponse[dict])
async def get_deal_stats():
    return ApiResponse(data=await execution_repository.get_deal_stats())


@router.get("/positions/current", response_model=ApiResponse[list[dict]])
async def list_current_positions():
    return ApiResponse(data=await execution_repository.list_positions())


@router.get("/positions/history", response_model=ApiResponse[list[dict]])
async def list_history_positions():
    return ApiResponse(data=[])


@router.get("/account/assets", response_model=ApiResponse[dict])
async def get_account_assets():
    return ApiResponse(data=await execution_repository.get_account_assets())


@router.get("/dashboard/asset-summary", response_model=ApiResponse[dict])
async def get_dashboard_asset_summary():
    assets = await execution_repository.get_account_assets()
    current = assets.get("current", {})
    return ApiResponse(
        data={
            "totalAsset": current.get("totalAsset", 0),
            "netValue": current.get("netValue", 1),
            "todayPnl": 0,
            "totalPnl": 0,
            "marketValue": current.get("marketValue", 0),
            "cashBalance": current.get("cashBalance", 0),
            "todayReturnRate": 0,
            "totalReturnRate": 0,
        }
    )


@router.get("/dashboard/position-overview", response_model=ApiResponse[dict])
async def get_dashboard_position_overview(limit: int = Query(6, ge=1, le=100)):
    positions = await execution_repository.list_positions()
    total_market_value = sum(p.get("holdingAmount", 0) for p in positions)
    result_positions = []
    for p in positions[:limit]:
        result_positions.append({
            "symbolCode": p.get("symbolCode", ""),
            "symbolName": p.get("symbolName", ""),
            "direction": p.get("direction", 1),
            "quantity": p.get("holdingQuantity", 0),
            "avgPrice": p.get("openPrice", 0),
            "marketValue": p.get("holdingAmount", 0),
            "unrealizedPnl": p.get("unrealizedPnl", 0),
            "weight": round(p.get("holdingAmount", 0) / total_market_value * 100, 1) if total_market_value > 0 else 0,
        })
    return ApiResponse(
        data={
            "positions": result_positions,
            "totalMarketValue": total_market_value,
        }
    )


@router.get("/dashboard/recent-deals", response_model=ApiResponse[list[dict]])
async def list_recent_deals(limit: int = Query(10, ge=1, le=100)):
    deals = await execution_repository.list_deals(page=1, size=limit)
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
    return ApiResponse(data=result)


@router.post("/manual/sell", response_model=ApiResponse[dict])
async def manual_sell(request: ManualOrderRequest):
    result = await manual_service.sell(
        request.marketId,
        request.accountId,
        request.symbolCode,
        request.orderType,
        request.price,
        request.quantity,
    )
    return ApiResponse(data=result)


@router.post("/manual/modify-order", response_model=ApiResponse[dict])
async def manual_modify_order(request: ModifyManualOrderRequest):
    try:
        result = await manual_service.modify_order(request.orderId, "manual", request.price, request.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(data=result)


@router.get("/logs/trading", response_model=ApiResponse[PagedResult[dict]])
async def list_trading_logs(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    result = PagedResult(list=[], total=0, page=page, size=size)
    return ApiResponse(data=result)
