"""
trade 表（完整交易记录）的读写操作。

接口文档对应：
  - #4 insert_trade_record  执行层 → 数据库
  - #12 get_trades          数据库 → 数据分析层
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from common.models.trade import Trade
from common.interfaces.trade_repository import (
    TradeRepository as TradeRepositoryInterface,
)
from infrastructure.db.repositories.base_repo import BaseRepository


class TradeRepository(BaseRepository, TradeRepositoryInterface):
    """完整交易记录表的 Repository，按 {account}_{strategy}_trade 分表。"""

    TABLE_SUFFIX = "trade"

    # ── 写入 ────────────────────────────────────────────────────

    async def insert_trade(self, account_id: str, strategy_id: str,
                           trade: Trade) -> int:
        return await asyncio.to_thread(
            self._insert_trade_sync, account_id, strategy_id, trade
        )

    def _insert_trade_sync(self, account_id: str, strategy_id: str,
                           trade: Trade) -> int:
        """写入一笔完整交易记录（开仓+平仓后调用），返回自增 trade_id。"""
        table = self._table_name(account_id, strategy_id)
        sql = (
            f"INSERT INTO {table} "
            f"(market_id, account_id, strategy_id, symbol_code, symbol_name, "
            f"asset_type, direction, open_time, close_time, "
            f"open_price, close_price, open_quantity, open_amount, "
            f"realized_pnl, return_rate, commission) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, "
            f"%s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            trade.market_id, trade.account_id, trade.strategy_id,
            trade.symbol_code, trade.symbol_name,
            trade.asset_type, trade.direction,
            trade.open_time, trade.close_time,
            trade.open_price, trade.close_price,
            trade.open_quantity, trade.open_amount,
            trade.realized_pnl, trade.return_rate,
            trade.commission,
        )

        try:
            with self._db.cnx.cursor() as cursor:
                cursor.execute(sql, params)
                trade_id = cursor.lastrowid
            self._db.commit()
        except Exception:
            self._db.cnx.rollback()
            raise
        return trade_id

    # ── 查询 ────────────────────────────────────────────────────

    async def get_trades_by_range(self, account_id: str, strategy_id: str,
                                  market_id: int,
                                  start_time: datetime, end_time: datetime
                                  ) -> list[Trade]:
        return await asyncio.to_thread(
            self._get_trades_by_range_sync,
            account_id,
            strategy_id,
            market_id,
            start_time,
            end_time,
        )

    def _get_trades_by_range_sync(self, account_id: str, strategy_id: str,
                                  market_id: int,
                                  start_time: datetime, end_time: datetime
                                  ) -> list[Trade]:
        """按条件查询完整交易记录。"""
        table = self._table_name(account_id, strategy_id)
        sql = (
            f"SELECT trade_id, market_id, account_id, strategy_id, "
            f"symbol_code, symbol_name, asset_type, direction, "
            f"open_time, close_time, open_price, close_price, "
            f"open_quantity, open_amount, realized_pnl, return_rate, commission "
            f"FROM {table} "
            f"WHERE market_id = %s AND account_id = %s "
            f"AND strategy_id = %s AND open_time BETWEEN %s AND %s "
            f"ORDER BY open_time ASC"
        )
        rows = self._db.fetch_all(sql, (
            market_id, account_id, strategy_id, start_time, end_time,
        ))
        return [Trade(**row) for row in rows]
