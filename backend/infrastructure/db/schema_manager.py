"""Create and drop database tables for account/strategy scoped data."""

from __future__ import annotations

import logging

from infrastructure.db.connection import Database
from infrastructure.db.naming import (
    SUFFIX_ASSET,
    SUFFIX_DEAL,
    SUFFIX_NOTIFICATION,
    SUFFIX_OPERATION,
    SUFFIX_REPORT,
    SUFFIX_RISK_EVENT,
    SUFFIX_TRADE,
    asset_table_name,
    table_name,
)

logger = logging.getLogger(__name__)

_CREATE_OPERATION = """\
CREATE TABLE IF NOT EXISTS {table} (
    operation_id     BIGINT          NOT NULL AUTO_INCREMENT,
    market_id        TINYINT         NOT NULL,
    account_id       VARCHAR(64)     NOT NULL,
    strategy_id      VARCHAR(64)     NOT NULL,
    symbol_code      VARCHAR(32)     NOT NULL,
    symbol_name      VARCHAR(64)     NOT NULL,
    asset_type       TINYINT         NOT NULL COMMENT '1-stock 2-fund 3-bond 4-future 5-option',
    operation_type   TINYINT         NOT NULL COMMENT '1-open 2-close',
    direction        TINYINT         NOT NULL COMMENT '1-long 2-short',
    order_type       TINYINT         NOT NULL COMMENT '1-market 2-limit',
    price            DECIMAL(20,4)   NOT NULL,
    quantity         DECIMAL(20,4)   NOT NULL,
    created_at       DATETIME        NOT NULL,
    status           TINYINT         NOT NULL DEFAULT 0 COMMENT '0-pending 1-success 2-failed 3-partial 4-cancelled',
    PRIMARY KEY (operation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

_CREATE_DEAL = """\
CREATE TABLE IF NOT EXISTS {table} (
    deal_id          BIGINT          NOT NULL AUTO_INCREMENT,
    operation_id     BIGINT          NOT NULL,
    market_id        TINYINT         NOT NULL,
    account_id       VARCHAR(64)     NOT NULL,
    strategy_id      VARCHAR(64)     NOT NULL,
    symbol_code      VARCHAR(32)     NOT NULL,
    symbol_name      VARCHAR(64)     NOT NULL,
    asset_type       TINYINT         NOT NULL COMMENT '1-stock 2-fund 3-bond 4-future 5-option',
    deal_type        TINYINT         NOT NULL COMMENT '1-open 2-close',
    direction        TINYINT         NOT NULL COMMENT '1-long 2-short',
    deal_price       DECIMAL(20,4)   NOT NULL,
    deal_quantity    DECIMAL(20,4)   NOT NULL,
    deal_amount      DECIMAL(20,4)   NOT NULL,
    commission       DECIMAL(20,4)   NOT NULL,
    position_after   DECIMAL(20,4)   NOT NULL,
    is_manual        TINYINT         NOT NULL DEFAULT 0 COMMENT '0-system 1-manual',
    deal_time        DATETIME        NOT NULL,
    PRIMARY KEY (deal_id),
    INDEX idx_operation_id (operation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

_CREATE_TRADE = """\
CREATE TABLE IF NOT EXISTS {table} (
    trade_id         BIGINT          NOT NULL AUTO_INCREMENT,
    market_id        TINYINT         NOT NULL,
    account_id       VARCHAR(64)     NOT NULL,
    strategy_id      VARCHAR(64)     NOT NULL,
    symbol_code      VARCHAR(32)     NOT NULL,
    symbol_name      VARCHAR(64)     NOT NULL,
    asset_type       TINYINT         NOT NULL COMMENT '1-stock 2-fund 3-bond 4-future 5-option',
    direction        TINYINT         NOT NULL COMMENT '1-long 2-short',
    open_time        DATETIME        NOT NULL,
    close_time       DATETIME        NOT NULL,
    open_price       DECIMAL(20,4)   NOT NULL,
    close_price      DECIMAL(20,4)   NOT NULL,
    open_quantity    DECIMAL(20,4)   NOT NULL,
    open_amount      DECIMAL(20,4)   NOT NULL,
    realized_pnl     DECIMAL(20,4)   NOT NULL,
    return_rate      DECIMAL(10,4)   NOT NULL,
    commission       DECIMAL(20,4)   NOT NULL,
    PRIMARY KEY (trade_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

_CREATE_ASSET = """\
CREATE TABLE IF NOT EXISTS {table} (
    asset_id         BIGINT          NOT NULL AUTO_INCREMENT,
    created_at       DATETIME        NOT NULL,
    market_id        TINYINT         NOT NULL,
    account_id       VARCHAR(64)     NOT NULL,
    total_asset      DECIMAL(20,4)   NOT NULL,
    net_value        DECIMAL(20,4)   NOT NULL,
    market_value     DECIMAL(20,4)   NOT NULL,
    cash_balance     DECIMAL(20,4)   NOT NULL,
    PRIMARY KEY (asset_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

_CREATE_RISK_EVENT = """\
CREATE TABLE IF NOT EXISTS {table} (
    risk_event_id   BIGINT          NOT NULL AUTO_INCREMENT,
    event_type      VARCHAR(64)     NOT NULL,
    account_id      VARCHAR(64)     NOT NULL,
    strategy_id     VARCHAR(64)     NOT NULL,
    symbol_code     VARCHAR(32)     NULL,
    event_level     TINYINT         NOT NULL,
    event_message   TEXT            NOT NULL,
    occur_time      DATETIME        NOT NULL,
    status          VARCHAR(32)     NOT NULL,
    PRIMARY KEY (risk_event_id),
    INDEX idx_event_type (event_type),
    INDEX idx_status (status),
    INDEX idx_occur_time (occur_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

_CREATE_NOTIFICATION = """\
CREATE TABLE IF NOT EXISTS {table} (
    notification_id   BIGINT        NOT NULL AUTO_INCREMENT,
    notification_type VARCHAR(64)   NOT NULL,
    risk_level        TINYINT       NOT NULL,
    title             VARCHAR(255)  NOT NULL,
    content           TEXT          NOT NULL,
    created_at        DATETIME      NOT NULL,
    is_read           TINYINT       NOT NULL DEFAULT 0,
    risk_event_id     BIGINT        NULL,
    send_status       VARCHAR(32)   NOT NULL DEFAULT 'skipped',
    PRIMARY KEY (notification_id),
    INDEX idx_notification_type (notification_type),
    INDEX idx_created_at (created_at),
    INDEX idx_risk_event_id (risk_event_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

_CREATE_REPORT = """\
CREATE TABLE IF NOT EXISTS {table} (
    report_id      INT            NOT NULL AUTO_INCREMENT,
    report_type    VARCHAR(20)    NOT NULL COMMENT 'daily / weekly / monthly',
    market_id      INT            NOT NULL COMMENT '市场标识',
    account_id     VARCHAR(64)    NOT NULL COMMENT '关联账户',
    strategy_id    VARCHAR(64)    DEFAULT NULL COMMENT '关联策略，账户级为 NULL',
    period_start   DATETIME       NOT NULL COMMENT '报表周期起',
    period_end     DATETIME       NOT NULL COMMENT '报表周期止',
    file_format    VARCHAR(10)    NOT NULL COMMENT 'pdf / xlsx / csv',
    content        MEDIUMBLOB     NOT NULL COMMENT '渲染后的文件二进制',
    file_size      INT            NOT NULL COMMENT 'content 字节数',
    status         VARCHAR(20)    NOT NULL DEFAULT 'saved' COMMENT 'saved / failed',
    generated_at   DATETIME       NOT NULL COMMENT '生成时间',
    PRIMARY KEY (report_id),
    KEY idx_lookup (market_id, account_id, strategy_id, period_start, period_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报表文件元数据与内容'
"""


class SchemaManager:
    """Manage physical MySQL tables."""

    def __init__(self, db: Database) -> None:
        self._db = db

    def create_tables(self, account_id: str, strategy_id: str) -> dict[str, bool]:
        """Create account/strategy-scoped business tables."""
        return self._batch_ddl(
            account_id,
            strategy_id,
            {
                SUFFIX_OPERATION: _CREATE_OPERATION,
                SUFFIX_DEAL: _CREATE_DEAL,
                SUFFIX_TRADE: _CREATE_TRADE,
                SUFFIX_RISK_EVENT: _CREATE_RISK_EVENT,
                SUFFIX_NOTIFICATION: _CREATE_NOTIFICATION,
            },
        )

    def create_asset_table(self, account_id: str) -> bool:
        """Create account-scoped asset table."""
        table = asset_table_name(account_id)
        return self._run_ddl(_CREATE_ASSET.format(table=table), table)

    def create_risk_event_table(self, account_id: str, strategy_id: str) -> bool:
        table = table_name(account_id, SUFFIX_RISK_EVENT, strategy_id)
        return self._run_ddl(_CREATE_RISK_EVENT.format(table=table), table)

    def create_notification_table(self, account_id: str, strategy_id: str) -> bool:
        table = table_name(account_id, SUFFIX_NOTIFICATION, strategy_id)
        return self._run_ddl(_CREATE_NOTIFICATION.format(table=table), table)

    def create_report_table(self, account_id: str) -> bool:
        """Create account-scoped report table (``{account}_report``)."""
        table = table_name(account_id, SUFFIX_REPORT)
        return self._run_ddl(_CREATE_REPORT.format(table=table), table)

    def create_all(self, account_id: str, strategy_id: str) -> dict[str, bool]:
        """Create strategy-scoped tables (operation, deal, trade, risk_event, notification).

        Account-level asset and report tables are NOT created here;
        call :meth:`create_asset_table` and :meth:`create_report_table` separately.
        """
        return self.create_tables(account_id, strategy_id)

    def drop_tables(self, account_id: str, strategy_id: str) -> dict[str, bool]:
        """Drop account/strategy-scoped business tables."""
        result: dict[str, bool] = {}
        for suffix in (
            SUFFIX_OPERATION,
            SUFFIX_DEAL,
            SUFFIX_TRADE,
            SUFFIX_RISK_EVENT,
            SUFFIX_NOTIFICATION,
        ):
            table = table_name(account_id, suffix, strategy_id)
            result[suffix] = self._run_ddl(f"DROP TABLE IF EXISTS {table}", table)
        return result

    def drop_asset_table(self, account_id: str) -> bool:
        table = asset_table_name(account_id)
        return self._run_ddl(f"DROP TABLE IF EXISTS {table}", table)

    def drop_report_table(self, account_id: str) -> bool:
        table = table_name(account_id, SUFFIX_REPORT)
        return self._run_ddl(f"DROP TABLE IF EXISTS {table}", table)

    def drop_risk_event_table(self, account_id: str, strategy_id: str) -> bool:
        table = table_name(account_id, SUFFIX_RISK_EVENT, strategy_id)
        return self._run_ddl(f"DROP TABLE IF EXISTS {table}", table)

    def drop_notification_table(self, account_id: str, strategy_id: str) -> bool:
        table = table_name(account_id, SUFFIX_NOTIFICATION, strategy_id)
        return self._run_ddl(f"DROP TABLE IF EXISTS {table}", table)

    def table_exists(
        self,
        account_id: str,
        suffix: str,
        strategy_id: str | None = None,
    ) -> bool:
        table = table_name(account_id, suffix, strategy_id, quoted=False)
        row = self._db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
            (table,),
        )
        return row is not None and row["cnt"] > 0

    def _batch_ddl(
        self,
        account_id: str,
        strategy_id: str,
        ddl_map: dict[str, str],
    ) -> dict[str, bool]:
        result: dict[str, bool] = {}
        for suffix, ddl in ddl_map.items():
            table = table_name(account_id, suffix, strategy_id)
            result[suffix] = self._run_ddl(ddl.format(table=table), table)
        return result

    def _run_ddl(self, sql: str, table_label: str) -> bool:
        try:
            self._db.execute(sql)
            logger.info("DDL ok %s", table_label)
            return True
        except Exception:
            logger.exception("DDL failed on %s", table_label)
            raise
