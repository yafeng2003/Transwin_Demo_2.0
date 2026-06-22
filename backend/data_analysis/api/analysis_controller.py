from datetime import datetime

from fastapi import APIRouter, Depends, Query

from common.models.analytics import (
    EquityCurve,
    ExposureMetrics,
    PeriodReturns,
    PositionDistribution,
    ReturnDistribution,
    ReturnMetrics,
    RiskMetrics,
    SectorDistribution,
    SlippageMetrics,
    StrategyComparison,
    TradeFrequency,
    TradeMetrics,
)
from common.models.analytics import DrawdownPoint
from common.models.trading import ActivePositions
from data_analysis.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/v1/analysis", tags=["数据分析"])


def get_analysis_service() -> AnalysisService:
    # 占位依赖，组装阶段在 main.py 通过 dependency_overrides 注入真实实例。
    raise RuntimeError("AnalysisService 未注入")


@router.get("/returns", response_model=ReturnMetrics)
async def get_returns(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    service: AnalysisService = Depends(get_analysis_service),
) -> ReturnMetrics:
    return await service.get_return_metrics(market_id, account_id, start_time, end_time)


@router.get("/returns/periods", response_model=PeriodReturns)
async def get_period_returns(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    granularity: str = Query("daily", description="粒度：daily / weekly / monthly"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    service: AnalysisService = Depends(get_analysis_service),
) -> PeriodReturns:
    return await service.get_period_returns(market_id, account_id, granularity, start_time, end_time)


@router.get("/equity-curve", response_model=EquityCurve)
async def get_equity_curve(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    service: AnalysisService = Depends(get_analysis_service),
) -> EquityCurve:
    return await service.get_equity_curve(market_id, account_id, start_time, end_time)


@router.get("/risk", response_model=RiskMetrics)
async def get_risk(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    service: AnalysisService = Depends(get_analysis_service),
) -> RiskMetrics:
    return await service.get_risk_metrics(market_id, account_id, start_time, end_time)


@router.get("/risk/drawdown", response_model=list[DrawdownPoint])
async def get_drawdown(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    service: AnalysisService = Depends(get_analysis_service),
) -> list[DrawdownPoint]:
    return await service.get_drawdown_series(market_id, account_id, start_time, end_time)


@router.get("/risk/distribution", response_model=ReturnDistribution)
async def get_distribution(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    bins: int = Query(20, ge=1, le=100, description="直方图分箱数"),
    service: AnalysisService = Depends(get_analysis_service),
) -> ReturnDistribution:
    return await service.get_return_distribution(market_id, account_id, start_time, end_time, bins)


@router.get("/trades", response_model=TradeMetrics)
async def get_trades(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    strategy_id: str = Query(description="策略"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    service: AnalysisService = Depends(get_analysis_service),
) -> TradeMetrics:
    return await service.get_trade_metrics(market_id, account_id, strategy_id, start_time, end_time)


@router.get("/trades/frequency", response_model=TradeFrequency)
async def get_trade_frequency(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    strategy_id: str = Query(description="策略"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    service: AnalysisService = Depends(get_analysis_service),
) -> TradeFrequency:
    return await service.get_trade_frequency(market_id, account_id, strategy_id, start_time, end_time)


@router.get("/trades/slippage", response_model=SlippageMetrics)
async def get_slippage(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    strategy_id: str = Query(description="策略"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    service: AnalysisService = Depends(get_analysis_service),
) -> SlippageMetrics:
    return await service.get_slippage(market_id, account_id, strategy_id, start_time, end_time)


@router.get("/positions", response_model=ActivePositions)
async def get_positions(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    strategy_id: str = Query(description="策略"),
    query_time: datetime = Query(description="快照时间点"),
    service: AnalysisService = Depends(get_analysis_service),
) -> ActivePositions:
    return await service.get_positions(market_id, account_id, strategy_id, query_time)


@router.get("/positions/distribution", response_model=PositionDistribution)
async def get_position_distribution(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    strategy_id: str = Query(description="策略"),
    query_time: datetime = Query(description="快照时间点"),
    service: AnalysisService = Depends(get_analysis_service),
) -> PositionDistribution:
    return await service.get_position_distribution(market_id, account_id, strategy_id, query_time)


@router.get("/positions/exposure", response_model=ExposureMetrics)
async def get_exposure(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    strategy_id: str = Query(description="策略"),
    query_time: datetime = Query(description="快照时间点"),
    service: AnalysisService = Depends(get_analysis_service),
) -> ExposureMetrics:
    return await service.get_exposure(market_id, account_id, strategy_id, query_time)


@router.get("/positions/sectors", response_model=SectorDistribution)
async def get_sector_distribution(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    strategy_id: str = Query(description="策略"),
    query_time: datetime = Query(description="快照时间点"),
    service: AnalysisService = Depends(get_analysis_service),
) -> SectorDistribution:
    return await service.get_sector_distribution(market_id, account_id, strategy_id, query_time)


@router.get("/strategy-comparison", response_model=StrategyComparison)
async def get_strategy_comparison(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    strategy_ids: list[str] = Query(description="参与对比的策略列表"),
    start_time: datetime = Query(description="起始时间"),
    end_time: datetime = Query(description="结束时间"),
    service: AnalysisService = Depends(get_analysis_service),
) -> StrategyComparison:
    return await service.compare_strategies(market_id, account_id, strategy_ids, start_time, end_time)
