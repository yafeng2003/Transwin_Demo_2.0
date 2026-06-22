"""实际执行成功的成交记录模型。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(kw_only=True)
class Deal:
    """一条实际成交记录，关联到 operation。
    """
    deal_id: int
    operation_id: int | None
    market_id: int
    account_id: str
    strategy_id: str
    symbol_code: str
    symbol_name: str
    asset_type: int = 1
    deal_type: int
    direction: int
    deal_price: Decimal
    deal_quantity: Decimal
    deal_amount: Decimal
    commission: Decimal = Decimal("0")
    position_after: Decimal = Decimal("0")
    is_manual: int = 0
    deal_time: datetime
