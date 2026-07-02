"""ManualExecutionService 测试。

- mock 模式：验证手工下单与改单校验
- ``--real-db`` 模式：验证手工成交可写入真实成交表
"""

from datetime import datetime
from decimal import Decimal

import pytest

from common.models import ActivePosition
from execution.adapters import MockBrokerAdapter
from execution.services import InMemoryExecutionRepository, ManualExecutionService
from infrastructure.db.repositories import DealRepository


@pytest.mark.anyio
async def test_manual_buy_places_order(db, using_real_db: bool):
    adapter = MockBrokerAdapter()
    repository = InMemoryExecutionRepository()
    deal_repository = DealRepository(db) if using_real_db else repository
    service = ManualExecutionService(
        adapter,
        repository=repository,
        deal_repository=deal_repository,
    )

    result = await service.buy(1, "ly", "HK.00700", 1, None, Decimal("100"))

    assert result["status"] == "submitted"
    assert adapter.orders[0].symbol_code == "HK.00700"
    if using_real_db:
        deals = await deal_repository.get_deals_by_range(
            "ly",
            "manual",
            1,
            datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999),
        )
        assert len(deals) == 1


@pytest.mark.anyio
async def test_manual_modify_order_requires_change():
    service = ManualExecutionService(MockBrokerAdapter())

    with pytest.raises(ValueError):
        await service.modify_order("1", "acc_main", None, None)


@pytest.mark.anyio
async def test_manual_sell_zero_quantity_sells_full_position():
    adapter = MockBrokerAdapter()
    adapter.positions = [
        ActivePosition(
            symbol_code="HK.00700",
            symbol_name="腾讯控股",
            open_price=Decimal("300"),
            current_price=Decimal("310"),
            holding_quantity=Decimal("200"),
            holding_amount=Decimal("62000"),
            open_time=datetime.now(),
            unrealized_pnl=Decimal("2000"),
        )
    ]
    service = ManualExecutionService(adapter)

    result = await service.sell(1, "acc_main", "HK.00700", 1, None, Decimal("0"))

    assert result["status"] == "submitted"
    assert adapter.orders[0].quantity == Decimal("200")


@pytest.mark.anyio
async def test_manual_sell_zero_quantity_requires_position():
    service = ManualExecutionService(MockBrokerAdapter())

    with pytest.raises(ValueError):
        await service.sell(1, "acc_main", "HK.00700", 1, None, Decimal("0"))
