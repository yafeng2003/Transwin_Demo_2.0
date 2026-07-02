"""RiskRepository 抽象接口。

风控层通过该接口保存风险事件、风险通知，并查询风控看板和列表所需数据。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from common.models import PagedResult, RiskEvent, RiskNotification


class RiskRepository(ABC):
    """风险事件与风险通知仓储接口。"""

    @abstractmethod
    async def save_event(self, event: RiskEvent) -> int:
        """保存风险事件并返回事件 ID。"""
        ...

    @abstractmethod
    async def get_event(
        self, event_id: int, account_id: str | None = None, strategy_id: str | None = None
    ) -> dict | None:
        """查询单条风险事件，可按 account/strategy 定位分表。"""
        ...

    @abstractmethod
    async def update_event_status(
        self,
        event_id: int,
        status: str,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> bool:
        """更新风险事件处理状态。"""
        ...

    @abstractmethod
    async def list_events(
        self,
        event_type: str | None = None,
        level: int | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> PagedResult[dict]:
        """分页查询风险事件列表，可按类型、等级、状态和 account/strategy 过滤。"""
        ...

    @abstractmethod
    async def save_notification(self, notification: RiskNotification) -> int:
        """保存由风险事件派生的通知记录。"""
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
        """分页查询风险通知列表，可按类型和 account/strategy 过滤。"""
        ...

    @abstractmethod
    async def summarize_events(
        self, account_id: str | None = None, strategy_id: str | None = None
    ) -> dict:
        """汇总风控概览所需的事件数量指标。"""
        ...

    @abstractmethod
    async def compute_trend(
        self, account_id: str | None = None, strategy_id: str | None = None,
        days: int = 30,
    ) -> list[dict]:
        """计算指定天数内的风险评分趋势 [{date, riskScore}]。"""
        ...
