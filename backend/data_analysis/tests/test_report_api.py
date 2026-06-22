from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from common.interfaces.analysis_interface import ReportFileStore
from common.interfaces.asset_repository import AssetRepository
from common.interfaces.deal_repository import DealRepository
from common.interfaces.operation_repository import OperationRepository
from common.interfaces.trade_repository import TradeRepository
from common.models.analytics import ReportFileResult, ReportMetadata
from data_analysis.tests.conftest import make_assets, make_deal, make_trade
from data_analysis.app import build_app


def _metadata(report_id: int = 1, file_format: str = "pdf") -> ReportMetadata:
    return ReportMetadata(
        report_id=report_id, report_type="daily", market_id=1, account_id="acc_001",
        strategy_id="s1", period_start=datetime(2024, 1, 1), period_end=datetime(2024, 1, 1, 23, 59),
        file_format=file_format, file_uri=f"s3://reports/{report_id}.{file_format}",
        file_size=2048, status="saved", generated_at=datetime(2024, 1, 2),
    )


@pytest.fixture
def repos():
    asset_repo = AsyncMock(spec=AssetRepository)
    trade_repo = AsyncMock(spec=TradeRepository)
    deal_repo = AsyncMock(spec=DealRepository)
    operation_repo = AsyncMock(spec=OperationRepository)
    asset_repo.get_assets_by_range.return_value = make_assets(["100", "110", "121"])
    trade_repo.get_trades_by_range.return_value = [make_trade("100", trade_id=1)]
    deal_repo.get_deals_by_range.return_value = [
        make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100"),
    ]
    return asset_repo, trade_repo, deal_repo, operation_repo


@pytest.fixture
def store():
    s = AsyncMock(spec=ReportFileStore)
    s.list_reports.return_value = [_metadata(1), _metadata(2)]
    s.get_report.return_value = _metadata(1)
    s.load_report_bytes.return_value = b"%PDF-1.4 fake"
    s.save_report_file.return_value = ReportFileResult(
        report_id=9, file_uri="s3://reports/9.pdf", status="saved",
    )
    return s


@pytest.fixture
def client(repos, store):
    return TestClient(build_app(*repos, report_store=store))


class TestReportCenterAPI:

    def test_list_reports(self, client):
        resp = client.get("/api/v1/reports", params={"market_id": 1, "account_id": "acc_001"})
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_report_metadata(self, client):
        resp = client.get("/api/v1/reports/1")
        assert resp.status_code == 200
        assert resp.json()["report_id"] == 1

    def test_get_report_404(self, client, store):
        store.get_report.return_value = None
        resp = client.get("/api/v1/reports/123")
        assert resp.status_code == 404

    def test_download_report(self, client):
        resp = client.get("/api/v1/reports/1/download")
        assert resp.status_code == 200
        assert resp.content == b"%PDF-1.4 fake"
        assert "attachment" in resp.headers["content-disposition"]
        assert resp.headers["content-type"].startswith("application/pdf")

    def test_generate_daily_report(self, client, store):
        resp = client.post("/api/v1/reports/generate", json={
            "report_type": "daily", "market_id": 1, "account_id": "acc_001",
            "strategy_id": "s1", "period_date": "2024-01-01", "file_format": "csv",
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "saved"
        store.save_report_file.assert_awaited_once()

    def test_generate_daily_missing_strategy_422(self, client):
        resp = client.post("/api/v1/reports/generate", json={
            "report_type": "daily", "market_id": 1, "account_id": "acc_001",
            "period_date": "2024-01-01",
        })
        assert resp.status_code == 422

    def test_generate_unknown_type_422(self, client):
        resp = client.post("/api/v1/reports/generate", json={
            "report_type": "annual", "market_id": 1, "account_id": "acc_001",
            "strategy_id": "s1", "period_date": "2024-01-01",
        })
        assert resp.status_code == 422
