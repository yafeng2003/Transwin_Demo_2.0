"""
operation 表（原始操作）的读写操作。

接口文档对应：
  - #1 insert_operation  策略层写入操作 → 数据库
  - #3 get_operations    数据库 → 执行层（取待执行操作）
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from common.models.operation import Operation
from common.interfaces.operation_repository import (
    OperationRepository as OperationRepositoryInterface,
)
from infrastructure.db.repositories.base_repo import BaseRepository


class OperationRepository(BaseRepository, OperationRepositoryInterface):
    """原始操作表的 Repository，按 {account}_{strategy}_operation 分表。"""

    TABLE_SUFFIX = "operation"

    # ── 写入 ────────────────────────────────────────────────────

    async def insert_operations(self, account_id: str, strategy_id: str,
                                operations: list[Operation]) -> int:
        return await asyncio.to_thread(
            self._insert_operations_sync, account_id, strategy_id, operations
        )

    def _insert_operations_sync(self, account_id: str, strategy_id: str,
                                operations: list[Operation]) -> int:
        """批量写入策略生成的操作，自动提交。

        返回写入条数。任一写入失败则整个事务回滚。
        """
        if not operations:
            return 0

        table = self._table_name(account_id, strategy_id)
        sql = (
            f"INSERT INTO {table} "
            f"(market_id, account_id, strategy_id, symbol_code, symbol_name, "
            f"asset_type, operation_type, direction, order_type, "
            f"price, quantity, created_at, status) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = [
            (
                op.market_id, op.account_id, op.strategy_id,
                op.symbol_code, op.symbol_name,
                op.asset_type, op.operation_type, op.direction,
                op.order_type, op.price, op.quantity,
                op.created_at, op.status,
            )
            for op in operations
        ]

        try:
            with self._db.cnx.cursor() as cursor:
                cursor.executemany(sql, params)
            self._db.commit()
        except Exception:
            self._db.cnx.rollback()
            raise
        return len(operations)

    # ── 查询 ────────────────────────────────────────────────────

    async def get_pending_operations(self, account_id: str, strategy_id: str,
                                     market_id: int) -> list[Operation]:
        return await asyncio.to_thread(
            self._get_pending_operations_sync, account_id, strategy_id, market_id
        )

    def _get_pending_operations_sync(self, account_id: str, strategy_id: str,
                                     market_id: int) -> list[Operation]:
        """获取指定策略下未执行的操作（status=0），按生成时间升序。"""
        table = self._table_name(account_id, strategy_id)
        sql = (
            f"SELECT operation_id, market_id, account_id, strategy_id, "
            f"symbol_code, symbol_name, asset_type, operation_type, direction, "
            f"order_type, price, quantity, created_at, status "
            f"FROM {table} "
            f"WHERE market_id = %s AND account_id = %s "
            f"AND strategy_id = %s AND status = 0 "
            f"ORDER BY created_at ASC"
        )
        rows = self._db.fetch_all(sql, (market_id, account_id, strategy_id))
        return [Operation(**row) for row in rows]

    async def get_operations_by_range(self, account_id: str, strategy_id: str,
                                      market_id: int,
                                      start_time: datetime, end_time: datetime
                                      ) -> list[Operation]:
        return await asyncio.to_thread(
            self._get_operations_by_range_sync,
            account_id,
            strategy_id,
            market_id,
            start_time,
            end_time,
        )

    def _get_operations_by_range_sync(self, account_id: str, strategy_id: str,
                                      market_id: int,
                                      start_time: datetime, end_time: datetime
                                      ) -> list[Operation]:
        """按生成时间范围查询操作记录，供滑点等分析使用。"""
        table = self._table_name(account_id, strategy_id)
        sql = (
            f"SELECT operation_id, market_id, account_id, strategy_id, "
            f"symbol_code, symbol_name, asset_type, operation_type, direction, "
            f"order_type, price, quantity, created_at, status "
            f"FROM {table} "
            f"WHERE market_id = %s AND account_id = %s "
            f"AND strategy_id = %s AND created_at BETWEEN %s AND %s "
            f"ORDER BY created_at ASC"
        )
        rows = self._db.fetch_all(sql, (market_id, account_id, strategy_id, start_time, end_time))
        return [Operation(**row) for row in rows]

    # ── 状态更新 ────────────────────────────────────────────────

    async def update_status(self, operation_id: int, account_id: str,
                            strategy_id: str, new_status: int) -> bool:
        return await asyncio.to_thread(
            self._update_status_sync,
            operation_id,
            account_id,
            strategy_id,
            new_status,
        )

    def _update_status_sync(self, operation_id: int, account_id: str,
                            strategy_id: str, new_status: int) -> bool:
        """更新单条操作的状态，返回是否找到并更新了记录。"""
        table = self._table_name(account_id, strategy_id)
        sql = f"UPDATE {table} SET status = %s WHERE operation_id = %s AND account_id = %s AND strategy_id = %s"
        affected = self._db.execute(sql, (new_status, operation_id, account_id, strategy_id))
        self._db.commit()
        return affected > 0
