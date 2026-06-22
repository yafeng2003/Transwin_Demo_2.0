
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from common.models.risk_event import RiskEvent, RiskEventResponse
from risk_control.services.risk_service import RiskEventServiceImpl


class TestRiskEventServiceImpl:

    @pytest.fixture
    def service(self):
        return RiskEventServiceImpl(
            db_session=AsyncMock(),
            notification_service=AsyncMock(),
        )

    async def test_handle_risk_event_basic(self, service):
        event = RiskEvent(
            event_type="order_failure",
            account_id="acc_001",
            strategy_id="ma_strategy",
            symbol_code="600001.SH",
            event_level=1,
            event_message="下单失败：余额不足",
            occur_time=datetime.now(),
        )

        response = await service.handle_risk_event(event)

        assert isinstance(response, RiskEventResponse)
        assert response.risk_event_id > 0
        assert response.status == "received"

    async def test_handle_risk_event_alert(self, service):
        event = RiskEvent(
            event_type="drawdown_exceeded",
            account_id="acc_001",
            strategy_id="ma_strategy",
            symbol_code="600001.SH",
            event_level=3,
            event_message="单日回撤超限",
            occur_time=datetime.now(),
        )

        response = await service.handle_risk_event(event)

        assert response.status == "received"
        service._notifier.send_risk_notification.assert_awaited_once()

    async def test_handle_risk_event_escalated(self, service):
        event = RiskEvent(
            event_type="api_abnormal",
            account_id="acc_001",
            strategy_id="ma_strategy",
            symbol_code=None,
            event_level=5,
            event_message="交易所 API 连续异常，系统可能失联",
            occur_time=datetime.now(),
        )

        response = await service.handle_risk_event(event)

        assert response.status == "escalated"
        service._notifier.send_risk_notification.assert_awaited_once()

    async def test_handle_risk_event_no_notifier(self):
        service = RiskEventServiceImpl(db_session=AsyncMock(), notification_service=None)

        event = RiskEvent(
            event_type="order_failure",
            account_id="acc_001",
            strategy_id="ma_strategy",
            symbol_code="600001.SH",
            event_level=4,
            event_message="连续 5 次下单失败",
            occur_time=datetime.now(),
        )

        response = await service.handle_risk_event(event)

        assert response.status == "received"
        assert response.risk_event_id > 0

    async def test_handle_risk_event_db_failure(self):
        mock_db = AsyncMock()
        mock_db.begin.side_effect = Exception("数据库连接断开")
        service = RiskEventServiceImpl(db_session=mock_db, notification_service=None)

        event = RiskEvent(
            event_type="position_abnormal",
            account_id="acc_001",
            strategy_id="ma_strategy",
            symbol_code="600001.SH",
            event_level=2,
            event_message="持仓数量异常跳变",
            occur_time=datetime.now(),
        )

        response = await service.handle_risk_event(event)

        assert response.status == "received"
        assert response.risk_event_id > 0

    async def test_event_level_boundary(self, service):
        event = RiskEvent(
            event_type="order_failure",
            account_id="acc_001",
            strategy_id="ma_strategy",
            symbol_code="600001.SH",
            event_level=2,
            event_message="下单失败：非严重",
            occur_time=datetime.now(),
        )

        await service.handle_risk_event(event)

        service._notifier.send_risk_notification.assert_not_awaited()
