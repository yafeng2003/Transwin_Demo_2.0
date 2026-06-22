"""OperationRepository 测试。

- mock 模式（默认）：验证参数传递与调用逻辑。
- ``--real-db`` 模式：验证真实 SQL 执行与数据读写。
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from common.models.operation import Operation
from infrastructure.db.repositories.operation_repo import OperationRepository


@pytest.mark.anyio
class TestInsertOperations:
    """批量写入操作。"""

    async def test_insert_multiple(self, db, sample_operation: Operation) -> None:
        repo = OperationRepository(db)

        result = await repo.insert_operations("ly", "maop", [sample_operation])

        assert result == 1

    async def test_insert_empty_list(self, db) -> None:
        repo = OperationRepository(db)

        result = await repo.insert_operations("ly", "maop", [])

        assert result == 0

    @pytest.mark.mock_only
    async def test_insert_rollback_on_error(
        self, mock_db: MagicMock, sample_operation: Operation
    ) -> None:
        mock_db.cnx.cursor.return_value.__enter__.return_value.executemany.side_effect = (
            RuntimeError("insert failed")
        )
        repo = OperationRepository(mock_db)

        with pytest.raises(RuntimeError):
            await repo.insert_operations("ly", "maop", [sample_operation])

        mock_db.cnx.rollback.assert_called_once()

    @pytest.mark.mock_only
    async def test_sql_contains_correct_table(
        self, mock_db: MagicMock, sample_operation: Operation
    ) -> None:
        repo = OperationRepository(mock_db)

        await repo.insert_operations("ly", "maop", [sample_operation])

        sql = mock_db.cnx.cursor.return_value.__enter__.return_value.executemany.call_args[0][0]
        assert "ly_maop_operation" in sql or "`ly_maop_operation`" in sql
        assert "INSERT INTO" in sql


@pytest.mark.anyio
class TestGetPendingOperations:
    """查询待执行操作。"""

    async def test_returns_operations(
        self, db, sample_operation: Operation, using_real_db: bool
    ) -> None:
        repo = OperationRepository(db)

        if using_real_db:
            await repo.insert_operations("ly", "maop", [sample_operation])
        else:
            db.fetch_all.return_value = [
                {
                    "operation_id": 1,
                    "market_id": 1,
                    "account_id": "ly",
                    "strategy_id": "maop",
                    "symbol_code": "000001",
                    "symbol_name": "Ping An Bank",
                    "asset_type": 1,
                    "operation_type": 1,
                    "direction": 1,
                    "order_type": 1,
                    "price": 12.50,
                    "quantity": 1000,
                    "created_at": "2026-06-01 09:30:00",
                    "status": 0,
                }
            ]

        ops = await repo.get_pending_operations("ly", "maop", 1)

        assert len(ops) == 1
        assert isinstance(ops[0], Operation)
        assert ops[0].symbol_code == "000001"

    async def test_empty_result(self, db) -> None:
        repo = OperationRepository(db)

        ops = await repo.get_pending_operations("ly", "maop", 1)

        assert ops == []


@pytest.mark.anyio
class TestGetOperationsByRange:
    """按时间范围查询操作记录。"""

    async def test_returns_operations(
        self, db, sample_operation: Operation, using_real_db: bool
    ) -> None:
        repo = OperationRepository(db)
        start = datetime(2026, 1, 1)
        end = datetime(2026, 12, 31)

        if using_real_db:
            await repo.insert_operations("ly", "maop", [sample_operation])
        else:
            db.fetch_all.return_value = [
                {
                    "operation_id": 1,
                    "market_id": 1,
                    "account_id": "ly",
                    "strategy_id": "maop",
                    "symbol_code": "000001",
                    "symbol_name": "Ping An Bank",
                    "asset_type": 1,
                    "operation_type": 1,
                    "direction": 1,
                    "order_type": 1,
                    "price": 12.50,
                    "quantity": 1000,
                    "created_at": "2026-06-01 09:30:00",
                    "status": 0,
                }
            ]

        ops = await repo.get_operations_by_range("ly", "maop", 1, start, end)

        assert len(ops) == 1
        assert isinstance(ops[0], Operation)
        assert ops[0].symbol_code == "000001"

    async def test_empty_result(self, db) -> None:
        repo = OperationRepository(db)

        ops = await repo.get_operations_by_range(
            "ly", "maop", 1, datetime(2020, 1, 1), datetime(2020, 1, 2)
        )

        assert ops == []

    @pytest.mark.mock_only
    async def test_sql_filters_by_created_at(self, mock_db: MagicMock) -> None:
        repo = OperationRepository(mock_db)

        await repo.get_operations_by_range(
            "ly", "maop", 1, datetime(2026, 1, 1), datetime(2026, 12, 31)
        )

        sql = mock_db.fetch_all.call_args[0][0]
        params = mock_db.fetch_all.call_args[0][1]
        assert "ly_maop_operation" in sql or "`ly_maop_operation`" in sql
        assert "created_at BETWEEN" in sql
        assert params == (
            1,
            "ly",
            "maop",
            datetime(2026, 1, 1),
            datetime(2026, 12, 31),
        )


@pytest.mark.anyio
class TestUpdateStatus:
    """更新操作状态。"""

    async def test_successful_update(
        self, db, sample_operation: Operation, using_real_db: bool
    ) -> None:
        repo = OperationRepository(db)

        if using_real_db:
            await repo.insert_operations("ly", "maop", [sample_operation])
            pending = await repo.get_pending_operations("ly", "maop", 1)
            assert len(pending) > 0
            op_id = pending[0].operation_id

            result = await repo.update_status(op_id, "ly", "maop", 1)

            assert result is True
            updated_ops = await repo.get_pending_operations("ly", "maop", 1)
            assert op_id not in [op.operation_id for op in updated_ops]
        else:
            # mock 模式下默认 execute 返回 1，update_status 应返回 True。
            result = await repo.update_status(42, "ly", "maop", 1)
            assert result is True

    async def test_not_found(self, db, using_real_db: bool) -> None:
        repo = OperationRepository(db)
        if not using_real_db:
            # 模拟无影响行。
            db.execute.return_value = 0

        result = await repo.update_status(99999, "ly", "maop", 1)

        assert result is False
