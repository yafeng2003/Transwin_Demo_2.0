"""AssetRepository 抽象接口。

执行层与数据分析层通过此接口读写资产快照。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from common.models.asset import Asset


class AssetRepository(ABC):
    """资产快照仓储接口。"""

    @abstractmethod
    async def sync_asset(self, account_id: str, asset: Asset) -> int:
        """保存账户资产快照，返回资产记录 ID。"""
        ...

    @abstractmethod
    async def get_assets_by_range(self, account_id: str, market_id: int,
                                  start_time: datetime, end_time: datetime
                                  ) -> list[Asset]:
        """按时间范围查询账户资产快照。"""
        ...
