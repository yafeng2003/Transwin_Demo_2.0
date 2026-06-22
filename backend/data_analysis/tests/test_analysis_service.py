from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from common.interfaces.asset_repository import AssetRepository
from common.interfaces.deal_repository import DealRepository
from common.interfaces.operation_repository import OperationRepository
from common.interfaces.trade_repository import TradeRepository
from data_analysis.config import AnalysisConfig
from data_analysis.services.analysis_service import AnalysisService
from data_analysis.tests.conftest import make_assets, make_deal, make_trade


class TestAnalysisService:

    @pytest.fixture
    def repos(self):
        return {
            "asset": AsyncMock(spec=AssetRepository),
            "trade": AsyncMock(spec=TradeRepository),
            "deal": AsyncMock(spec=DealRepository),
            "operation": AsyncMock(spec=OperationRepository),
        }

    @pytest.fixture
    def service(self, repos):
        return AnalysisService(
            repos["asset"], repos["trade"], repos["deal"], repos["operation"], config=AnalysisConfig()
        )

    async def test_get_return_metrics_pulls_assets(self, service, repos):
        repos["asset"].get_assets_by_range.return_value = make_assets(["100", "110", "121"])
        metrics = await service.get_return_metrics(1, "acc_001", datetime.min, datetime.max)

        repos["asset"].get_assets_by_range.assert_awaited_once()
        assert metrics.cumulative_return == pytest.approx(0.21)

    async def test_get_trade_metrics_pulls_trades(self, service, repos):
        repos["trade"].get_trades_by_range.return_value = [make_trade("100", trade_id=1), make_trade("-50", trade_id=2)]
        metrics = await service.get_trade_metrics(1, "acc_001", "s1", datetime.min, datetime.max)

        repos["trade"].get_trades_by_range.assert_awaited_once()
        assert metrics.total_trades == 2
        assert metrics.win_rate == pytest.approx(0.5)

    async def test_get_positions_reconstructs_from_deals(self, service, repos):
        repos["deal"].get_deals_by_range.return_value = [
            make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100"),
        ]
        snapshot = await service.get_positions(1, "acc_001", "s1", datetime(2024, 6, 1))

        repos["deal"].get_deals_by_range.assert_awaited_once()
        assert snapshot.active_positions[0].holding_quantity == Decimal("100")

    async def test_compare_strategies_aggregates_pnl(self, service, repos):
        async def fake_trades(account_id, strategy_id, market_id, start, end):
            mapping = {
                "A": [make_trade("60", trade_id=1, strategy_id="A")],
                "B": [make_trade("40", trade_id=2, strategy_id="B")],
            }
            return mapping[strategy_id]

        repos["trade"].get_trades_by_range.side_effect = fake_trades
        result = await service.compare_strategies(1, "acc_001", ["A", "B"], datetime.min, datetime.max)

        by_id = {c.strategy_id: c.contribution for c in result.contributions}
        assert by_id["A"] == pytest.approx(0.6)
        assert by_id["B"] == pytest.approx(0.4)

    async def test_market_specific_annualization(self, repos):
        # 加密货币按 365 年化，与默认 252 不同，验证 config 口径生效
        crypto = AnalysisService(
            repos["asset"], repos["trade"], repos["deal"], repos["operation"], config=AnalysisConfig()
        )
        repos["asset"].get_assets_by_range.return_value = make_assets(["100", "101", "104.03"], market_id=5)
        m_crypto = await crypto.get_return_metrics(5, "acc_001", datetime.min, datetime.max)
        repos["asset"].get_assets_by_range.return_value = make_assets(["100", "101", "104.03"], market_id=3)
        m_us = await crypto.get_return_metrics(3, "acc_001", datetime.min, datetime.max)
        assert m_crypto.sharpe_ratio != pytest.approx(m_us.sharpe_ratio)


class TestPriceProviderIntegration:

    async def test_positions_marked_to_market_via_provider(self):
        from common.interfaces.analysis_interface import PriceProvider

        asset_repo = AsyncMock(spec=AssetRepository)
        trade_repo = AsyncMock(spec=TradeRepository)
        deal_repo = AsyncMock(spec=DealRepository)
        operation_repo = AsyncMock(spec=OperationRepository)
        deal_repo.get_deals_by_range.return_value = [
            make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100"),
        ]
        prices = AsyncMock(spec=PriceProvider)
        prices.get_prices.return_value = {"600001.SH": Decimal("12")}

        service = AnalysisService(
            asset_repo, trade_repo, deal_repo, operation_repo,
            config=AnalysisConfig(), price_provider=prices,
        )
        snapshot = await service.get_positions(1, "acc_001", "s1", datetime(2024, 6, 1))

        prices.get_prices.assert_awaited_once()
        assert snapshot.active_positions[0].unrealized_pnl == Decimal("200")
