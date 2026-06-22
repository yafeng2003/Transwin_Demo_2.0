from decimal import Decimal

from common.models.analytics import SlippageMetrics, TradeFrequency, TradeMetrics
from common.models.deal import Deal
from common.models.operation import Operation
from common.models.trade import Trade

_ZERO = Decimal("0")
_OPEN = 1
_CLOSE = 2
_LONG = 1
_SHORT = 2


def _closed_trades(trades: list[Trade]) -> list[Trade]:
    return [t for t in trades if t.close_time is not None and t.close_price is not None]


def analyze_trades(trades: list[Trade]) -> TradeMetrics:
    trades = _closed_trades(trades)
    total = len(trades)
    if total == 0:
        return TradeMetrics(
            total_trades=0, winning_trades=0, losing_trades=0, win_rate=0.0,
            gross_profit=_ZERO, gross_loss=_ZERO, profit_factor=None, payoff_ratio=None,
            avg_trade_pnl=_ZERO, expectancy=_ZERO, total_commission=_ZERO, avg_holding_seconds=0.0,
        )

    wins = [t for t in trades if t.realized_pnl > _ZERO]
    losses = [t for t in trades if t.realized_pnl < _ZERO]

    gross_profit = sum((t.realized_pnl for t in wins), _ZERO)
    gross_loss = -sum((t.realized_pnl for t in losses), _ZERO)
    total_pnl = sum((t.realized_pnl for t in trades), _ZERO)
    total_commission = sum((t.commission for t in trades), _ZERO)

    win_rate = len(wins) / total
    avg_trade_pnl = total_pnl / total

    avg_win = (gross_profit / len(wins)) if wins else _ZERO
    avg_loss = (gross_loss / len(losses)) if losses else _ZERO

    # 盈亏比与 Profit Factor 是不同口径，分别给出；分母为 0 时返回 None。
    profit_factor = float(gross_profit / gross_loss) if gross_loss > _ZERO else None
    payoff_ratio = float(avg_win / avg_loss) if avg_loss > _ZERO else None

    loss_rate = len(losses) / total
    expectancy = Decimal(str(win_rate)) * avg_win - Decimal(str(loss_rate)) * avg_loss

    holding_seconds = [(t.close_time - t.open_time).total_seconds() for t in trades]
    avg_holding_seconds = sum(holding_seconds) / total

    return TradeMetrics(
        total_trades=total, winning_trades=len(wins), losing_trades=len(losses), win_rate=win_rate,
        gross_profit=gross_profit, gross_loss=gross_loss, profit_factor=profit_factor,
        payoff_ratio=payoff_ratio, avg_trade_pnl=avg_trade_pnl, expectancy=expectancy,
        total_commission=total_commission, avg_holding_seconds=avg_holding_seconds,
    )


def compute_trade_frequency(trades: list[Trade]) -> TradeFrequency:
    trades = _closed_trades(trades)
    total = len(trades)
    if total == 0:
        return TradeFrequency(
            total_trades=0, span_days=0.0, trades_per_day=0.0,
            trades_per_week=0.0, trades_per_month=0.0,
        )

    earliest = min(t.open_time for t in trades)
    latest = max(t.close_time for t in trades)
    span_days = (latest - earliest).total_seconds() / 86400.0
    # 同日内全部交易时跨度为 0，按 1 天计避免除零。
    effective_days = span_days if span_days > 0 else 1.0
    per_day = total / effective_days

    return TradeFrequency(
        total_trades=total,
        span_days=span_days,
        trades_per_day=per_day,
        trades_per_week=per_day * 7.0,
        trades_per_month=per_day * 30.0,
    )


def _is_buy_side(deal: Deal) -> bool:
    # 买入：开多 或 平空；卖出：平多 或 开空。
    return (deal.deal_type == _OPEN and deal.direction == _LONG) or (
        deal.deal_type == _CLOSE and deal.direction == _SHORT
    )


def compute_slippage(deals: list[Deal], operations: list[Operation]) -> SlippageMetrics:
    intended_price = {op.operation_id: op.price for op in operations}

    matched = 0
    total_cost = _ZERO
    bps_values: list[float] = []
    for deal in deals:
        if deal.operation_id is None:
            continue
        intended = intended_price.get(deal.operation_id)
        if intended is None or intended <= _ZERO:
            continue
        matched += 1
        # 正数表示成交劣于委托：买入价更高、卖出价更低都算损失。
        signed = (deal.deal_price - intended) if _is_buy_side(deal) else (intended - deal.deal_price)
        total_cost += signed * deal.deal_quantity
        bps_values.append(float(signed / intended) * 10000.0)

    avg_bps = sum(bps_values) / len(bps_values) if bps_values else 0.0
    avg_per_deal = (total_cost / matched) if matched else _ZERO

    return SlippageMetrics(
        deal_count=len(deals),
        matched_count=matched,
        avg_slippage_bps=avg_bps,
        total_slippage_cost=total_cost,
        avg_slippage_per_deal=avg_per_deal,
    )
