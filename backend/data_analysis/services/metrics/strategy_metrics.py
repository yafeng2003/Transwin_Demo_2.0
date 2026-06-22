import statistics
from collections import defaultdict
from datetime import date
from decimal import Decimal

import numpy as np

from common.models.analytics import (
    CorrelationMatrix,
    StrategyComparison,
    StrategyContribution,
    StrategyPerformance,
)
from common.models.trade import Trade

_ZERO = Decimal("0")


def _closed_trades(trades: list[Trade]) -> list[Trade]:
    return [t for t in trades if t.close_time is not None and t.close_price is not None]


def compute_contributions(pnl_by_strategy: dict[str, Decimal]) -> list[StrategyContribution]:
    total = sum(pnl_by_strategy.values(), _ZERO)
    contributions: list[StrategyContribution] = []
    for strategy_id, pnl in pnl_by_strategy.items():
        # 总盈亏为 0 时贡献度无意义，统一记 0。
        ratio = float(pnl / total) if total != _ZERO else 0.0
        contributions.append(
            StrategyContribution(strategy_id=strategy_id, realized_pnl=pnl, contribution=ratio)
        )
    return contributions


def compute_correlation(returns_by_strategy: dict[str, list[float]]) -> CorrelationMatrix | None:
    labels = list(returns_by_strategy.keys())
    if len(labels) < 2:
        return None

    lengths = {len(returns_by_strategy[label]) for label in labels}
    if len(lengths) != 1 or lengths in ({0}, {1}):
        # 相关性要求各策略收益序列已按时间对齐且长度一致且不少于 2。
        return None

    data = np.array([returns_by_strategy[label] for label in labels], dtype=float)
    matrix = np.corrcoef(data)
    return CorrelationMatrix(labels=labels, matrix=np.nan_to_num(matrix, nan=0.0).tolist())


def max_drawdown_amount(cumulative_values: list[Decimal]) -> Decimal:
    if not cumulative_values:
        return _ZERO
    peak = cumulative_values[0]
    worst = _ZERO
    for value in cumulative_values:
        peak = max(peak, value)
        worst = max(worst, peak - value)
    return worst


def build_cumulative_realized_pnl(trades: list[Trade]) -> list[Decimal]:
    trades = _closed_trades(trades)
    ordered = sorted(trades, key=lambda t: t.close_time)
    running = _ZERO
    series: list[Decimal] = []
    for trade in ordered:
        running += trade.realized_pnl
        series.append(running)
    return series


def daily_pnl(trades: list[Trade]) -> dict[date, Decimal]:
    buckets: dict[date, Decimal] = defaultdict(lambda: _ZERO)
    for trade in _closed_trades(trades):
        buckets[trade.close_time.date()] += trade.realized_pnl
    return dict(buckets)


def strategy_performance(strategy_id: str, trades: list[Trade]) -> StrategyPerformance:
    trades = _closed_trades(trades)
    total = len(trades)
    realized = sum((t.realized_pnl for t in trades), _ZERO)
    if total == 0:
        return StrategyPerformance(
            strategy_id=strategy_id, realized_pnl=_ZERO, total_trades=0, win_rate=0.0,
            profit_factor=None, avg_return_rate=0.0, return_rate_std=0.0,
            trade_sharpe=0.0, max_drawdown_amount=_ZERO,
        )

    wins = [t for t in trades if t.realized_pnl > _ZERO]
    gross_profit = sum((t.realized_pnl for t in wins), _ZERO)
    gross_loss = -sum((t.realized_pnl for t in trades if t.realized_pnl < _ZERO), _ZERO)
    profit_factor = float(gross_profit / gross_loss) if gross_loss > _ZERO else None

    returns = [float(t.return_rate) for t in trades]
    avg_rr = statistics.fmean(returns)
    std_rr = statistics.stdev(returns) if total >= 2 else 0.0
    # 交易级夏普：单笔收益率的均值/标准差，不做时间年化（账户净值无法拆到策略）。
    trade_sharpe = (avg_rr / std_rr) if std_rr > 0 else 0.0

    mdd_amount = max_drawdown_amount(build_cumulative_realized_pnl(trades))

    return StrategyPerformance(
        strategy_id=strategy_id,
        realized_pnl=realized,
        total_trades=total,
        win_rate=len(wins) / total,
        profit_factor=profit_factor,
        avg_return_rate=avg_rr,
        return_rate_std=std_rr,
        trade_sharpe=trade_sharpe,
        max_drawdown_amount=mdd_amount,
    )


def _aligned_daily_returns(trades_by_strategy: dict[str, list[Trade]]) -> dict[str, list[float]] | None:
    daily_by_strategy = {sid: daily_pnl(trades) for sid, trades in trades_by_strategy.items()}
    all_dates = sorted({d for buckets in daily_by_strategy.values() for d in buckets})
    if len(all_dates) < 2:
        return None
    # 按日期并集对齐，缺失日补 0，得到可比较的每日盈亏序列。
    return {
        sid: [float(daily_by_strategy[sid].get(d, _ZERO)) for d in all_dates]
        for sid in trades_by_strategy
    }


def compare_strategies(trades_by_strategy: dict[str, list[Trade]]) -> StrategyComparison:
    trades_by_strategy = {
        sid: _closed_trades(trades) for sid, trades in trades_by_strategy.items()
    }
    pnl_by_strategy = {
        sid: sum((t.realized_pnl for t in trades), _ZERO)
        for sid, trades in trades_by_strategy.items()
    }
    performances = [
        strategy_performance(sid, trades) for sid, trades in trades_by_strategy.items()
    ]

    aligned = _aligned_daily_returns(trades_by_strategy)
    correlation = compute_correlation(aligned) if aligned else None

    return StrategyComparison(
        performances=performances,
        contributions=compute_contributions(pnl_by_strategy),
        correlation=correlation,
    )
