"""OperationRepository 抽象接口。

策略层与执行层通过此接口读写操作表，不依赖具体数据库实现。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from common.models.operation import Operation


class OperationRepository(ABC):
    """操作仓储接口。"""

    @abstractmethod
    async def insert_operations(self, account_id: str, strategy_id: str,
                                operations: list[Operation]) -> int:
        """批量保存策略生成的原始操作，返回写入条数。"""
        ...

    @abstractmethod
    async def get_pending_operations(self, account_id: str, strategy_id: str,
                                     market_id: int) -> list[Operation]:
        """查询待执行操作列表。"""
        ...

    @abstractmethod
    async def get_operations_by_range(self, account_id: str, strategy_id: str,
                                      market_id: int,
                                      start_time: datetime, end_time: datetime
                                      ) -> list[Operation]:
        """按时间范围查询操作记录。"""
        ...

    @abstractmethod
    async def update_status(self, operation_id: int, account_id: str,
                            strategy_id: str, new_status: int) -> bool:
        """更新操作状态，返回是否成功更新到记录。"""
        ...
