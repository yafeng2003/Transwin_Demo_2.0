"""Execution-layer price provider for analysis services."""

from datetime import datetime
from decimal import Decimal

from common.interfaces.analysis_interface import PriceProvider
from common.interfaces.broker_adapter import BrokerAdapter


class ExecutionPriceProvider(PriceProvider):
    """Fetch latest prices through the configured broker adapter."""

    def __init__(self, adapter: BrokerAdapter):
        self._adapter = adapter

    async def get_prices(
        self,
        market_id: int,
        symbol_codes: list[str],
        as_of: datetime,
    ) -> dict[str, Decimal]:
        prices: dict[str, Decimal] = {}
        if not symbol_codes:
            return prices

        await self._adapter.connect()
        try:
            for symbol_code in dict.fromkeys(symbol_codes):
                price = await self._adapter.get_market_price(symbol_code)
                if price is not None:
                    prices[symbol_code] = price
        finally:
            await self._adapter.close()

        return prices
