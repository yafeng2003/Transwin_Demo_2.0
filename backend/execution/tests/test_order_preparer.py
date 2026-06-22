"""OrderPreparer 测试。

验证 lot size 调整、可买数量限制和大额拆单规则。
"""

from datetime import datetime
from decimal import Decimal

import pytest

from common.config import ExecutionSettings
from common.models import Operation
from execution.adapters import MockBrokerAdapter
from execution.services import OrderPreparer


def make_operation(quantity: Decimal, operation_type: int = 1) -> Operation:
    return Operation(
        operation_id=1,
        market_id=2,
        account_id="acc_main",
        strategy_id="ma_cross",
        symbol_code="HK.00700",
        symbol_name="腾讯控股",
        asset_type=1,
        operation_type=operation_type,
        direction=1,
        order_type=1,
        price=Decimal("0"),
        quantity=quantity,
        created_at=datetime.now(),
        status=0,
    )


@pytest.mark.anyio
async def test_prepare_rejects_quantity_below_lot():
    adapter = MockBrokerAdapter()
    adapter.lot_sizes["HK.00700"] = 100
    preparer = OrderPreparer(adapter)

    requests, reason = await preparer.prepare(make_operation(Decimal("50")))

    assert requests == []
    assert reason == "qty_below_lot"


@pytest.mark.anyio
async def test_prepare_adjusts_quantity_to_lot():
    adapter = MockBrokerAdapter()
    adapter.lot_sizes["HK.00700"] = 100
    preparer = OrderPreparer(adapter)

    requests, reason = await preparer.prepare(make_operation(Decimal("250")))

    assert reason == "ok"
    assert requests[0].quantity == Decimal("200")


@pytest.mark.anyio
async def test_prepare_caps_buy_quantity_by_max_buy():
    adapter = MockBrokerAdapter()
    adapter.lot_sizes["HK.00700"] = 100
    adapter.max_buy_quantities["HK.00700"] = Decimal("300")
    preparer = OrderPreparer(adapter)

    requests, reason = await preparer.prepare(make_operation(Decimal("1000")))

    assert reason == "ok"
    assert sum(request.quantity for request in requests) == Decimal("300")


@pytest.mark.anyio
async def test_prepare_splits_large_order():
    adapter = MockBrokerAdapter()
    adapter.lot_sizes["HK.00700"] = 100
    preparer = OrderPreparer(
        adapter,
        ExecutionSettings(split_base_size=1000, split_min_count=3, split_max_count=5, split_interval_seconds=0),
    )

    requests, reason = await preparer.prepare(make_operation(Decimal("3000")))

    assert reason == "ok"
    assert len(requests) == 3
    assert sum(request.quantity for request in requests) == Decimal("3000")
