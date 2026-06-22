"""schema_manager.py 测试。

- mock 模式（默认）：验证 SQL 生成与调用
- ``--real-db`` 模式：连接真实数据库验证 DDL 执行效果
"""

from __future__ import annotations

from unittest.mock import MagicMock, call

import pytest

from infrastructure.db.schema_manager import SchemaManager


class TestCreateTables:
    """创建表相关。"""

    def test_create_tables_returns_dict(self, db) -> None:
        """双模式：返回 dict 键值正确。"""
        sm = SchemaManager(db)
        result = sm.create_tables("ly", "maop")

        assert isinstance(result, dict)
        assert set(result.keys()) == {
            "operation",
            "deal",
            "trade",
            "risk_event",
            "notification",
        }

    @pytest.mark.mock_only
    def test_create_tables_executes_ddl_for_all_strategy_tables(
        self, mock_db: MagicMock
    ) -> None:
        sm = SchemaManager(mock_db)
        sm.create_tables("ly", "maop")

        assert mock_db.execute.call_count == 5
        calls = [c[0][0] for c in mock_db.execute.call_args_list]
        assert any("ly_maop_operation" in c for c in calls)
        assert any("ly_maop_deal" in c for c in calls)
        assert any("ly_maop_trade" in c for c in calls)
        assert any("ly_maop_risk_event" in c for c in calls)
        assert any("ly_maop_notification" in c for c in calls)

    @pytest.mark.mock_only
    def test_create_asset_table(self, mock_db: MagicMock) -> None:
        sm = SchemaManager(mock_db)
        sm.create_asset_table("ly")

        sql = mock_db.execute.call_args[0][0]
        assert "ly_asset" in sql
        assert "CREATE TABLE" in sql

    @pytest.mark.mock_only
    def test_create_all_includes_asset(self, mock_db: MagicMock) -> None:
        sm = SchemaManager(mock_db)
        result = sm.create_all("test", "s1")

        assert isinstance(result, dict)
        assert set(result.keys()) == {
            "operation",
            "deal",
            "trade",
            "risk_event",
            "notification",
            "asset",
        }
        assert mock_db.execute.call_count == 6

    @pytest.mark.mock_only
    def test_ddl_uses_if_not_exists(self, mock_db: MagicMock) -> None:
        sm = SchemaManager(mock_db)
        sm.create_tables("ly", "maop")

        for c in mock_db.execute.call_args_list:
            sql = c[0][0]
            assert "CREATE TABLE IF NOT EXISTS" in sql


class TestDropTables:
    """删除表相关。"""

    @pytest.mark.mock_only
    def test_drop_tables_executes_drop_for_all_strategy_tables(
        self, mock_db: MagicMock
    ) -> None:
        sm = SchemaManager(mock_db)
        result = sm.drop_tables("ly", "maop")

        assert mock_db.execute.call_count == 5
        assert set(result.keys()) == {
            "operation",
            "deal",
            "trade",
            "risk_event",
            "notification",
        }
        for c in mock_db.execute.call_args_list:
            assert "DROP TABLE IF EXISTS" in c[0][0]

    @pytest.mark.mock_only
    def test_drop_asset_table(self, mock_db: MagicMock) -> None:
        sm = SchemaManager(mock_db)
        result = sm.drop_asset_table("ly")

        assert result is True
        assert "DROP TABLE IF EXISTS" in mock_db.execute.call_args[0][0]
        assert "ly_asset" in mock_db.execute.call_args[0][0]


class TestTableExists:
    """表存在检查。"""

    def test_exists_true(self, db, using_real_db: bool) -> None:
        sm = SchemaManager(db)
        if using_real_db:
            # real-db 模式下表已由 setup 创建
            assert sm.table_exists("ly", "operation", "maop") is True
        else:
            db.fetch_one.return_value = {"cnt": 1}
            assert sm.table_exists("ly", "operation", "maop") is True

    def test_exists_false(self, db, using_real_db: bool) -> None:
        sm = SchemaManager(db)
        if using_real_db:
            # 查一个不存在的表
            assert sm.table_exists("nonexistent", "foo", "bar") is False
        else:
            db.fetch_one.return_value = {"cnt": 0}
            assert sm.table_exists("ly", "operation", "maop") is False

    def test_exists_asset_table(self, db, using_real_db: bool) -> None:
        """asset 表不含 strategy_id。"""
        sm = SchemaManager(db)
        if using_real_db:
            assert sm.table_exists("ly", "asset") is True
        else:
            db.fetch_one.return_value = {"cnt": 1}
            assert sm.table_exists("ly", "asset") is True

    @pytest.mark.mock_only
    def test_mock_sql_check(self, mock_db: MagicMock) -> None:
        """验证 mock 模式下查询了 information_schema（mock-only）。"""
        mock_db.fetch_one.return_value = {"cnt": 1}
        sm = SchemaManager(mock_db)
        sm.table_exists("ly", "operation", "maop")

        sql = mock_db.fetch_one.call_args[0][0]
        assert "information_schema.TABLES" in sql


@pytest.mark.mock_only
class TestDdlFailure:
    """DDL 执行失败时异常传播（mock-only）。"""

    def test_raises_on_create_failure(self, mock_db: MagicMock) -> None:
        mock_db.execute.side_effect = RuntimeError("connection lost")
        sm = SchemaManager(mock_db)

        with pytest.raises(RuntimeError, match="connection lost"):
            sm.create_tables("ly", "maop")

    def test_raises_on_drop_failure(self, mock_db: MagicMock) -> None:
        mock_db.execute.side_effect = RuntimeError("connection lost")
        sm = SchemaManager(mock_db)

        with pytest.raises(RuntimeError):
            sm.drop_tables("ly", "maop")
