"""TradeRepository 抽象接口。

执行层与数据分析层通过此接口读写完整交易记录。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from common.models.trade import Trade


class TradeRepository(ABC):
    """完整交易记录仓储接口。"""

    @abstractmethod
    async def insert_trade(self, account_id: str, strategy_id: str,
                           trade: Trade) -> int:
        """保存完整交易记录，返回交易记录 ID。"""
        ...

    @abstractmethod
    async def get_trades_by_range(self, account_id: str, strategy_id: str,
                                  market_id: int,
                                  start_time: datetime, end_time: datetime
                                  ) -> list[Trade]:
        """按时间范围查询完整交易记录。"""
        ...
