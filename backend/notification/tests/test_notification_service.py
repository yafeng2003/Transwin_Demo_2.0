"""NotificationService 测试。

验证通知发送状态记录和通知列表过滤逻辑。
"""

from datetime import datetime

import pytest

from common.models import RiskNotification
from notification.services import MockNotificationSender, NotificationService


@pytest.mark.anyio
async def test_send_risk_notification_records_success():
    sender = MockNotificationSender()
    service = NotificationService(email_sender=sender)

    notification = RiskNotification(
        notification_type="risk_alert",
        risk_level=3,
        title="风险报警",
        content="下单失败",
        created_at=datetime.now(),
    )

    notification_id = await service.send_risk_notification(notification)

    assert notification_id == 1
    assert len(sender.sent) == 1


@pytest.mark.anyio
async def test_send_risk_notification_records_failed_status():
    service = NotificationService(email_sender=MockNotificationSender(should_fail=True))

    notification = RiskNotification(
        notification_type="risk_alert",
        risk_level=3,
        title="风险报警",
        content="下单失败",
        created_at=datetime.now(),
    )

    notification_id = await service.send_risk_notification(notification)
    result = await service.list_notifications()

    assert notification_id == 1
    assert result.list[0]["sendStatus"] == "failed"


@pytest.mark.anyio
async def test_list_notifications_filters_by_type():
    service = NotificationService()
    await service.send_risk_notification(
        RiskNotification(notification_type="risk_alert", risk_level=3, title="A", content="A")
    )
    await service.send_risk_notification(
        RiskNotification(notification_type="system", risk_level=1, title="B", content="B")
    )

    result = await service.list_notifications(notification_type="risk_alert")

    assert result.total == 1
    assert result.list[0]["type"] == "risk_alert"
