"""AssetRepository 测试。

- mock 模式（默认）：验证参数传递与调用逻辑。
- ``--real-db`` 模式：验证真实 SQL 执行与数据读写。
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from common.models.asset import Asset
from infrastructure.db.repositories.asset_repo import AssetRepository


@pytest.mark.anyio
class TestSyncAsset:
    """写入资产快照。"""

    async def test_sync(self, db, sample_asset: Asset) -> None:
        repo = AssetRepository(db)

        asset_id = await repo.sync_asset("ly", sample_asset)

        assert asset_id > 0

    @pytest.mark.mock_only
    async def test_rollback_on_failure(
        self, mock_db: MagicMock, sample_asset: Asset
    ) -> None:
        mock_db.cnx.cursor.return_value.__enter__.return_value.execute.side_effect = (
            RuntimeError("sync error")
        )
        repo = AssetRepository(mock_db)

        with pytest.raises(RuntimeError):
            await repo.sync_asset("ly", sample_asset)

        mock_db.cnx.rollback.assert_called_once()

    @pytest.mark.mock_only
    async def test_uses_asset_table(
        self, mock_db: MagicMock, sample_asset: Asset
    ) -> None:
        """asset 表不含 strategy_id，只传 account_id。"""
        repo = AssetRepository(mock_db)

        await repo.sync_asset("ly", sample_asset)

        sql = mock_db.cnx.cursor.return_value.__enter__.return_value.execute.call_args[0][0]
        assert "ly_asset" in sql or "`ly_asset`" in sql
        assert "maop" not in sql


@pytest.mark.anyio
class TestGetAssetsByRange:
    """按时间范围查询资产序列。"""

    async def test_returns_assets(
        self, db, sample_asset: Asset, using_real_db: bool
    ) -> None:
        start = datetime(2026, 6, 1)
        end = datetime(2026, 6, 30)
        repo = AssetRepository(db)

        if using_real_db:
            await repo.sync_asset("ly", sample_asset)
        else:
            db.fetch_all.return_value = [
                {
                    "asset_id": 1,
                    "created_at": "2026-06-01 15:00:00",
                    "market_id": 1,
                    "account_id": "ly",
                    "total_asset": 150000.00,
                    "net_value": 1.05,
                    "market_value": 120000.00,
                    "cash_balance": 30000.00,
                }
            ]

        assets = await repo.get_assets_by_range("ly", 1, start, end)

        assert len(assets) == 1
        assert isinstance(assets[0], Asset)
        assert assets[0].total_asset is not None

    async def test_empty(self, db) -> None:
        repo = AssetRepository(db)

        assets = await repo.get_assets_by_range(
            "ly", 1, datetime(2020, 1, 1), datetime(2020, 1, 2)
        )

        assert assets == []
