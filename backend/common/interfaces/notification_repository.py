"""NotificationRepository 抽象接口。

通知层通过该接口保存通知记录和查询通知列表，具体存储可由内存仓库或数据库仓库实现。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from common.models import PagedResult, RiskNotification


class NotificationRepository(ABC):
    """通知记录仓储接口。"""

    @abstractmethod
    async def save_notification(self, notification: RiskNotification, send_status: str) -> int:
        """保存通知及发送状态，返回通知记录 ID。"""
        ...

    @abstractmethod
    async def list_notifications(
        self,
        notification_type: str | None = None,
        page: int = 1,
        size: int = 20,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> PagedResult[dict]:
        """分页查询通知记录，可按类型和 account/strategy 维度过滤。"""
        ...
