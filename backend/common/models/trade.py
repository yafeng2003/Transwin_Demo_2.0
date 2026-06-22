"""完整交易记录（开仓+平仓）模型。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(kw_only=True)
class Trade:
    """一笔有始有终的完整交易。
    由执行层在平仓后汇总写入，覆盖从开仓到平仓的全量信息。
    """
    trade_id: int | None
    market_id: int
    account_id: str
    strategy_id: str
    symbol_code: str
    symbol_name: str
    asset_type: int
    direction: int
    open_time: datetime
    close_time: datetime | None
    open_price: Decimal
    close_price: Decimal | None
    open_quantity: Decimal
    open_amount: Decimal
    realized_pnl: Decimal = Decimal("0")
    return_rate: Decimal = Decimal("0")
    commission: Decimal = Decimal("0")
