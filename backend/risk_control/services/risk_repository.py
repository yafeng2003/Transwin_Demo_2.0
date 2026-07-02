"""风控层内存仓储。

用于默认组装和单元测试；真实数据库场景通过 common/interfaces.RiskRepository 注入数据库实现。
"""

from common.interfaces import RiskRepository
from common.models import PagedResult, RiskEvent, RiskNotification


class InMemoryRiskRepository(RiskRepository):
    """RiskRepository 的内存实现，支持事件和通知的分页查询。"""

    def __init__(self):
        self._events: list[tuple[int, RiskEvent]] = []
        self._notifications: list[tuple[int, RiskNotification]] = []
        self._next_event_id = 1
        self._next_notification_id = 1

    async def save_event(self, event: RiskEvent) -> int:
        """保存风险事件并返回内存自增 ID。"""
        event_id = self._next_event_id
        self._next_event_id += 1
        self._events.append((event_id, event))
        return event_id

    async def get_event(
        self, event_id: int, account_id: str | None = None, strategy_id: str | None = None
    ) -> dict | None:
        """按事件 ID 查询风险事件，可附加 account/strategy 过滤。"""
        for stored_id, event in self._events:
            if (
                stored_id == event_id
                and (account_id is None or event.account_id == account_id)
                and (strategy_id is None or event.strategy_id == strategy_id)
            ):
                return self._to_event_row(stored_id, event)
        return None

    async def update_event_status(
        self,
        event_id: int,
        status: str,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> bool:
        """更新风险事件处理状态。"""
        for stored_id, event in self._events:
            if (
                stored_id == event_id
                and (account_id is None or event.account_id == account_id)
                and (strategy_id is None or event.strategy_id == strategy_id)
            ):
                event.status = status
                return True
        return False

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
        """按类型、等级、状态和分表维度分页查询风险事件。"""
        rows = [
            self._to_event_row(event_id, event)
            for event_id, event in self._events
            if (event_type is None or event.event_type == event_type)
            and (level is None or self._frontend_level(event.event_level) == level)
            and (status is None or event.status == status)
            and (account_id is None or event.account_id == account_id)
            and (strategy_id is None or event.strategy_id == strategy_id)
        ]
        start = (page - 1) * size
        end = start + size
        return PagedResult(list=rows[start:end], total=len(rows), page=page, size=size)

    async def save_notification(self, notification: RiskNotification) -> int:
        """保存由风险事件派生的通知记录。"""
        notification_id = self._next_notification_id
        self._next_notification_id += 1
        self._notifications.append((notification_id, notification))
        return notification_id

    async def list_notifications(
        self,
        notification_type: str | None = None,
        page: int = 1,
        size: int = 20,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> PagedResult[dict]:
        """分页查询风险通知，可按类型和 account/strategy 过滤。"""
        rows = [
            {
                "id": notification_id,
                "type": notification.notification_type,
                "typeLabel": self._notification_label(notification.notification_type),
                "level": self._frontend_level(notification.risk_level),
                "title": notification.title,
                "content": notification.content,
                "isRead": notification.is_read,
                "createdAt": notification.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for notification_id, notification in self._notifications
            if notification_type is None or notification.notification_type == notification_type
            if account_id is None or notification.account_id == account_id
            if strategy_id is None or notification.strategy_id == strategy_id
        ]
        start = (page - 1) * size
        end = start + size
        return PagedResult(list=rows[start:end], total=len(rows), page=page, size=size)

    async def summarize_events(
        self, account_id: str | None = None, strategy_id: str | None = None
    ) -> dict:
        """汇总风险看板所需的事件数量指标。"""
        events = [
            event
            for _, event in self._events
            if (account_id is None or event.account_id == account_id)
            and (strategy_id is None or event.strategy_id == strategy_id)
        ]
        total = len(events)
        unresolved = sum(1 for event in events if event.status != "resolved")
        high = sum(1 for event in events if event.event_level >= 4)
        today_events = total
        return {
            "totalEvents": total,
            "todayEvents": today_events,
            "weekEvents": total,
            "unresolvedEvents": unresolved,
            "highRiskEvents": high,
        }

    async def compute_trend(
        self, account_id: str | None = None, strategy_id: str | None = None,
        days: int = 30,
    ) -> list[dict]:
        return []

    def _to_event_row(self, event_id: int, event: RiskEvent) -> dict:
        return {
            "id": event_id,
            "eventType": event.event_type,
            "eventLabel": self._event_label(event.event_type),
            "level": self._frontend_level(event.event_level),
            "accountId": event.account_id,
            "strategyId": event.strategy_id,
            "symbolCode": event.symbol_code,
            "message": event.event_message,
            "status": event.status,
            "occurTime": event.occur_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _frontend_level(self, event_level: int) -> int:
        if event_level >= 4:
            return 3
        if event_level >= 2:
            return 2
        return 1

    def _event_label(self, event_type: str) -> str:
        labels = {
            "order_failed": "下单失败",
            "cancel_failed": "撤单失败",
            "modify_failed": "改单失败",
            "api_error": "API异常",
            "timeout": "超时",
            "daily_loss": "单日亏损",
            "drawdown": "最大回撤",
            "consecutive_loss": "连续亏损",
            "circuit_breaker": "熔断",
        }
        return labels.get(event_type, event_type)

    def _notification_label(self, notification_type: str) -> str:
        labels = {
            "risk_alert": "风险报警",
            "circuit_breaker": "熔断通知",
            "anomaly": "异常通知",
            "strategy_pause": "策略暂停",
            "manual_intervention": "人工干预",
        }
        return labels.get(notification_type, notification_type)
