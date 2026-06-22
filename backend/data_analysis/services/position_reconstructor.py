from datetime import datetime
from decimal import Decimal

from common.models.trading import ActivePosition, ActivePositions
from common.models.deal import Deal

_ZERO = Decimal("0")
_OPEN = 1
_CLOSE = 2
_LONG = 1


class _SymbolState:

    def __init__(self) -> None:
        self.quantity: Decimal = _ZERO
        self.avg_cost: Decimal = _ZERO
        self.direction: int = 0
        self.position_type: int = 0
        self.open_time: datetime | None = None
        self.symbol_code: str = ""


def _unrealized(direction: int, avg_cost: Decimal, price: Decimal, quantity: Decimal) -> Decimal:
    # 多头价涨为盈，空头价跌为盈。
    if direction == _LONG:
        return (price - avg_cost) * quantity
    return (avg_cost - price) * quantity


def reconstruct_positions(
    deals: list[Deal],
    market_id: int,
    account_id: str,
    strategy_id: str,
    query_time: datetime,
    prices: dict[str, Decimal] | None = None,
) -> ActivePositions:
    """按成交流水重放出 query_time 时点的持仓快照。

    数量以 position_after 为权威值（执行层成交后写入），均价由开仓成交移动加权得到。
    传入 prices 时计算浮动盈亏，否则记 0（无内部现价源时）。
    """
    relevant = sorted(
        (d for d in deals if d.deal_time <= query_time),
        key=lambda d: d.deal_time,
    )

    states: dict[str, _SymbolState] = {}
    for deal in relevant:
        state = states.setdefault(deal.symbol_code, _SymbolState())
        state.symbol_code = deal.symbol_code

        if deal.deal_type == _OPEN:
            new_qty = state.quantity + deal.deal_quantity
            if new_qty > _ZERO:
                state.avg_cost = (
                    state.avg_cost * state.quantity + deal.deal_price * deal.deal_quantity
                ) / new_qty
            if state.quantity == _ZERO:
                state.open_time = deal.deal_time
                state.direction = deal.direction
                state.position_type = deal.direction
            state.quantity = deal.position_after
        elif deal.deal_type == _CLOSE:
            state.quantity = deal.position_after
            if state.quantity <= _ZERO:
                states[deal.symbol_code] = _SymbolState()
        else:
            state.quantity = deal.position_after

    positions: list[ActivePosition] = []
    for state in states.values():
        if state.quantity <= _ZERO or state.open_time is None:
            continue
        price = prices.get(state.symbol_code) if prices else None
        unrealized = (
            _unrealized(state.direction, state.avg_cost, price, state.quantity)
            if price is not None
            else _ZERO
        )
        positions.append(
            ActivePosition(
                symbol_code=state.symbol_code,
                position_type=state.position_type,
                direction=state.direction,
                open_price=state.avg_cost,
                holding_quantity=state.quantity,
                holding_amount=state.avg_cost * state.quantity,
                open_time=state.open_time,
                unrealized_pnl=unrealized,
            )
        )

    return ActivePositions(
        market_id=market_id,
        account_id=account_id,
        strategy_id=strategy_id,
        current_time=query_time,
        active_positions=positions,
    )
