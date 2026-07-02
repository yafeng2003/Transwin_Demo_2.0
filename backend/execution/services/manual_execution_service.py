"""手工交易服务。

用于处理前端手工买入、卖出和改单请求；下单结果成功时写成交，失败时向风控层上报事件。
"""

from decimal import Decimal

from common.interfaces import BrokerAdapter, DealRepository, RiskEventHandler
from common.models import Deal
from common.models import ModifyOrderRequest, OrderRequest, OrderSide, OrderType, RiskEvent
from execution.services.execution_repository import InMemoryExecutionRepository


class ManualExecutionService:
    """手工执行入口，面向 BrokerAdapter 与仓储接口编排交易流程。"""

    def __init__(
        self,
        adapter: BrokerAdapter,
        repository: InMemoryExecutionRepository | None = None,
        deal_repository: DealRepository | None = None,
        risk_handler: RiskEventHandler | None = None,
    ):
        self._adapter = adapter
        self._repository = repository or InMemoryExecutionRepository()
        self._deal_repository = deal_repository or self._repository
        self._risk_handler = risk_handler

    async def buy(
        self,
        market_id: int,
        account_id: str,
        symbol_code: str,
        order_type: int,
        price: Decimal | None,
        quantity: Decimal,
    ) -> dict:
        """发起手工买入委托。"""
        return await self._place_manual_order(market_id, account_id, symbol_code, OrderSide.BUY, order_type, price, quantity)

    async def sell(
        self,
        market_id: int,
        account_id: str,
        symbol_code: str,
        order_type: int,
        price: Decimal | None,
        quantity: Decimal,
    ) -> dict:
        """发起手工卖出委托。"""
        return await self._place_manual_order(market_id, account_id, symbol_code, OrderSide.SELL, order_type, price, quantity)

    async def modify_order(
        self,
        order_id: str,
        account_id: str,
        price: Decimal | None,
        quantity: Decimal | None,
    ) -> dict:
        """修改手工订单价格或数量。"""
        if price is None and quantity is None:
            raise ValueError("price or quantity is required")

        await self._adapter.connect()
        try:
            result = await self._adapter.modify_order(
                ModifyOrderRequest(order_id=order_id, account_id=account_id, price=price, quantity=quantity)
            )
        finally:
            await self._adapter.close()

        return {
            "orderId": result.order_id or order_id,
            "status": result.status,
            "message": result.message or "订单修改成功。",
            "modifyTime": result.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    async def _place_manual_order(
        self,
        market_id: int,
        account_id: str,
        symbol_code: str,
        side: OrderSide,
        order_type: int,
        price: Decimal | None,
        quantity: Decimal,
    ) -> dict:
        """组装手工订单请求，调用券商接口，并处理成交与风险上报。"""
        await self._adapter.connect()
        try:
            if side == OrderSide.SELL and quantity == Decimal("0"):
                quantity = await self._resolve_full_sell_quantity(account_id, market_id, symbol_code)
            request = OrderRequest(
                symbol_code=symbol_code,
                side=side,
                order_type=OrderType.MARKET if order_type == 1 else OrderType.LIMIT,
                quantity=quantity,
                price=price,
                market_id=market_id,
                account_id=account_id,
                remark="manual_order",
                is_manual=True,
            )
            result = await self._adapter.place_order(request)
            self._attach_order_context(result, request)
            await self._repository.save_order_result(result)
            if result.success:
                price = result.price or Decimal("0")
                deal = Deal(
                    deal_id=0,
                    operation_id=None,
                    market_id=market_id,
                    account_id=account_id,
                    strategy_id="manual",
                    symbol_code=symbol_code,
                    symbol_name="",
                    asset_type=1,
                    deal_type=1,
                    direction=1 if side == OrderSide.BUY else 2,
                    deal_price=price,
                    deal_quantity=result.quantity,
                    deal_amount=price * result.quantity,
                    commission=Decimal("0"),
                    position_after=Decimal("0"),
                    deal_time=result.created_at,
                    is_manual=1,
                )
                await self._deal_repository.insert_deal(account_id, "manual", deal)
        finally:
            await self._adapter.close()

        if not result.success and self._risk_handler is not None:
            await self._risk_handler.handle_risk_event(
                RiskEvent(
                    event_type="order_failed",
                    account_id=account_id,
                    strategy_id="manual",
                    symbol_code=symbol_code,
                    event_level=3,
                    event_message=result.message,
                )
            )

        return {
            "orderId": result.order_id,
            "status": result.status,
            "message": result.message or "委托已提交，等待成交确认。",
            "dealTime": result.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    async def _resolve_full_sell_quantity(self, account_id: str, market_id: int, symbol_code: str) -> Decimal:
        positions = await self._adapter.get_positions(account_id, market_id)
        for position in positions:
            if position.symbol_code == symbol_code and position.holding_quantity > Decimal("0"):
                return position.holding_quantity
        raise ValueError("no position available for full sell")

    def _attach_order_context(self, result, request: OrderRequest) -> None:
        result.raw = {
            **(result.raw or {}),
            "marketId": request.market_id,
            "accountId": request.account_id,
            "strategyId": request.strategy_id or "manual",
            "symbolName": "",
            "operationType": 1,
        }
