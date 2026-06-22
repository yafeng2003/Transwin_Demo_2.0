"""OrderExecutor 测试。

- mock 模式：验证待执行操作、下单和风控上报链路
- ``--real-db`` 模式：验证执行结果可写入数据库仓储
"""

from datetime import datetime
from decimal import Decimal

import pytest

from common.models import Operation
from execution.adapters import MockBrokerAdapter
from execution.services import InMemoryExecutionRepository, OrderExecutor
from infrastructure.db.repositories import (
    AssetRepository,
    DealRepository,
    OperationRepository,
)
from risk_control.services import RiskEventService


def make_operation() -> Operation:
    return Operation(
        operation_id=1,
        market_id=1,
        account_id="ly",
        strategy_id="maop",
        symbol_code="HK.00700",
        symbol_name="腾讯控股",
        asset_type=1,
        operation_type=1,
        direction=1,
        order_type=1,
        price=Decimal("0"),
        quantity=Decimal("100"),
        created_at=datetime.now(),
        status=0,
    )


@pytest.mark.anyio
async def test_execute_pending_operations_success(db, using_real_db: bool):
    repository = InMemoryExecutionRepository()
    operation_repository = repository
    deal_repository = repository
    asset_repository = repository
    if using_real_db:
        operation_repository = OperationRepository(db)
        deal_repository = DealRepository(db)
        asset_repository = AssetRepository(db)
        await operation_repository.insert_operations("ly", "maop", [make_operation()])
    else:
        await repository.add_operation(make_operation())

    adapter = MockBrokerAdapter()
    executor = OrderExecutor(
        adapter=adapter,
        repository=repository,
        operation_repository=operation_repository,
        deal_repository=deal_repository,
        asset_repository=asset_repository,
    )

    result = await executor.execute_pending_operations(market_id=1, account_id="ly", strategy_id="maop")

    assert result["status"] == "success"
    assert result["success"] == 1
    if using_real_db:
        deals = await deal_repository.get_deals_by_range(
            "ly",
            "maop",
            1,
            datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999),
        )
        assert len(deals) == 1


@pytest.mark.anyio
async def test_execute_pending_operations_reports_risk_on_failure(db, using_real_db: bool):
    repository = InMemoryExecutionRepository()
    operation_repository = repository
    deal_repository = repository
    asset_repository = repository
    if using_real_db:
        operation_repository = OperationRepository(db)
        deal_repository = DealRepository(db)
        asset_repository = AssetRepository(db)
        await operation_repository.insert_operations("ly", "maop", [make_operation()])
    else:
        await repository.add_operation(make_operation())

    risk_service = RiskEventService()
    adapter = MockBrokerAdapter(fail_place_order=True)
    executor = OrderExecutor(
        adapter=adapter,
        repository=repository,
        operation_repository=operation_repository,
        deal_repository=deal_repository,
        asset_repository=asset_repository,
        risk_handler=risk_service,
    )

    result = await executor.execute_pending_operations(market_id=1, account_id="ly", strategy_id="maop")
    events = await risk_service.list_events()

    assert result["status"] == "failed"
    assert events.total == 1
    assert events.list[0]["eventType"] == "order_failed"
