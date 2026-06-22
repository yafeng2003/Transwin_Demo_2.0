"""数据分析层 HTTP API。

按前端《前端所需后端接口文档》提供 4 个组合接口：收益/风险/交易/策略分析。
返回统一用 ApiResponse 包裹(参照 execution_controller)；字段为 camelCase；
入参用 period(1m/3m/6m/1y)，market_id/account_id 选填。
依赖在 main.py 通过 dependency_overrides 注入 AnalysisService。
"""

from fastapi import APIRouter, Depends, Query

from common.models import ApiResponse
from data_analysis.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/v1/analysis", tags=["数据分析"])


def get_analysis_service() -> AnalysisService:
    # 占位依赖，组装阶段在 main.py 通过 dependency_overrides 注入真实实例。
    raise RuntimeError("AnalysisService 未注入")


@router.get("/returns", response_model=ApiResponse[dict])
async def analysis_returns(
    market_id: int = Query(1, description="市场ID，选填"),
    account_id: str = Query("", description="账户ID，选填"),
    period: str = Query("3m", description="周期：1m/3m/6m/1y，默认3m"),
    service: AnalysisService = Depends(get_analysis_service),
) -> ApiResponse[dict]:
    return ApiResponse(data=await service.returns_analysis(market_id, account_id, period))


@router.get("/risk", response_model=ApiResponse[dict])
async def analysis_risk(
    market_id: int = Query(1, description="市场ID，选填"),
    account_id: str = Query("", description="账户ID，选填"),
    period: str = Query("3m", description="周期：1m/3m/6m/1y，默认3m"),
    service: AnalysisService = Depends(get_analysis_service),
) -> ApiResponse[dict]:
    return ApiResponse(data=await service.risk_analysis(market_id, account_id, period))


@router.get("/trading", response_model=ApiResponse[dict])
async def analysis_trading(
    market_id: int = Query(1, description="市场ID，选填"),
    account_id: str = Query("", description="账户ID，选填"),
    strategy_id: str = Query("", description="策略ID，选填；为空表示全部策略"),
    period: str = Query("3m", description="周期：1m/3m/6m/1y，默认3m"),
    service: AnalysisService = Depends(get_analysis_service),
) -> ApiResponse[dict]:
    return ApiResponse(
        data=await service.trading_analysis(market_id, account_id, strategy_id, period)
    )


@router.get("/strategy", response_model=ApiResponse[list[dict]])
async def analysis_strategy(
    market_id: int = Query(1, description="市场ID，选填"),
    account_id: str = Query("", description="账户ID，选填"),
    service: AnalysisService = Depends(get_analysis_service),
) -> ApiResponse[list[dict]]:
    return ApiResponse(data=await service.strategy_analysis(market_id, account_id))
