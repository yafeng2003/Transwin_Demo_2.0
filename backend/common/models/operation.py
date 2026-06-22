"""策略生成的原始操作模型。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(kw_only=True)
class Operation:
    """策略层生成的一条交易操作，写入 operation 表。
    """
    operation_id: int
    market_id: int
    account_id: str
    strategy_id: str
    symbol_code: str
    symbol_name: str
    asset_type: int
    operation_type: int
    direction: int
    order_type: int
    price: Decimal
    quantity: Decimal
    created_at: datetime
    status: int
