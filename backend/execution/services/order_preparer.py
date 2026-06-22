"""订单准备服务。

把策略层生成的 Operation 按交易约束转换为一个或多个可提交给券商的 OrderRequest。
"""

from decimal import Decimal

from common.config import ExecutionSettings, load_execution_settings
from common.interfaces import BrokerAdapter
from common.models import Operation, OrderRequest, OrderSide, OrderType


class OrderPreparer:
    """执行前校验、数量调整和拆单逻辑。"""

    def __init__(self, adapter: BrokerAdapter, settings: ExecutionSettings | None = None):
        self._adapter = adapter
        self._settings = settings or load_execution_settings()

    async def prepare(self, operation: Operation) -> tuple[list[OrderRequest], str]:
        """根据 lot size、可买数量和拆单配置生成订单请求列表。"""
        side = OrderSide.BUY if operation.operation_type == 1 else OrderSide.SELL
        order_type = OrderType.MARKET if operation.order_type == 1 else OrderType.LIMIT
        lot_size = await self._adapter.get_lot_size(operation.symbol_code)
        quantity = self._adjust_to_lot(operation.quantity, lot_size)
        if quantity <= 0:
            return [], "qty_below_lot"

        price = None if order_type == OrderType.MARKET else operation.price
        if side == OrderSide.BUY:
            market_price = await self._adapter.get_market_price(operation.symbol_code)
            if market_price is None or market_price <= 0:
                return [], "price_unavailable"

            max_buy_quantity = await self._adapter.get_max_buy_quantity(operation.symbol_code, market_price)
            if max_buy_quantity is None:
                return [], "max_buy_query_failed"

            max_buy_quantity = self._adjust_to_lot(max_buy_quantity, lot_size)
            if max_buy_quantity <= 0:
                return [], "max_buy_zero"
            quantity = min(quantity, max_buy_quantity)

        split_quantities = self._split_quantity(quantity, lot_size)
        requests = [
            OrderRequest(
                symbol_code=operation.symbol_code,
                side=side,
                order_type=order_type,
                quantity=split_quantity,
                price=price,
                market_id=operation.market_id,
                account_id=operation.account_id,
                strategy_id=operation.strategy_id,
                operation_id=operation.operation_id,
                remark=f"operation_{operation.operation_id}_{index}",
            )
            for index, split_quantity in enumerate(split_quantities, 1)
        ]
        return requests, "ok"

    def _adjust_to_lot(self, quantity: Decimal, lot_size: int) -> Decimal:
        """将数量向下调整到 lot size 的整数倍。"""
        if lot_size <= 0:
            return Decimal("0")
        adjusted = int(quantity) // lot_size * lot_size
        return Decimal(adjusted)

    def _split_quantity(self, quantity: Decimal, lot_size: int) -> list[Decimal]:
        """按配置拆分大额订单，并保证每笔数量符合 lot size。"""
        total_quantity = int(quantity)
        if total_quantity <= self._settings.split_base_size:
            return [Decimal(total_quantity)]

        split_count = min(
            self._settings.split_max_count,
            max(self._settings.split_min_count, total_quantity // self._settings.split_base_size),
        )
        sub_quantity = total_quantity // split_count // lot_size * lot_size
        if sub_quantity <= 0:
            sub_quantity = lot_size

        orders: list[Decimal] = []
        remaining = total_quantity
        for _ in range(split_count - 1):
            if sub_quantity <= remaining:
                orders.append(Decimal(sub_quantity))
                remaining -= sub_quantity

        final_quantity = remaining // lot_size * lot_size
        if final_quantity > 0:
            orders.append(Decimal(final_quantity))
        return orders
