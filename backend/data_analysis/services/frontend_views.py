"""把分析层的计算结果组装成前端约定的返回结构(camelCase)。

均为纯函数：输入原始数据/已算指标，输出前端字段的 dict，不做 IO，便于单元测试。
带 ⚠ 的字段为口径需与前端确认项(见 docstring)。
百分比类字段统一乘 100 并四舍五入到约定小数位。
"""

from __future__ import annotations

from common.models.trade import Trade
from data_analysis.services.metrics import (
    return_metrics,
    risk_metrics,
    strategy_metrics,
    trade_metrics,
)


def _equity_series(assets, equity_field: str):
    ordered = sorted(assets, key=lambda a: a.created_at)
    return ordered, [float(getattr(a, equity_field)) for a in ordered]


def daily_returns(assets, equity_field: str) -> list[dict]:
    """每日收益序列：date / dailyReturn(%) / cumulativeReturn(%) / netValue。"""
    ordered, values = _equity_series(assets, equity_field)
    if not values:
        return []
    base = values[0]
    out: list[dict] = []
    prev: float | None = None
    for asset, nv in zip(ordered, values):
        daily = (nv / prev - 1.0) * 100 if prev not in (None, 0.0) else 0.0
        cumulative = (nv / base - 1.0) * 100 if base else 0.0
        out.append(
            {
                "date": asset.created_at.strftime("%Y-%m-%d"),
                "dailyReturn": round(daily, 2),
                "cumulativeReturn": round(cumulative, 2),
                "netValue": round(nv, 4),
            }
        )
        prev = nv
    return out


def build_returns_view(assets, trades, ppy: int, rf: float, equity_field: str) -> dict:
    """GET /analysis/returns 的返回体。winRate 取该账户全部策略交易的胜率。"""
    rm = return_metrics.analyze_returns(assets, ppy, rf, equity_field)
    _, values = _equity_series(assets, equity_field)
    mdd = risk_metrics.max_drawdown(values)
    calmar = return_metrics.calmar_ratio(rm.annualized_return, mdd)
    tm = trade_metrics.analyze_trades(trades)
    return {
        "summary": {
            "totalReturn": round(rm.cumulative_return * 100, 2),
            "annualReturn": round(rm.annualized_return * 100, 2),
            "sharpeRatio": round(rm.sharpe_ratio, 2),
            "maxDrawdown": round(-mdd * 100, 2) + 0.0,
            "calmarRatio": round(calmar, 2),
            "winRate": round(tm.win_rate * 100, 1),
        },
        "dailyReturns": daily_returns(assets, equity_field),
    }


def build_risk_view(assets, exposure: dict, ppy: int, var_conf: float, equity_field: str) -> dict:
    """GET /analysis/risk 的返回体。riskExposure 由调用方组装后传入。"""
    _, values = _equity_series(assets, equity_field)
    vol = risk_metrics.annualized_volatility(values, ppy)
    dvol = risk_metrics.downside_deviation(values, ppy)
    dist = risk_metrics.drawdown_distribution(values)
    return {
        "volatility": round(vol * 100, 2),
        "downsideVolatility": round(dvol * 100, 2),
        "drawdownDistribution": [{"range": label, "count": count} for label, count in dist],
        "riskExposure": exposure,
    }


def build_trading_view(trades, deals, operations) -> dict:
    """GET /analysis/trading 的返回体。slippage 单位为基点(bps)，需与前端确认。"""
    tm = trade_metrics.analyze_trades(trades)
    freq = trade_metrics.compute_trade_frequency(trades)
    slip = trade_metrics.compute_slippage(deals, operations)
    monthly = trade_metrics.monthly_trade_stats(trades)
    avg_profit = float(tm.gross_profit) / tm.winning_trades if tm.winning_trades else 0.0
    avg_loss = -float(tm.gross_loss) / tm.losing_trades if tm.losing_trades else 0.0
    return {
        "winRate": round(tm.win_rate * 100, 1),
        "profitLossRatio": round(tm.payoff_ratio, 2) if tm.payoff_ratio is not None else None,
        "avgProfit": round(avg_profit, 2),
        "avgLoss": round(avg_loss, 2),
        "tradeCount": tm.total_trades,
        "tradeFrequency": round(freq.trades_per_day, 2),
        "totalCommission": round(float(tm.total_commission), 2),
        "slippage": round(slip.avg_slippage_bps, 4),
        "monthlyTrades": [
            {"month": month, "count": count, "winRate": round(wr * 100, 1)}
            for month, count, wr in monthly
        ],
    }


def _compounded_return_pct(trades: list[Trade]) -> float:
    # ⚠ 策略级总收益代理：无策略级净值曲线，用单笔收益率连乘近似。
    factor = 1.0
    for t in trades:
        factor *= 1.0 + float(t.return_rate)
    return (factor - 1.0) * 100


def _pnl_curve_max_drawdown_pct(trades: list[Trade]) -> float:
    # ⚠ 策略级最大回撤代理：累计已实现盈亏曲线相对其历史峰值的最大回撤(%)。
    cumulative = 0.0
    peak = 0.0
    worst = 0.0
    for t in sorted(trades, key=lambda x: (x.close_time or x.open_time)):
        cumulative += float(t.realized_pnl)
        peak = max(peak, cumulative)
        if peak > 0:
            worst = max(worst, (peak - cumulative) / peak)
    return round(-worst * 100, 2) + 0.0


def build_strategy_view(trades_by_strategy: dict[str, list[Trade]]) -> list[dict]:
    """GET /analysis/strategy 的返回体(数组)。

    winRate / tradeCount / contribution / correlation 为精确值；
    ⚠ totalReturn / sharpeRatio / maxDrawdown 为基于已实现盈亏的策略级代理
    (资产表为账户级、无策略级净值曲线)，口径需与前端确认。
    """
    comparison = strategy_metrics.compare_strategies(trades_by_strategy)
    perf_by_id = {p.strategy_id: p for p in comparison.performances}
    contrib_by_id = {c.strategy_id: c for c in comparison.contributions}
    corr = comparison.correlation
    corr_index = {label: i for i, label in enumerate(corr.labels)} if corr else {}

    views: list[dict] = []
    for sid, trades in trades_by_strategy.items():
        perf = perf_by_id.get(sid)
        if perf is None:
            continue
        contrib = contrib_by_id.get(sid)
        correlation: list[dict] = []
        if corr is not None and sid in corr_index:
            i = corr_index[sid]
            correlation = [
                {"strategy": corr.labels[j], "value": round(corr.matrix[i][j], 2)}
                for j in range(len(corr.labels))
            ]
        views.append(
            {
                "strategyId": sid,
                "strategyName": sid,
                "totalReturn": round(_compounded_return_pct(trades), 2),
                "sharpeRatio": round(perf.trade_sharpe, 2),
                "maxDrawdown": _pnl_curve_max_drawdown_pct(trades),
                "winRate": round(perf.win_rate * 100, 1),
                "tradeCount": perf.total_trades,
                "contribution": round(contrib.contribution * 100, 1) if contrib else 0.0,
                "correlation": correlation,
            }
        )
    return views
