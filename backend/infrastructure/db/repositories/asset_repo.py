"""
asset 表（资产快照）的读写操作。

接口文档对应：
  - #6 sync_asset   执行层 → 数据库（按天同步资产）
  - #11 get_assets  数据库 → 数据分析层（时间范围查资产序列）

注意：asset 表不含 strategy_id，表名按 {account}_asset 格式。
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from common.models.asset import Asset
from common.interfaces.asset_repository import (
    AssetRepository as AssetRepositoryInterface,
)
from infrastructure.db.repositories.base_repo import BaseRepository


class AssetRepository(BaseRepository, AssetRepositoryInterface):
    """资产表的 Repository，按 {account}_asset 分表。"""

    TABLE_SUFFIX = "asset"

    # ── 写入 ────────────────────────────────────────────────────

    async def sync_asset(self, account_id: str, asset: Asset) -> int:
        return await asyncio.to_thread(self._sync_asset_sync, account_id, asset)

    def _sync_asset_sync(self, account_id: str, asset: Asset) -> int:
        """写入一条资产快照，返回自增 asset_id。

        按天定时由执行层同步触发，覆盖当天快照（应用层保证幂等）。
        """
        table = self._table_name(account_id)  # 无 strategy_id
        sql = (
            f"INSERT INTO {table} "
            f"(created_at, market_id, account_id, total_asset, net_value, "
            f"market_value, cash_balance) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            asset.created_at, asset.market_id, asset.account_id,
            asset.total_asset, asset.net_value,
            asset.market_value, asset.cash_balance,
        )

        try:
            with self._db.cnx.cursor() as cursor:
                cursor.execute(sql, params)
                asset_id = cursor.lastrowid
            self._db.commit()
        except Exception:
            self._db.cnx.rollback()
            raise
        return asset_id

    # ── 查询 ────────────────────────────────────────────────────

    async def get_assets_by_range(self, account_id: str, market_id: int,
                                  start_time: datetime, end_time: datetime
                                  ) -> list[Asset]:
        return await asyncio.to_thread(
            self._get_assets_by_range_sync,
            account_id,
            market_id,
            start_time,
            end_time,
        )

    def _get_assets_by_range_sync(self, account_id: str, market_id: int,
                                  start_time: datetime, end_time: datetime
                                  ) -> list[Asset]:
        """按时间范围查询资产序列。"""
        table = self._table_name(account_id)  # 无 strategy_id
        sql = (
            f"SELECT asset_id, created_at, market_id, account_id, "
            f"total_asset, net_value, market_value, cash_balance "
            f"FROM {table} "
            f"WHERE market_id = %s AND account_id = %s "
            f"AND created_at BETWEEN %s AND %s "
            f"ORDER BY created_at ASC"
        )
        rows = self._db.fetch_all(sql, (market_id, account_id, start_time, end_time))
        return [Asset(**row) for row in rows]
