"""富途券商适配器。

将执行层 BrokerAdapter 接口适配到 futu-openapi；业务层只依赖抽象接口，不直接依赖 futu 包。
"""

from datetime import datetime
from decimal import Decimal

from common.config import FutuSettings, load_futu_settings
from common.interfaces import BrokerAdapter
from common.models import (
    ActivePosition,
    Asset,
    CancelOrderRequest,
    ModifyOrderRequest,
    OrderRequest,
    OrderResult,
    OrderSide,
    OrderType,
)


class FutuBrokerAdapter(BrokerAdapter):
    """基于 futu-openapi 的真实券商适配实现。"""

    def __init__(self, settings: FutuSettings | None = None):
        self._settings = settings or load_futu_settings()
        self._quote_context = None
        self._trade_context = None
        self._futu = None

    async def connect(self) -> None:
        """初始化行情和交易上下文。"""
        try:
            import futu
        except ImportError as exc:
            raise RuntimeError("futu package is not installed") from exc

        self._futu = futu
        self._quote_context = futu.OpenQuoteContext(host=self._settings.host, port=self._settings.port)
        self._trade_context = futu.OpenSecTradeContext(
            filter_trdmarket=getattr(futu.TrdMarket, self._settings.trading_market),
            host=self._settings.host,
            port=self._settings.port,
            security_firm=getattr(futu.SecurityFirm, self._settings.security_firm),
        )

    async def close(self) -> None:
        """关闭已创建的 futu 上下文。"""
        for ctx in [self._quote_context, self._trade_context]:
            if ctx is not None:
                ctx.close()

    async def unlock(self) -> bool:
        """真实交易环境下解锁交易，模拟环境直接通过。"""
        self._ensure_connected()
        if self._settings.trading_env.upper() != "REAL":
            return True

        ret, data = self._trade_context.unlock_trade(self._settings.trading_pwd)
        return ret == self._futu.RET_OK

    async def get_account_assets(self, account_id: str, market_id: int) -> Asset:
        """查询账户资产并转换为领域模型。"""
        self._ensure_connected()
        ret, data = self._trade_context.accinfo_query(trd_env=self._trd_env())
        if ret != self._futu.RET_OK:
            raise RuntimeError(f"account query failed: {data}")

        return Asset(
            created_at=datetime.now(),
            market_id=market_id,
            account_id=account_id,
            total_asset=Decimal(str(data["total_assets"][0])),
            net_value=Decimal("1"),
            market_value=Decimal(str(data["market_val"][0])),
            cash_balance=Decimal(str(data["cash"][0])),
        )

    async def get_positions(self, account_id: str, market_id: int) -> list[ActivePosition]:
        """查询当前持仓并转换为领域模型列表。"""
        self._ensure_connected()
        ret, data = self._trade_context.position_list_query(trd_env=self._trd_env())
        if ret != self._futu.RET_OK:
            raise RuntimeError(f"position query failed: {data}")
        if data.empty:
            return []

        positions: list[ActivePosition] = []
        for _, row in data.iterrows():
            qty = Decimal(str(row["qty"]))
            if qty <= 0:
                continue
            current_price = Decimal(str(row.get("nominal_price", 0)))
            positions.append(
                ActivePosition(
                    symbol_code=row["code"],
                    symbol_name=row.get("stock_name", ""),
                    open_price=Decimal(str(row.get("cost_price", 0))),
                    current_price=current_price,
                    holding_quantity=qty,
                    holding_amount=qty * current_price,
                    unrealized_pnl=Decimal(str(row.get("pl_val", 0))),
                )
            )
        return positions

    async def get_market_price(self, symbol_code: str) -> Decimal | None:
        self._ensure_connected()
        ret, data = self._quote_context.get_market_snapshot([symbol_code])
        if ret != self._futu.RET_OK:
            return None
        return Decimal(str(data["last_price"][0]))

    async def get_lot_size(self, symbol_code: str) -> int:
        self._ensure_connected()
        ret, data = self._quote_context.get_market_snapshot([symbol_code])
        if ret != self._futu.RET_OK:
            raise RuntimeError(f"lot size query failed: {data}")
        return int(data["lot_size"][0])

    async def get_max_buy_quantity(self, symbol_code: str, price: Decimal) -> Decimal | None:
        self._ensure_connected()
        ret, data = self._trade_context.acctradinginfo_query(
            order_type=self._futu.OrderType.NORMAL,
            code=symbol_code,
            price=float(price),
            trd_env=self._trd_env(),
        )
        if ret != self._futu.RET_OK:
            return None
        return Decimal(str(data.iloc[0]["max_cash_and_margin_buy"]))

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """提交订单并统一转换为 OrderResult。"""
        self._ensure_connected()
        ret, data = self._trade_context.place_order(
            price=float(order.price or 0),
            qty=float(order.quantity),
            code=order.symbol_code,
            trd_side=self._trd_side(order.side),
            order_type=self._order_type(order.order_type),
            trd_env=self._trd_env(),
            remark=order.remark,
        )
        if ret != self._futu.RET_OK:
            return OrderResult(
                success=False,
                symbol_code=order.symbol_code,
                side=order.side,
                order_type=order.order_type,
                quantity=order.quantity,
                price=order.price,
                status="failed",
                message=str(data),
            )

        return OrderResult(
            success=True,
            order_id=str(data["order_id"][0]),
            symbol_code=order.symbol_code,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price,
            status="submitted",
            message="submitted",
        )

    async def cancel_order(self, request: CancelOrderRequest) -> OrderResult:
        raise NotImplementedError("Futu cancel_order will be implemented after order id mapping is finalized")

    async def modify_order(self, request: ModifyOrderRequest) -> OrderResult:
        if request.price is None and request.quantity is None:
            raise ValueError("price or quantity is required")
        raise NotImplementedError("Futu modify_order will be implemented after order id mapping is finalized")

    async def query_order(self, order_id: str) -> OrderResult | None:
        return None

    def _ensure_connected(self) -> None:
        if self._quote_context is None or self._trade_context is None or self._futu is None:
            raise RuntimeError("futu adapter is not connected")

    def _trd_env(self):
        return getattr(self._futu.TrdEnv, self._settings.trading_env.upper())

    def _trd_side(self, side: OrderSide):
        return self._futu.TrdSide.BUY if side == OrderSide.BUY else self._futu.TrdSide.SELL

    def _order_type(self, order_type: OrderType):
        return self._futu.OrderType.MARKET if order_type == OrderType.MARKET else self._futu.OrderType.NORMAL
