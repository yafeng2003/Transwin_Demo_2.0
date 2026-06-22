from datetime import datetime, timedelta
from decimal import Decimal

from common.models.asset import Asset
from common.models.deal import Deal
from common.models.operation import Operation
from common.models.trade import Trade

_BASE = datetime(2024, 1, 1, 9, 30, 0)


def make_asset(day_offset: int, net_value: str, account_id: str = "acc_001", market_id: int = 1) -> Asset:
    nv = Decimal(net_value)
    return Asset(
        asset_id=day_offset + 1,
        created_at=_BASE + timedelta(days=day_offset),
        market_id=market_id,
        account_id=account_id,
        total_asset=nv,
        net_value=nv,
        market_value=nv,
        cash_balance=Decimal("0"),
    )


def make_assets(net_values: list[str], market_id: int = 1) -> list[Asset]:
    return [make_asset(i, nv, market_id=market_id) for i, nv in enumerate(net_values)]


def make_trade(
    pnl: str,
    commission: str = "1",
    hold_hours: int = 1,
    strategy_id: str = "s1",
    trade_id: int = 1,
    return_rate: str = "0.1",
    close_day_offset: int | None = None,
    symbol_code: str = "600001.SH",
    symbol_name: str = "测试标的",
) -> Trade:
    open_time = _BASE
    close_time = (
        _BASE + timedelta(days=close_day_offset)
        if close_day_offset is not None
        else open_time + timedelta(hours=hold_hours)
    )
    return Trade(
        trade_id=trade_id,
        market_id=1,
        account_id="acc_001",
        strategy_id=strategy_id,
        symbol_code=symbol_code,
        symbol_name=symbol_name,
        asset_type=1,
        direction=1,
        open_time=open_time,
        close_time=close_time,
        open_price=Decimal("10"),
        close_price=Decimal("11"),
        open_quantity=Decimal("100"),
        open_amount=Decimal("1000"),
        realized_pnl=Decimal(pnl),
        return_rate=Decimal(return_rate),
        commission=Decimal(commission),
    )


def make_deal(
    deal_id: int,
    day_offset: int,
    deal_type: int,
    deal_quantity: str,
    deal_price: str,
    position_after: str,
    direction: int = 1,
    symbol_code: str = "600001.SH",
    strategy_id: str = "s1",
    operation_id: int | None = None,
) -> Deal:
    return Deal(
        deal_id=deal_id,
        operation_id=operation_id if operation_id is not None else deal_id,
        market_id=1,
        account_id="acc_001",
        strategy_id=strategy_id,
        symbol_code=symbol_code,
        symbol_name="测试标的",
        asset_type=1,
        deal_type=deal_type,
        direction=direction,
        deal_price=Decimal(deal_price),
        deal_quantity=Decimal(deal_quantity),
        deal_amount=Decimal(deal_price) * Decimal(deal_quantity),
        commission=Decimal("1"),
        position_after=Decimal(position_after),
        is_manual=0,
        deal_time=_BASE + timedelta(days=day_offset),
    )


def make_operation(
    operation_id: int,
    price: str,
    direction: int = 1,
    operation_type: int = 1,
    order_type: int = 1,
    quantity: str = "100",
    strategy_id: str = "s1",
    symbol_code: str = "600001.SH",
) -> Operation:
    return Operation(
        operation_id=operation_id,
        market_id=1,
        account_id="acc_001",
        strategy_id=strategy_id,
        symbol_code=symbol_code,
        symbol_name="测试标的",
        asset_type=1,
        operation_type=operation_type,
        direction=direction,
        order_type=order_type,
        price=Decimal(price),
        quantity=Decimal(quantity),
        created_at=_BASE,
        status=1,
    )
