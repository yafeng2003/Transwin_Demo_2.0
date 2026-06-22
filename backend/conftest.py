"""pytest shared fixtures.

Supports a default mock mode and an optional ``--real-db`` mode for tests that
can verify real MySQL behavior.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from common.models.asset import Asset
from common.models.deal import Deal
from common.models.operation import Operation
from common.models.risk import RiskEvent, RiskNotification
from common.models.trade import Trade
from infrastructure.db.connection import Database, DatabaseConfig


@pytest.fixture
def anyio_backend():
    return "asyncio"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "mock_only: skip when running with --real-db")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--real-db",
        action="store_true",
        default=False,
        help="run tests against a real MySQL database instead of mocks",
    )
    parser.addoption("--db-host", default="192.16.1.112", help="database host")
    parser.addoption("--db-port", default=3306, type=int, help="database port")
    parser.addoption("--db-user", default="root", help="database user")
    parser.addoption("--db-password", default="", help="database password")
    parser.addoption("--db-name", default="test_backend", help="existing test database name")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.getoption("--real-db"):
        skip = pytest.mark.skip(reason="mock-only test skipped in --real-db mode")
        for item in items:
            if item.get_closest_marker("mock_only") is not None:
                item.add_marker(skip)


@pytest.fixture
def using_real_db(request: pytest.FixtureRequest) -> bool:
    return bool(request.config.getoption("--real-db"))


def _db_config(request: pytest.FixtureRequest) -> DatabaseConfig:
    return DatabaseConfig(
        host=request.config.getoption("--db-host"),
        port=request.config.getoption("--db-port"),
        user=request.config.getoption("--db-user"),
        password=request.config.getoption("--db-password"),
        database=request.config.getoption("--db-name"),
    )


@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock()
    db.fetch_all.return_value = []
    db.fetch_one.return_value = None
    db.execute.return_value = 1

    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    db.cnx.cursor.return_value.__enter__.return_value = mock_cursor

    return db


@pytest.fixture
def real_db(request: pytest.FixtureRequest) -> Database:
    if not request.config.getoption("--real-db"):
        pytest.skip("requires --real-db")
    db = Database(_db_config(request))
    db.connect()
    return db


@pytest.fixture
def db(request: pytest.FixtureRequest, mock_db: MagicMock) -> Database | MagicMock:
    if request.config.getoption("--real-db"):
        real = Database(_db_config(request))
        real.connect()
        return real
    return mock_db


@pytest.fixture(scope="session", autouse=True)
def real_db_setup(request: pytest.FixtureRequest) -> None:
    if request.config.getoption("--real-db"):
        db = Database(_db_config(request))
        db.connect()

        from infrastructure.db.schema_manager import SchemaManager

        sm = SchemaManager(db)
        sm.create_all("ly", "maop")
        sm.create_all("ly", "manual")
        sm.create_all("test", "s1")
        sm.create_asset_table("ly")
        sm.create_asset_table("test_account")

        yield

        sm.drop_tables("ly", "maop")
        sm.drop_tables("ly", "manual")
        sm.drop_tables("test", "s1")
        sm.drop_asset_table("ly")
        sm.drop_asset_table("test_account")
        db.close()
    else:
        yield


_CLEAN_TABLES = [
    "`ly_maop_operation`",
    "`ly_maop_deal`",
    "`ly_maop_trade`",
    "`ly_maop_risk_event`",
    "`ly_maop_notification`",
    "`ly_manual_operation`",
    "`ly_manual_deal`",
    "`ly_manual_trade`",
    "`ly_manual_risk_event`",
    "`ly_manual_notification`",
    "`ly_asset`",
    "`test_s1_operation`",
    "`test_s1_deal`",
    "`test_s1_trade`",
    "`test_s1_risk_event`",
    "`test_s1_notification`",
    "`test_account_asset`",
]


@pytest.fixture(scope="session")
def _clean_conn(request: pytest.FixtureRequest) -> Database | None:
    if not request.config.getoption("--real-db"):
        yield None
        return

    conn = Database(_db_config(request))
    conn.connect()
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def _clean_before_each(
    _clean_conn: Database | None, using_real_db: bool
) -> None:
    if not using_real_db or _clean_conn is None:
        return
    for table in _CLEAN_TABLES:
        _clean_conn.execute(f"DELETE FROM {table}")
    _clean_conn.commit()


@pytest.fixture
def sample_operation() -> Operation:
    return Operation(
        operation_id=0,
        market_id=1,
        account_id="ly",
        strategy_id="maop",
        symbol_code="000001",
        symbol_name="Ping An Bank",
        asset_type=1,
        operation_type=1,
        direction=1,
        order_type=1,
        price=Decimal("12.50"),
        quantity=Decimal("1000"),
        created_at=datetime(2026, 6, 1, 9, 30, 0),
        status=0,
    )


@pytest.fixture
def sample_deal() -> Deal:
    return Deal(
        deal_id=0,
        operation_id=1,
        market_id=1,
        account_id="ly",
        strategy_id="maop",
        symbol_code="000001",
        symbol_name="Ping An Bank",
        asset_type=1,
        deal_type=1,
        direction=1,
        deal_price=Decimal("12.50"),
        deal_quantity=Decimal("1000"),
        deal_amount=Decimal("12500.00"),
        commission=Decimal("2.50"),
        position_after=Decimal("1000"),
        is_manual=0,
        deal_time=datetime(2026, 6, 1, 9, 30, 5),
    )


@pytest.fixture
def sample_asset() -> Asset:
    return Asset(
        asset_id=0,
        created_at=datetime(2026, 6, 1, 15, 0, 0),
        market_id=1,
        account_id="ly",
        total_asset=Decimal("150000.00"),
        net_value=Decimal("1.05"),
        market_value=Decimal("120000.00"),
        cash_balance=Decimal("30000.00"),
    )


@pytest.fixture
def sample_trade() -> Trade:
    return Trade(
        trade_id=0,
        market_id=1,
        account_id="ly",
        strategy_id="maop",
        symbol_code="000001",
        symbol_name="Ping An Bank",
        asset_type=1,
        direction=1,
        open_time=datetime(2026, 6, 1, 9, 30, 0),
        close_time=datetime(2026, 6, 10, 14, 0, 0),
        open_price=Decimal("12.50"),
        close_price=Decimal("13.20"),
        open_quantity=Decimal("1000"),
        open_amount=Decimal("12500.00"),
        realized_pnl=Decimal("700.00"),
        return_rate=Decimal("0.056"),
        commission=Decimal("5.00"),
    )


@pytest.fixture
def sample_risk_event() -> RiskEvent:
    return RiskEvent(
        event_type="api_error",
        account_id="ly",
        strategy_id="maop",
        symbol_code="000001",
        event_level=4,
        event_message="API connection error",
        occur_time=datetime(2026, 6, 1, 10, 0, 0),
        status="pending",
    )


@pytest.fixture
def sample_risk_notification() -> RiskNotification:
    return RiskNotification(
        notification_type="risk_alert",
        account_id="ly",
        strategy_id="maop",
        risk_level=4,
        title="Risk alert",
        content="API connection error",
        created_at=datetime(2026, 6, 1, 10, 1, 0),
        risk_event_id=1,
    )
