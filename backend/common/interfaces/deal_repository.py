"""DealRepository 抽象接口。

执行层与数据分析层通过此接口读写成交记录。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from common.models.deal import Deal


class DealRepository(ABC):
    """成交记录仓储接口。"""

    @abstractmethod
    async def insert_deal(self, account_id: str, strategy_id: str,
                          deal: Deal) -> int:
        """保存成交记录，返回成交记录 ID。"""
        ...

    @abstractmethod
    async def get_deals_before(self, account_id: str, strategy_id: str,
                               market_id: int, current_time: datetime
                               ) -> list[Deal]:
        """查询指定时间点之前的成交记录。"""
        ...

    @abstractmethod
    async def get_deals_by_range(self, account_id: str, strategy_id: str,
                                 market_id: int,
                                 start_time: datetime, end_time: datetime
                                 ) -> list[Deal]:
        """按时间范围查询成交记录。"""
        ...
