"""通知服务。

负责记录通知发送状态，并可委托外部发送器实际发送邮件、短信或其他渠道通知。
"""

from common.interfaces import NotificationRepository, RiskNotificationSender
from common.models import PagedResult, RiskNotification
from notification.services.notification_repository import InMemoryNotificationRepository


class NotificationService(RiskNotificationSender):
    """通知层业务入口，实现 RiskNotificationSender 供风控层依赖注入。"""

    def __init__(
        self,
        repository: NotificationRepository | None = None,
        email_sender: RiskNotificationSender | None = None,
    ):
        self._repository = repository or InMemoryNotificationRepository()
        self._email_sender = email_sender

    async def send_risk_notification(self, notification: RiskNotification) -> int:
        """发送风险通知并记录 success / failed / skipped 状态。"""
        send_status = "skipped"
        if self._email_sender is not None:
            try:
                await self._email_sender.send_risk_notification(notification)
                send_status = "success"
            except Exception:
                send_status = "failed"

        return await self._repository.save_notification(notification, send_status)

    async def list_notifications(
        self,
        notification_type: str | None = None,
        page: int = 1,
        size: int = 20,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> PagedResult[dict]:
        """分页查询通知记录。"""
        return await self._repository.list_notifications(
            notification_type=notification_type,
            page=page,
            size=size,
            account_id=account_id,
            strategy_id=strategy_id,
        )
