"""
deal 表（成交记录）的读写操作。

接口文档对应：
  - #5 insert_deal_record  执行层 → 数据库
  - #2 get_strategy_deals  数据库 → 策略层（策略生成需要的历史成交）
  - #10 get_deals          数据库 → 数据分析层
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from common.models.deal import Deal
from common.interfaces.deal_repository import (
    DealRepository as DealRepositoryInterface,
)
from infrastructure.db.repositories.base_repo import BaseRepository


class DealRepository(BaseRepository, DealRepositoryInterface):
    """成交记录表的 Repository，按 {account}_{strategy}_deal 分表。"""

    TABLE_SUFFIX = "deal"

    # ── 写入 ────────────────────────────────────────────────────

    async def insert_deal(self, account_id: str, strategy_id: str,
                          deal: Deal) -> int:
        return await asyncio.to_thread(
            self._insert_deal_sync, account_id, strategy_id, deal
        )

    def _insert_deal_sync(self, account_id: str, strategy_id: str,
                          deal: Deal) -> int:
        """写入一条成交记录，返回自增 deal_id。"""
        table = self._table_name(account_id, strategy_id)
        sql = (
            f"INSERT INTO {table} "
            f"(operation_id, market_id, account_id, strategy_id, "
            f"symbol_code, symbol_name, asset_type, deal_type, direction, "
            f"deal_price, deal_quantity, deal_amount, commission, "
            f"position_after, is_manual, deal_time) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, "
            f"%s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            deal.operation_id, deal.market_id, deal.account_id,
            deal.strategy_id, deal.symbol_code, deal.symbol_name,
            deal.asset_type, deal.deal_type, deal.direction,
            deal.deal_price, deal.deal_quantity, deal.deal_amount,
            deal.commission, deal.position_after, deal.is_manual,
            deal.deal_time,
        )

        try:
            with self._db.cnx.cursor() as cursor:
                cursor.execute(sql, params)
                deal_id = cursor.lastrowid
            self._db.commit()
        except Exception:
            self._db.cnx.rollback()
            raise
        return deal_id

    # ── 查询 ────────────────────────────────────────────────────

    async def get_deals_before(self, account_id: str, strategy_id: str,
                               market_id: int, current_time: datetime
                               ) -> list[Deal]:
        return await asyncio.to_thread(
            self._get_deals_before_sync,
            account_id,
            strategy_id,
            market_id,
            current_time,
        )

    def _get_deals_before_sync(self, account_id: str, strategy_id: str,
                               market_id: int, current_time: datetime
                               ) -> list[Deal]:
        """查询某策略在指定时间前的所有成交记录（策略层用）。"""
        table = self._table_name(account_id, strategy_id)
        sql = (
            f"SELECT deal_id, operation_id, market_id, account_id, "
            f"strategy_id, symbol_code, symbol_name, asset_type, deal_type, "
            f"direction, deal_price, deal_quantity, deal_amount, commission, "
            f"position_after, is_manual, deal_time "
            f"FROM {table} "
            f"WHERE market_id = %s AND account_id = %s "
            f"AND strategy_id = %s AND deal_time <= %s "
            f"ORDER BY deal_time ASC"
        )
        rows = self._db.fetch_all(sql, (market_id, account_id, strategy_id, current_time))
        return [Deal(**row) for row in rows]

    async def get_deals_by_range(self, account_id: str, strategy_id: str,
                                 market_id: int,
                                 start_time: datetime, end_time: datetime
                                 ) -> list[Deal]:
        return await asyncio.to_thread(
            self._get_deals_by_range_sync,
            account_id,
            strategy_id,
            market_id,
            start_time,
            end_time,
        )

    def _get_deals_by_range_sync(self, account_id: str, strategy_id: str,
                                 market_id: int,
                                 start_time: datetime, end_time: datetime
                                 ) -> list[Deal]:
        """按时间范围查询成交记录（数据分析层用）。"""
        table = self._table_name(account_id, strategy_id)
        sql = (
            f"SELECT deal_id, operation_id, market_id, account_id, "
            f"strategy_id, symbol_code, symbol_name, asset_type, deal_type, "
            f"direction, deal_price, deal_quantity, deal_amount, commission, "
            f"position_after, is_manual, deal_time "
            f"FROM {table} "
            f"WHERE market_id = %s AND account_id = %s "
            f"AND strategy_id = %s AND deal_time BETWEEN %s AND %s "
            f"ORDER BY deal_time ASC"
        )
        rows = self._db.fetch_all(sql, (market_id, account_id, strategy_id, start_time, end_time))
        return [Deal(**row) for row in rows]
