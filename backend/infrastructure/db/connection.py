from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Optional

try:
    import pymysql
    from pymysql.cursors import DictCursor
except ModuleNotFoundError:
    pymysql = None
    DictCursor = None

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    host: str = "192.16.1.112"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "strategy_system"
    charset: str = "utf8mb4"
    max_retries: int = 3         
    retry_interval: float = 3.0 


class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection: Optional[Any] = None
        self._lock = threading.Lock()

    # ── 连接生命周期 ──────────────────────────────────────────────

    def connect(self) -> Any:
        global pymysql, DictCursor
        if pymysql is None or DictCursor is None:
            try:
                pymysql = import_module("pymysql")
                DictCursor = import_module("pymysql.cursors").DictCursor
            except ModuleNotFoundError as exc:
                raise ModuleNotFoundError("pymysql is required for real database connections") from exc

        last_error: Optional[Exception] = None

        for attempt in range(1, self.config.max_retries + 1):
            try:
                self._connection = pymysql.connect(
                    host=self.config.host,
                    port=self.config.port,
                    user=self.config.user,
                    password=self.config.password,
                    database=self.config.database,
                    charset=self.config.charset,
                    cursorclass=DictCursor,
                )
                logger.info(
                    "Connected to mysql://%s@%s:%d/%s",
                    self.config.user,
                    self.config.host,
                    self.config.port,
                    self.config.database,
                )
                return self._connection
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "DB connection attempt %d/%d failed: %s",
                    attempt,
                    self.config.max_retries,
                    exc,
                )
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_interval)

        raise ConnectionError(
            f"Could not connect to {self.config.host}:{self.config.port}/"
            f"{self.config.database} after {self.config.max_retries} attempts"
        ) from last_error

    def close(self) -> None:
        if self._connection is not None and self._connection.open:
            self._connection.close()
            logger.debug("Database connection closed")

    @property
    def cnx(self) -> Any:
        if self._connection is None or not self._connection.open:
            self.connect()
        else:
            try:
                self._connection.ping(reconnect=True)
            except Exception:
                self.connect()
        return self._connection

    def fetch_all(self, sql: str, params: tuple = ()) -> list[dict]:
        with self._lock:
            with self.cnx.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()

    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[dict]:
        with self._lock:
            with self.cnx.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()

    def execute(self, sql: str, params: tuple = ()) -> int:
        with self._lock:
            with self.cnx.cursor() as cursor:
                affected = cursor.execute(sql, params)
            return affected

    def commit(self) -> None:
        with self._lock:
            self.cnx.commit()

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, *exc_args) -> None:
        self.close()
