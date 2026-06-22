from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from common.interfaces.analysis_interface import ReportFileStore
from common.interfaces.asset_repository import AssetRepository
from common.interfaces.deal_repository import DealRepository
from common.interfaces.operation_repository import OperationRepository
from common.interfaces.trade_repository import TradeRepository
from data_analysis.tests.conftest import make_assets, make_deal, make_operation, make_trade
from data_analysis.app import build_app

_WINDOW = {"start_time": "2024-01-01T00:00:00", "end_time": "2024-12-31T00:00:00"}
_ACCOUNT = {"market_id": 1, "account_id": "acc_001"}


@pytest.fixture
def repos():
    asset_repo = AsyncMock(spec=AssetRepository)
    trade_repo = AsyncMock(spec=TradeRepository)
    deal_repo = AsyncMock(spec=DealRepository)
    operation_repo = AsyncMock(spec=OperationRepository)
    asset_repo.get_assets_by_range.return_value = make_assets(["100", "110", "121"])
    trade_repo.get_trades_by_range.return_value = [make_trade("100", trade_id=1), make_trade("-50", trade_id=2)]
    deal_repo.get_deals_by_range.return_value = [
        make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10.1", position_after="100", operation_id=1),
    ]
    operation_repo.get_operations_by_range.return_value = [make_operation(1, "10.0")]
    return asset_repo, trade_repo, deal_repo, operation_repo


@pytest.fixture
def client(repos):
    store = AsyncMock(spec=ReportFileStore)
    return TestClient(build_app(*repos, report_store=store))


class TestAnalysisAPI:

    def test_health(self, client):
        assert client.get("/health").json() == {"status": "ok"}

    def test_returns(self, client):
        resp = client.get("/api/v1/analysis/returns", params={**_ACCOUNT, **_WINDOW})
        assert resp.status_code == 200
        assert resp.json()["cumulative_return"] == pytest.approx(0.21)

    def test_period_returns(self, client):
        resp = client.get("/api/v1/analysis/returns/periods",
                          params={**_ACCOUNT, **_WINDOW, "granularity": "daily"})
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 2

    def test_equity_curve(self, client):
        resp = client.get("/api/v1/analysis/equity-curve", params={**_ACCOUNT, **_WINDOW})
        assert len(resp.json()["points"]) == 3

    def test_risk(self, client):
        resp = client.get("/api/v1/analysis/risk", params={**_ACCOUNT, **_WINDOW})
        assert resp.status_code == 200
        assert "max_drawdown" in resp.json()

    def test_drawdown_series(self, client):
        resp = client.get("/api/v1/analysis/risk/drawdown", params={**_ACCOUNT, **_WINDOW})
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_return_distribution(self, client):
        resp = client.get("/api/v1/analysis/risk/distribution",
                          params={**_ACCOUNT, **_WINDOW, "bins": 5})
        assert resp.status_code == 200
        assert "bins" in resp.json()

    def test_trades(self, client):
        resp = client.get("/api/v1/analysis/trades", params={**_ACCOUNT, "strategy_id": "s1", **_WINDOW})
        assert resp.json()["total_trades"] == 2

    def test_trade_frequency(self, client):
        resp = client.get("/api/v1/analysis/trades/frequency",
                          params={**_ACCOUNT, "strategy_id": "s1", **_WINDOW})
        assert resp.status_code == 200
        assert resp.json()["total_trades"] == 2

    def test_slippage(self, client):
        resp = client.get("/api/v1/analysis/trades/slippage",
                          params={**_ACCOUNT, "strategy_id": "s1", **_WINDOW})
        assert resp.status_code == 200
        assert resp.json()["matched_count"] == 1

    def test_positions(self, client):
        resp = client.get("/api/v1/analysis/positions",
                          params={**_ACCOUNT, "strategy_id": "s1", "query_time": "2024-06-01T00:00:00"})
        assert resp.status_code == 200
        assert resp.json()["active_positions"][0]["holding_quantity"] == "100"

    def test_position_distribution(self, client):
        resp = client.get("/api/v1/analysis/positions/distribution",
                          params={**_ACCOUNT, "strategy_id": "s1", "query_time": "2024-06-01T00:00:00"})
        assert resp.status_code == 200
        assert resp.json()["weights"][0]["weight"] == pytest.approx(1.0)

    def test_exposure(self, client):
        resp = client.get("/api/v1/analysis/positions/exposure",
                          params={**_ACCOUNT, "strategy_id": "s1", "query_time": "2024-06-01T00:00:00"})
        assert resp.status_code == 200
        assert resp.json()["position_count"] == 1

    def test_strategy_comparison(self, client):
        resp = client.get("/api/v1/analysis/strategy-comparison",
                          params={**_ACCOUNT, "strategy_ids": ["A", "B"], **_WINDOW})
        assert resp.status_code == 200
        assert len(resp.json()["contributions"]) == 2
