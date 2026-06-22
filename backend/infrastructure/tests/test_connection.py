"""connection.py 单元测试。

核心依赖 ``pymysql.connect`` 及游标行为全部 mock。
``--real-db`` 模式下自动跳过（Database 内部逻辑无法通过集成测试覆盖）。
"""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

try:
    import pymysql
except ModuleNotFoundError:
    class FakePyMySQLError(Exception):
        pass

    pymysql = ModuleType("pymysql")
    pymysql.Error = FakePyMySQLError
    pymysql.connect = MagicMock()

    cursors = ModuleType("pymysql.cursors")
    cursors.DictCursor = object
    pymysql.cursors = cursors

    sys.modules["pymysql"] = pymysql
    sys.modules["pymysql.cursors"] = cursors

from infrastructure.db import connection as connection_module
from infrastructure.db.connection import Database, DatabaseConfig


class TestDatabaseConfig:
    """DatabaseConfig 默认值与初始化（纯数据类，无需 mock）。"""

    def test_default_host(self) -> None:
        cfg = DatabaseConfig()
        assert cfg.host == "192.16.1.112"

    def test_default_port(self) -> None:
        cfg = DatabaseConfig()
        assert cfg.port == 3306

    def test_default_retry(self) -> None:
        cfg = DatabaseConfig()
        assert cfg.max_retries == 3
        assert cfg.retry_interval == 3.0

    def test_custom_values(self) -> None:
        cfg = DatabaseConfig(host="localhost", port=4000)
        assert cfg.host == "localhost"
        assert cfg.port == 4000


@pytest.mark.mock_only
class TestDatabaseConnect:
    """Database.connect() — 连接生命周期。"""

    @patch("pymysql.connect")
    def test_success(self, mock_connect: MagicMock) -> None:
        db = Database(DatabaseConfig(host="h", port=1, user="u", password="p", database="d"))
        conn = db.connect()

        mock_connect.assert_called_once_with(
            host="h", port=1, user="u", password="p", database="d",
            charset="utf8mb4", cursorclass=connection_module.DictCursor,
        )
        assert conn is mock_connect.return_value
        assert db._connection is mock_connect.return_value

    @patch("pymysql.connect")
    def test_retry_then_success(self, mock_connect: MagicMock) -> None:
        """前两次失败，第三次成功。"""
        mock_conn_ok = MagicMock()
        mock_connect.side_effect = [
            pymysql.Error("conn refused"),
            pymysql.Error("timeout"),
            mock_conn_ok,
        ]
        db = Database(DatabaseConfig(host="h", port=1, user="u", password="p", database="d"))

        conn = db.connect()

        assert mock_connect.call_count == 3
        assert conn is mock_conn_ok

    @patch("pymysql.connect")
    def test_all_retries_fail(self, mock_connect: MagicMock) -> None:
        mock_connect.side_effect = pymysql.Error("always fail")
        db = Database(DatabaseConfig(host="h", port=1, user="u", password="p", database="d", max_retries=2))

        with pytest.raises(ConnectionError, match="Could not connect"):
            db.connect()

        assert mock_connect.call_count == 2

    @patch("pymysql.connect")
    def test_close(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_conn.open = True
        mock_connect.return_value = mock_conn

        db = Database(DatabaseConfig())
        db._connection = mock_conn
        db.close()

        mock_conn.close.assert_called_once()

    @patch("pymysql.connect")
    def test_close_when_none(self, mock_connect: MagicMock) -> None:
        """从未连接时 close 不应抛异常。"""
        db = Database(DatabaseConfig())
        db.close()  # should not raise


@pytest.mark.mock_only
class TestDatabaseCnxProperty:
    """Database.cnx 惰性连接属性。"""

    @patch("pymysql.connect")
    def test_auto_connect_when_none(self, mock_connect: MagicMock) -> None:
        db = Database(DatabaseConfig())
        assert db._connection is None

        cnx = db.cnx

        mock_connect.assert_called_once()
        assert cnx is mock_connect.return_value

    @patch("pymysql.connect")
    def test_auto_reconnect_when_closed(self, mock_connect: MagicMock) -> None:
        mock_old = MagicMock()
        mock_old.open = False
        mock_connect.return_value = MagicMock()

        db = Database(DatabaseConfig())
        db._connection = mock_old

        cnx = db.cnx

        # 应触发重新连接
        assert mock_connect.call_count == 1
        assert cnx is mock_connect.return_value

    @patch("pymysql.connect")
    def test_return_existing(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_conn.open = True
        db = Database(DatabaseConfig())
        db._connection = mock_conn

        cnx = db.cnx

        mock_connect.assert_not_called()
        assert cnx is mock_conn


@pytest.mark.mock_only
class TestDatabaseQueryMethods:
    """fetch_all / fetch_one / execute。"""

    @patch("pymysql.connect")
    def test_fetch_all(self, mock_connect: MagicMock) -> None:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1}, {"id": 2}]
        mock_connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        db = Database(DatabaseConfig())
        result = db.fetch_all("SELECT * FROM t", (1,))

        assert result == [{"id": 1}, {"id": 2}]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM t", (1,))

    @patch("pymysql.connect")
    def test_fetch_one(self, mock_connect: MagicMock) -> None:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 1}
        mock_connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        db = Database(DatabaseConfig())
        result = db.fetch_one("SELECT * FROM t WHERE id=%s", (1,))

        assert result == {"id": 1}

    @patch("pymysql.connect")
    def test_fetch_one_none(self, mock_connect: MagicMock) -> None:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        db = Database(DatabaseConfig())
        result = db.fetch_one("SELECT * FROM t WHERE id=%s", (999,))

        assert result is None

    @patch("pymysql.connect")
    def test_execute(self, mock_connect: MagicMock) -> None:
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = 2
        mock_connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        db = Database(DatabaseConfig())
        affected = db.execute("UPDATE t SET x=1 WHERE id=%s", (1,))

        assert affected == 2

    @patch("pymysql.connect")
    def test_commit(self, mock_connect: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        db = Database(DatabaseConfig())
        db._connection = mock_conn
        db.commit()

        mock_conn.commit.assert_called_once()


@pytest.mark.mock_only
class TestDatabaseContextManager:
    """Database 作为上下文管理器。"""

    @patch("pymysql.connect")
    def test_enter_exit(self, mock_connect: MagicMock) -> None:
        db = Database(DatabaseConfig())

        with db as d:
            assert d is db
            mock_connect.assert_called_once()

        # 退出时 close 被调用
        db._connection.close.assert_called_once()
