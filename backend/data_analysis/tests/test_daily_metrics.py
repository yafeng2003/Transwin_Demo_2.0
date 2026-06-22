from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from common.interfaces.analysis_interface import DailyMetricsStore
from common.interfaces.asset_repository import AssetRepository
from common.interfaces.trade_repository import TradeRepository
from data_analysis.services.aggregation import daily_metrics as dm
from data_analysis.tests.conftest import make_assets, make_trade


class TestComputeDailyMetrics:

    def test_returns_drawdown_and_trade_rollup(self):
        assets = make_assets(["100", "110", "121"])
        trades = [make_trade("50", commission="2", trade_id=1, close_day_offset=1)]
        metrics = dm.compute_daily_metrics(assets, trades, 1, "acc_001", "s1")

        assert len(metrics) == 3
        assert metrics[0].daily_return == pytest.approx(0.0)
        assert metrics[2].cumulative_return == pytest.approx(0.21)
        # 单调上升序列无回撤
        assert all(m.drawdown == pytest.approx(0.0) for m in metrics)
        # 交易落在第二天
        assert metrics[1].trade_count == 1
        assert metrics[1].realized_pnl == Decimal("50")
        assert metrics[1].commission == Decimal("2")

    def test_empty_assets(self):
        assert dm.compute_daily_metrics([], [], 1, "acc_001", "s1") == []

    def test_open_trade_is_ignored(self):
        open_trade = make_trade("999", trade_id=1)
        open_trade.close_time = None
        open_trade.close_price = None

        metrics = dm.compute_daily_metrics(make_assets(["100", "110"]), [open_trade], 1, "acc_001", "s1")

        assert sum(m.trade_count for m in metrics) == 0
        assert sum(m.realized_pnl for m in metrics) == Decimal("0")


class TestDailyAggregationService:

    async def test_run_upserts_metrics(self):
        asset_repo = AsyncMock(spec=AssetRepository)
        trade_repo = AsyncMock(spec=TradeRepository)
        asset_repo.get_assets_by_range.return_value = make_assets(["100", "110", "121"])
        trade_repo.get_trades_by_range.return_value = [make_trade("50", trade_id=1, close_day_offset=1)]
        store = AsyncMock(spec=DailyMetricsStore)
        store.upsert_daily_metrics.return_value = 3

        service = dm.DailyAggregationService(asset_repo, trade_repo, store)
        count = await service.run(1, "acc_001", "s1", datetime.min, datetime.max)

        assert count == 3
        store.upsert_daily_metrics.assert_awaited_once()
        upserted = store.upsert_daily_metrics.await_args[0][0]
        assert len(upserted) == 3
        assert all(m.strategy_id == "s1" for m in upserted)
