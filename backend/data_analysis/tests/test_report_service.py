from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from common.interfaces.analysis_interface import ReportFileStore
from common.interfaces.asset_repository import AssetRepository
from common.interfaces.deal_repository import DealRepository
from common.interfaces.trade_repository import TradeRepository
from common.models.analytics import ReportFile, ReportFileResult
from data_analysis.config import AnalysisConfig
from data_analysis.services.report.report_service import ReportService
from data_analysis.tests.conftest import make_assets, make_deal, make_trade


@pytest.fixture
def repos():
    asset_repo = AsyncMock(spec=AssetRepository)
    trade_repo = AsyncMock(spec=TradeRepository)
    deal_repo = AsyncMock(spec=DealRepository)
    asset_repo.get_assets_by_range.return_value = make_assets(["100", "110", "121"])
    trade_repo.get_trades_by_range.return_value = [make_trade("100", trade_id=1), make_trade("-50", trade_id=2)]
    deal_repo.get_deals_by_range.return_value = [
        make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100"),
    ]
    return asset_repo, trade_repo, deal_repo


@pytest.fixture
def store():
    s = AsyncMock(spec=ReportFileStore)
    s.save_report_file.return_value = ReportFileResult(
        report_id=1, file_uri="s3://reports/1.pdf", status="saved",
    )
    return s


class TestReportService:

    async def test_daily_report_renders_and_persists_pdf(self, repos, store):
        service = ReportService(*repos, store, AnalysisConfig())
        result = await service.generate_daily_report(1, "acc_001", "s1", date(2024, 1, 1), "pdf")

        store.save_report_file.assert_awaited_once()
        saved: ReportFile = store.save_report_file.await_args[0][0]
        assert saved.report_type == "daily"
        assert saved.file_format == "pdf"
        assert saved.content[:4] == b"%PDF"
        assert result.status == "saved"

    async def test_weekly_report_csv(self, repos, store):
        service = ReportService(*repos, store, AnalysisConfig())
        await service.generate_weekly_report(1, "acc_001", "s1", date(2024, 1, 1), "csv")
        saved: ReportFile = store.save_report_file.await_args[0][0]
        assert saved.report_type == "weekly"
        assert saved.content.startswith(b"\xef\xbb\xbf")

    async def test_monthly_report_aggregates_strategies(self, repos, store):
        service = ReportService(*repos, store, AnalysisConfig())
        await service.generate_monthly_report(1, "acc_001", ["A", "B"], date(2024, 1, 15), "xlsx")
        saved: ReportFile = store.save_report_file.await_args[0][0]
        assert saved.report_type == "monthly"
        assert saved.content[:2] == b"PK"
        # 月报跨两个策略，trades 至少被各取一次
        assert repos[1].get_trades_by_range.await_count >= 2
