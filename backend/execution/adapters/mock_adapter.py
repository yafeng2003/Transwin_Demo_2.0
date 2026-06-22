"""模拟券商适配器。

用于单元测试和本地开发，提供可控的行情、持仓、下单返回值。
"""

from datetime import datetime
from decimal import Decimal

from common.interfaces import BrokerAdapter
from common.models import (
    ActivePosition,
    Asset,
    CancelOrderRequest,
    ModifyOrderRequest,
    OrderRequest,
    OrderResult,
)


class MockBrokerAdapter(BrokerAdapter):
    """BrokerAdapter 的内存模拟实现。"""

    def __init__(self, fail_place_order: bool = False):
        self.fail_place_order = fail_place_order
        self.connected = False
        self.orders: list[OrderRequest] = []
        self.positions: list[ActivePosition] = []
        self.market_prices: dict[str, Decimal] = {}
        self.lot_sizes: dict[str, int] = {}
        self.max_buy_quantities: dict[str, Decimal] = {}

    async def connect(self) -> None:
        """标记模拟连接已建立。"""
        self.connected = True

    async def close(self) -> None:
        """标记模拟连接已关闭。"""
        self.connected = False

    async def unlock(self) -> bool:
        return True

    async def get_account_assets(self, account_id: str, market_id: int) -> Asset:
        return Asset(
            created_at=datetime.now(),
            market_id=market_id,
            account_id=account_id,
            total_asset=Decimal("1000000"),
            net_value=Decimal("1"),
            market_value=Decimal("0"),
            cash_balance=Decimal("1000000"),
        )

    async def get_positions(self, account_id: str, market_id: int) -> list[ActivePosition]:
        return self.positions

    async def get_market_price(self, symbol_code: str) -> Decimal | None:
        return self.market_prices.get(symbol_code, Decimal("10"))

    async def get_lot_size(self, symbol_code: str) -> int:
        return self.lot_sizes.get(symbol_code, 100)

    async def get_max_buy_quantity(self, symbol_code: str, price: Decimal) -> Decimal | None:
        return self.max_buy_quantities.get(symbol_code, Decimal("100000"))

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """记录订单并按配置返回成功或失败结果。"""
        self.orders.append(order)
        if self.fail_place_order:
            return OrderResult(
                success=False,
                symbol_code=order.symbol_code,
                side=order.side,
                order_type=order.order_type,
                quantity=order.quantity,
                price=order.price,
                status="failed",
                message="mock place_order failed",
            )
        return OrderResult(
            success=True,
            order_id=f"MOCK-{len(self.orders)}",
            symbol_code=order.symbol_code,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price,
            status="submitted",
            message="submitted",
        )

    async def cancel_order(self, request: CancelOrderRequest) -> OrderResult:
        return OrderResult(
            success=True,
            order_id=request.order_id,
            symbol_code="",
            side="BUY",
            order_type="MARKET",
            quantity=Decimal("0.0001"),
            status="cancelled",
        )

    async def modify_order(self, request: ModifyOrderRequest) -> OrderResult:
        return OrderResult(
            success=True,
            order_id=request.order_id,
            symbol_code="",
            side="BUY",
            order_type="MARKET",
            quantity=request.quantity or Decimal("0.0001"),
            price=request.price,
            status="modified",
        )

    async def query_order(self, order_id: str) -> OrderResult | None:
        return None
