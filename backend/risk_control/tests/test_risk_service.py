"""RiskEventService 测试。

验证风险事件处理、通知触发和列表过滤逻辑。
"""

import pytest

from common.models import RiskEvent
from notification.services import MockNotificationSender
from risk_control.services import RiskEventService


@pytest.mark.anyio
async def test_handle_low_level_event_does_not_notify():
    sender = MockNotificationSender()
    service = RiskEventService(notification_sender=sender)

    response = await service.handle_risk_event(
        RiskEvent(
            event_type="order_failed",
            account_id="acc_main",
            strategy_id="ma_cross",
            symbol_code="HK.00700",
            event_level=2,
            event_message="下单失败",
        )
    )

    assert response.risk_event_id == 1
    assert response.status == "pending"
    assert sender.sent == []


@pytest.mark.anyio
async def test_handle_alert_event_sends_notification():
    sender = MockNotificationSender()
    service = RiskEventService(notification_sender=sender)

    await service.handle_risk_event(
        RiskEvent(
            event_type="order_failed",
            account_id="acc_main",
            strategy_id="ma_cross",
            symbol_code="HK.00700",
            event_level=3,
            event_message="下单失败",
        )
    )

    assert len(sender.sent) == 1
    assert sender.sent[0].notification_type == "risk_alert"


@pytest.mark.anyio
async def test_handle_level_five_event_is_processing():
    service = RiskEventService()

    response = await service.handle_risk_event(
        RiskEvent(
            event_type="api_error",
            account_id="acc_main",
            strategy_id="ma_cross",
            event_level=5,
            event_message="富途连接异常",
        )
    )

    assert response.status == "processing"


@pytest.mark.anyio
async def test_list_events_filters_by_type():
    service = RiskEventService()
    await service.handle_risk_event(
        RiskEvent(event_type="order_failed", account_id="a", strategy_id="s", event_level=2, event_message="A")
    )
    await service.handle_risk_event(
        RiskEvent(event_type="api_error", account_id="a", strategy_id="s", event_level=4, event_message="B")
    )

    result = await service.list_events(event_type="api_error")

    assert result.total == 1
    assert result.list[0]["eventType"] == "api_error"
