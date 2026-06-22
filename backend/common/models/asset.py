"""账户资产快照模型。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(kw_only=True)
class Asset:
    """某个时间点账户的资产快照。
    按天由执行层定时同步写入，用于后续净值曲线与收益分析。
    """
    created_at: datetime
    market_id: int
    account_id: str
    total_asset: Decimal
    net_value: Decimal
    market_value: Decimal
    cash_balance: Decimal
    asset_id: int | None = None
