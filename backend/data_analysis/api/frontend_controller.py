"""Frontend-facing analysis API adapters.

将 AnalysisService 的原始计算结果组装为前端约定的 camelCase 返回结构，
提供更丰富的图表数据（navSeries / drawdownSeries / monthlyReturns 等）。
"""

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Query

from common.models import ApiResponse
from data_analysis.services.analysis_service import AnalysisService
from data_analysis.services.metrics import risk_metrics
from data_analysis.services.metrics.return_metrics import calmar_ratio

router = APIRouter(prefix="/api/v1/analysis", tags=["数据分析"])


def get_frontend_analysis_service() -> AnalysisService:
    raise RuntimeError("AnalysisService 未注入")


def _period_window(period: str) -> tuple[datetime, datetime]:
    end_time = datetime.now()
    days = {"1m": 30, "3m": 90, "6m": 180, "1y": 365}.get(period, 30)
    return end_time - timedelta(days=days), end_time


def _sortino_ratio(annualized_return: float, downside_deviation: float) -> float:
    if downside_deviation <= 0:
        return 0
    return annualized_return / downside_deviation


def _annual_returns(daily_returns: list[dict]) -> list[dict]:
    buckets: dict[int, list[dict]] = defaultdict(list)
    for item in daily_returns:
        year = datetime.strptime(item["date"], "%Y-%m-%d").year
        buckets[year].append(item)
    rows = []
    for year in sorted(buckets):
        points = buckets[year]
        if not points:
            continue
        first = points[0]["netValue"]
        last = points[-1]["netValue"]
        annual_return = ((last / first) - 1) * 100 if first else 0
        rows.append({"year": year, "return": annual_return, "benchmark": 0})
    return rows


@router.get("/returns", response_model=ApiResponse[dict])
async def get_analysis_returns(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
    period: str = Query("1m"),
    service: AnalysisService = Depends(get_frontend_analysis_service),
):
    start_time, end_time = _period_window(period)
    summary = await service.get_return_metrics(market_id, account_id, start_time, end_time)
    risk_summary = await service.get_risk_metrics(market_id, account_id, start_time, end_time)
    curve = await service.get_equity_curve(market_id, account_id, start_time, end_time)
    drawdown = await service.get_drawdown_series(market_id, account_id, start_time, end_time)
    monthly = await service.get_period_returns(market_id, account_id, "monthly", start_time, end_time)
    distribution = await service.get_return_distribution(market_id, account_id, start_time, end_time, bins=10)

    daily_returns = []
    previous_net_value: Decimal | None = None
    for point in curve.points:
        daily_return = Decimal("0")
        if previous_net_value not in (None, Decimal("0")):
            daily_return = (point.net_value / previous_net_value - Decimal("1")) * Decimal("100")
        previous_net_value = point.net_value
        daily_returns.append({
            "date": point.time.strftime("%Y-%m-%d"),
            "dailyReturn": float(daily_return),
            "cumulativeReturn": point.cumulative_return * 100,
            "netValue": float(point.net_value),
        })

    nav_series = [point["netValue"] for point in daily_returns]
    drawdown_series = [point.drawdown * 100 for point in drawdown]
    monthly_returns = [{
        "year": item.period_end.year,
        "monthIdx": item.period_end.month,
        "return": item.return_rate * 100,
    } for item in monthly.items]
    daily_return_dist = [{
        "bucket": f"{bin.lower * 100:.1f}~{bin.upper * 100:.1f}%",
        "count": bin.count,
    } for bin in distribution.bins]
    annual_returns = _annual_returns(daily_returns)

    return ApiResponse(data={
        "summary": {
            "totalReturn": summary.cumulative_return * 100,
            "annualReturn": summary.annualized_return * 100,
            "sharpeRatio": summary.sharpe_ratio,
            "maxDrawdown": (-risk_summary.max_drawdown * 100) + 0.0,
            "calmarRatio": calmar_ratio(summary.annualized_return, risk_summary.max_drawdown),
            "winRate": 0,
            "volatility": risk_summary.annualized_volatility * 100,
            "sortinoRatio": _sortino_ratio(
                summary.annualized_return,
                risk_metrics.downside_deviation(nav_series, service._ppy(market_id)),
            ),
            "informationRatio": 0,
        },
        "dailyReturns": daily_returns,
        "navSeries": nav_series,
        "drawdownSeries": drawdown_series,
        "monthlyReturns": monthly_returns,
        "dailyReturnDist": daily_return_dist,
        "annualReturns": annual_returns,
    })


@router.get("/risk", response_model=ApiResponse[dict])
async def get_analysis_risk(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
    period: str = Query("1m"),
    service: AnalysisService = Depends(get_frontend_analysis_service),
):
    start_time, end_time = _period_window(period)
    metrics = await service.get_risk_metrics(market_id, account_id, start_time, end_time)
    distribution = await service.get_return_distribution(market_id, account_id, start_time, end_time, bins=5)
    return ApiResponse(data={
        "volatility": metrics.annualized_volatility * 100,
        "downsideVolatility": metrics.var_95 * 100,
        "drawdownDistribution": [{
            "range": f"{bin.lower * 100:.2f}~{bin.upper * 100:.2f}%",
            "count": bin.count,
        } for bin in distribution.bins],
        "riskExposure": {"sectors": [], "strategies": [], "heatmapData": []},
    })


@router.get("/trading", response_model=ApiResponse[dict])
async def get_analysis_trading(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
    period: str = Query("1m"),
    strategy_id: str = Query("manual"),
    service: AnalysisService = Depends(get_frontend_analysis_service),
):
    start_time, end_time = _period_window(period)
    metrics = await service.get_trade_metrics(market_id, account_id, strategy_id, start_time, end_time)
    frequency = await service.get_trade_frequency(market_id, account_id, strategy_id, start_time, end_time)
    slippage = await service.get_slippage(market_id, account_id, strategy_id, start_time, end_time)
    avg_profit = float(metrics.gross_profit / metrics.winning_trades) if metrics.winning_trades else 0
    avg_loss = float(-metrics.gross_loss / metrics.losing_trades) if metrics.losing_trades else 0
    return ApiResponse(data={
        "winRate": metrics.win_rate * 100,
        "profitLossRatio": metrics.payoff_ratio or 0,
        "avgProfit": avg_profit,
        "avgLoss": avg_loss,
        "tradeCount": metrics.total_trades,
        "tradeFrequency": frequency.trades_per_day,
        "totalCommission": float(metrics.total_commission),
        "slippage": slippage.avg_slippage_bps,
        "monthlyTrades": [],
    })


@router.get("/strategy", response_model=ApiResponse[list[dict]])
async def get_analysis_strategy(
    market_id: int = Query(1),
    account_id: str = Query("acc_main"),
    strategy_ids: list[str] | None = Query(None),
    service: AnalysisService = Depends(get_frontend_analysis_service),
):
    ids = strategy_ids or ["manual"]
    start_time, end_time = _period_window("1y")
    comparison = await service.compare_strategies(market_id, account_id, ids, start_time, end_time)
    contribution_by_strategy = {
        item.strategy_id: item.contribution * 100 for item in comparison.contributions
    }
    rows = []
    for performance in comparison.performances:
        correlation = []
        if comparison.correlation is not None and performance.strategy_id in comparison.correlation.labels:
            row_index = comparison.correlation.labels.index(performance.strategy_id)
            correlation = [{
                "strategy": label,
                "value": comparison.correlation.matrix[row_index][index],
            } for index, label in enumerate(comparison.correlation.labels)]
        rows.append({
            "strategyId": performance.strategy_id,
            "strategyName": performance.strategy_id,
            "totalReturn": float(performance.realized_pnl),
            "sharpeRatio": performance.trade_sharpe,
            "maxDrawdown": float(performance.max_drawdown_amount),
            "winRate": performance.win_rate * 100,
            "tradeCount": performance.total_trades,
            "contribution": contribution_by_strategy.get(performance.strategy_id, 0),
            "correlation": correlation,
        })
    return ApiResponse(data=rows)
