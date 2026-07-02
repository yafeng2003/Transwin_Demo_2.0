from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from common.models import ActivePosition, Deal
from execution.adapters import MockBrokerAdapter
from execution.services import ExecutionPriceProvider, InMemoryExecutionRepository, PositionService


BASE_TIME = datetime(2026, 6, 1, 9, 30)


def make_deal(
    deal_id: int,
    deal_type: int,
    quantity: str,
    price: str,
    position_after: str,
) -> Deal:
    return Deal(
        deal_id=deal_id,
        operation_id=deal_id,
        market_id=1,
        account_id="acc_main",
        strategy_id="ma_cross",
        symbol_code="HK.00700",
        symbol_name="Tencent",
        deal_type=deal_type,
        direction=1,
        deal_price=Decimal(price),
        deal_quantity=Decimal(quantity),
        deal_amount=Decimal(price) * Decimal(quantity),
        position_after=Decimal(position_after),
        deal_time=BASE_TIME + timedelta(minutes=deal_id),
    )


@pytest.mark.anyio
async def test_execution_price_provider_fetches_prices():
    adapter = MockBrokerAdapter()
    adapter.market_prices = {
        "HK.00700": Decimal("310"),
        "HK.09988": Decimal("80"),
    }
    provider = ExecutionPriceProvider(adapter)

    prices = await provider.get_prices(1, ["HK.00700", "HK.00700", "HK.09988"], BASE_TIME)

    assert prices == {
        "HK.00700": Decimal("310"),
        "HK.09988": Decimal("80"),
    }
    assert adapter.connected is False


@pytest.mark.anyio
async def test_strategy_positions_are_reconstructed_from_deals():
    adapter = MockBrokerAdapter()
    adapter.market_prices = {"HK.00700": Decimal("12")}
    repository = InMemoryExecutionRepository()
    await repository.insert_deal(
        "acc_main",
        "ma_cross",
        make_deal(1, deal_type=1, quantity="100", price="10", position_after="100"),
    )
    await repository.insert_deal(
        "acc_main",
        "ma_cross",
        make_deal(2, deal_type=1, quantity="100", price="11", position_after="200"),
    )
    service = PositionService(adapter, repository)

    positions = await service.list_strategy_positions(1, "acc_main", "ma_cross", BASE_TIME + timedelta(days=1))

    assert len(positions) == 1
    assert positions[0]["symbolCode"] == "HK.00700"
    assert positions[0]["symbolName"] == "Tencent"
    assert positions[0]["openPrice"] == 10.5
    assert positions[0]["currentPrice"] == 12.0
    assert positions[0]["holdingQuantity"] == 200.0
    assert positions[0]["holdingAmount"] == 2400.0
    assert positions[0]["unrealizedPnl"] == 300.0


@pytest.mark.anyio
async def test_account_positions_are_queried_from_broker():
    adapter = MockBrokerAdapter()
    adapter.positions = [
        ActivePosition(
            symbol_code="HK.00700",
            symbol_name="Tencent",
            open_price=Decimal("300"),
            current_price=Decimal("310"),
            holding_quantity=Decimal("100"),
            holding_amount=Decimal("31000"),
            open_time=BASE_TIME,
            unrealized_pnl=Decimal("1000"),
            strategy_id="",
        )
    ]
    service = PositionService(adapter, InMemoryExecutionRepository())

    positions = await service.list_account_positions("acc_main", 1)

    assert len(positions) == 1
    assert positions[0]["symbolCode"] == "HK.00700"
    assert positions[0]["strategyId"] == ""
    assert positions[0]["holdingAmount"] == 31000.0
    assert adapter.connected is False
