"""AssetSyncService 测试。

- mock 模式：验证资产与持仓同步调用链
- ``--real-db`` 模式：验证资产快照可写入真实数据库
"""

from datetime import datetime
from decimal import Decimal

import pytest

from common.models import ActivePosition
from execution.adapters import MockBrokerAdapter
from execution.services import AssetSyncService, InMemoryExecutionRepository
from infrastructure.db.repositories import AssetRepository


@pytest.mark.anyio
async def test_sync_asset_saves_asset_and_positions(db, using_real_db: bool):
    adapter = MockBrokerAdapter()
    adapter.positions = [
        ActivePosition(
            symbol_code="HK.00700",
            symbol_name="腾讯控股",
            open_price=Decimal("300"),
            current_price=Decimal("310"),
            holding_quantity=Decimal("100"),
            holding_amount=Decimal("31000"),
            open_time=datetime.now(),
            unrealized_pnl=Decimal("1000"),
            strategy_id="ma_cross",
        )
    ]
    repository = InMemoryExecutionRepository()
    asset_repository = AssetRepository(db) if using_real_db else repository
    service = AssetSyncService(adapter, repository, asset_repository=asset_repository)

    result = await service.sync_asset("ly", 1)
    assets = await repository.get_account_assets()
    positions = await repository.list_positions()

    assert result["status"] == "success"
    assert result["assetSynced"] is True
    assert result["positionCount"] == 1
    if using_real_db:
        stored_assets = await asset_repository.get_assets_by_range(
            "ly",
            1,
            datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999),
        )
        assert len(stored_assets) == 1
    else:
        assert assets["current"]["totalAsset"] == 1000000.0
    assert positions[0]["symbolCode"] == "HK.00700"


@pytest.mark.anyio
async def test_sync_asset_can_skip_positions(db, using_real_db: bool):
    repository = InMemoryExecutionRepository()
    asset_repository = AssetRepository(db) if using_real_db else repository
    service = AssetSyncService(MockBrokerAdapter(), repository, asset_repository=asset_repository)

    result = await service.sync_asset("ly", 1, sync_positions=False)
    positions = await repository.list_positions()

    assert result["positionsSynced"] is False
    assert result["positionCount"] == 0
    assert positions == []
