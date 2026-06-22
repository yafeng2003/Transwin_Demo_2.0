
from datetime import datetime

from common.interfaces.risk_interface import RiskEventHandler
from common.models.risk_event import RiskEvent, RiskEventResponse


class OrderExecutor:

    def __init__(self, risk_handler: RiskEventHandler):
        self._risk_handler = risk_handler

    async def execute_order(self, order_id: int, symbol: str, quantity: float) -> bool:
        try:
            success = await self._place_order_to_exchange(order_id, symbol, quantity)

            if not success:
                event = RiskEvent(
                    event_type="order_failure",
                    account_id="acc_001",
                    strategy_id="ma_strategy",
                    symbol_code=symbol,
                    event_level=2,
                    event_message=f"订单 {order_id} 提交失败：交易所拒单",
                    occur_time=datetime.now(),
                )
                response: RiskEventResponse = await self._risk_handler.handle_risk_event(event)

                if response.status == "escalated":
                    print(f"风控紧急响应：{response.risk_event_id}")
                return False

            return True

        except ConnectionError as e:
            event = RiskEvent(
                event_type="api_abnormal",
                account_id="acc_001",
                strategy_id="ma_strategy",
                symbol_code=symbol,
                event_level=4,
                event_message=f"交易所 API 连接失败：{e}",
                occur_time=datetime.now(),
            )
            await self._risk_handler.handle_risk_event(event)
            raise

    async def _place_order_to_exchange(self, order_id: int, symbol: str, quantity: float) -> bool:
        return True
