"""通知层内存仓储。

用于默认组装和单元测试；数据库场景通过 common/interfaces.NotificationRepository 注入真实实现。
"""

from common.interfaces import NotificationRepository
from common.models import PagedResult, RiskNotification


class InMemoryNotificationRepository(NotificationRepository):
    """NotificationRepository 的内存实现。"""

    def __init__(self):
        self._notifications: list[tuple[int, RiskNotification, str]] = []
        self._next_id = 1

    async def save_notification(self, notification: RiskNotification, send_status: str) -> int:
        """保存通知及其发送状态。"""
        notification_id = self._next_id
        self._next_id += 1
        self._notifications.append((notification_id, notification, send_status))
        return notification_id

    async def list_notifications(
        self,
        notification_type: str | None = None,
        page: int = 1,
        size: int = 20,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> PagedResult[dict]:
        """分页查询通知列表，可按类型和 account/strategy 过滤。"""
        rows = [
            {
                "id": notification_id,
                "type": notification.notification_type,
                "typeLabel": self._type_label(notification.notification_type),
                "level": notification.risk_level,
                "title": notification.title,
                "content": notification.content,
                "isRead": notification.is_read,
                "sendStatus": send_status,
                "createdAt": notification.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for notification_id, notification, send_status in self._notifications
            if notification_type is None or notification.notification_type == notification_type
            if account_id is None or notification.account_id == account_id
            if strategy_id is None or notification.strategy_id == strategy_id
        ]
        start = (page - 1) * size
        end = start + size
        return PagedResult(list=rows[start:end], total=len(rows), page=page, size=size)

    def _type_label(self, notification_type: str) -> str:
        labels = {
            "risk_alert": "风险报警",
            "circuit_breaker": "熔断",
            "anomaly": "异常",
            "strategy_pause": "策略暂停",
            "manual_intervention": "人工干预",
            "email": "邮件",
            "system": "系统通知",
        }
        return labels.get(notification_type, notification_type)
