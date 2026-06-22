
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from common.models.risk_event import RiskEvent, RiskEventResponse
from execution.services.order_executor import OrderExecutor


class TestOrderExecutor:

    @pytest.fixture
    def mock_risk_handler(self):
        from common.interfaces.risk_interface import RiskEventHandler

        mock = AsyncMock(spec=RiskEventHandler)
        mock.handle_risk_event = AsyncMock(return_value=RiskEventResponse(
            risk_event_id=1001,
            status="received",
        ))
        return mock

    @pytest.fixture
    def executor(self, mock_risk_handler) -> OrderExecutor:
        return OrderExecutor(risk_handler=mock_risk_handler)

    async def test_execute_order_success(self, executor, mock_risk_handler):
        result = await executor.execute_order(order_id=1, symbol="600001.SH", quantity=100)

        assert result is True
        mock_risk_handler.handle_risk_event.assert_not_awaited()

    async def test_execute_order_failure_triggers_risk_event(self, executor, mock_risk_handler):
        executor._place_order_to_exchange = AsyncMock(return_value=False)

        result = await executor.execute_order(order_id=1, symbol="600001.SH", quantity=100)

        assert result is False
        mock_risk_handler.handle_risk_event.assert_awaited_once()

        called_event: RiskEvent = mock_risk_handler.handle_risk_event.await_args[0][0]
        assert called_event.event_type == "order_failure"
        assert called_event.symbol_code == "600001.SH"
        assert called_event.event_level == 2

    async def test_execute_order_escalated_response(self, executor, mock_risk_handler):
        executor._place_order_to_exchange = AsyncMock(return_value=False)
        mock_risk_handler.handle_risk_event.return_value = RiskEventResponse(
            risk_event_id=1002,
            status="escalated",
        )

        result = await executor.execute_order(order_id=1, symbol="600001.SH", quantity=100)
        assert result is False

    async def test_execute_order_network_error(self, executor, mock_risk_handler):
        executor._place_order_to_exchange = AsyncMock(side_effect=ConnectionError("连接超时"))

        with pytest.raises(ConnectionError):
            await executor.execute_order(order_id=1, symbol="600001.SH", quantity=100)

        mock_risk_handler.handle_risk_event.assert_awaited_once()
        called_event = mock_risk_handler.handle_risk_event.await_args[0][0]
        assert called_event.event_type == "api_abnormal"
        assert called_event.event_level == 4
