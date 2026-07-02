"""Position query services for strategy and account holdings."""

from datetime import datetime
from decimal import Decimal

from common.interfaces.broker_adapter import BrokerAdapter
from common.interfaces.deal_repository import DealRepository
from common.models import ActivePosition
from data_analysis.services.position_reconstructor import reconstruct_positions
from execution.services.price_provider import ExecutionPriceProvider


class PositionService:
    """Build strategy positions from deals and query account positions from broker."""

    def __init__(
        self,
        adapter: BrokerAdapter,
        deal_repository: DealRepository,
        price_provider: ExecutionPriceProvider | None = None,
    ):
        self._adapter = adapter
        self._deal_repository = deal_repository
        self._price_provider = price_provider or ExecutionPriceProvider(adapter)

    async def list_strategy_positions(
        self,
        market_id: int,
        account_id: str,
        strategy_id: str,
        query_time: datetime | None = None,
    ) -> list[dict]:
        query_time = query_time or datetime.now()
        deals = await self._deal_repository.get_deals_before(
            account_id,
            strategy_id,
            market_id,
            query_time,
        )
        symbols = sorted({deal.symbol_code for deal in deals})
        prices = await self._price_provider.get_prices(market_id, symbols, query_time)
        snapshot = reconstruct_positions(
            deals,
            market_id=market_id,
            account_id=account_id,
            strategy_id=strategy_id,
            query_time=query_time,
            prices=prices,
        )

        names = {deal.symbol_code: deal.symbol_name for deal in deals if deal.symbol_name}
        return [
            self._position_to_view(
                position,
                strategy_id=strategy_id,
                current_price=prices.get(position.symbol_code),
                symbol_name=names.get(position.symbol_code, position.symbol_name),
            )
            for position in snapshot.active_positions
        ]

    async def list_account_positions(self, account_id: str, market_id: int) -> list[dict]:
        await self._adapter.connect()
        try:
            positions = await self._adapter.get_positions(account_id, market_id)
        finally:
            await self._adapter.close()

        return [
            self._position_to_view(
                position,
                strategy_id=position.strategy_id,
                current_price=position.current_price,
                symbol_name=position.symbol_name,
            )
            for position in positions
        ]

    def _position_to_view(
        self,
        position: ActivePosition,
        strategy_id: str,
        current_price: Decimal | None,
        symbol_name: str,
    ) -> dict:
        price = current_price if current_price is not None else position.current_price
        price = price if price is not None else position.open_price
        market_value = price * position.holding_quantity
        unrealized_pnl = position.unrealized_pnl
        cost_amount = position.open_price * position.holding_quantity
        unrealized_rate = (
            unrealized_pnl / cost_amount * Decimal("100")
            if cost_amount != Decimal("0")
            else Decimal("0")
        )

        return {
            "symbolCode": position.symbol_code,
            "symbolName": symbol_name,
            "direction": position.direction,
            "openPrice": float(position.open_price),
            "currentPrice": float(price),
            "holdingQuantity": float(position.holding_quantity),
            "holdingAmount": float(market_value),
            "unrealizedPnl": float(unrealized_pnl),
            "unrealizedPnlRate": float(unrealized_rate),
            "openTime": position.open_time.strftime("%Y-%m-%d") if position.open_time else "",
            "strategyId": strategy_id,
        }
