"""数据分析层 HTTP API 测试：按前端契约校验 4 个组合接口。

伪仓储用 AsyncMock 且忽略日期区间，返回固定数据，故 period 换算日期后结果确定。
"""

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

_ACCOUNT = {"market_id": 1, "account_id": "acc_001"}


@pytest.fixture
def repos():
    asset_repo = AsyncMock(spec=AssetRepository)
    trade_repo = AsyncMock(spec=TradeRepository)
    deal_repo = AsyncMock(spec=DealRepository)
    operation_repo = AsyncMock(spec=OperationRepository)
    asset_repo.get_assets_by_range.return_value = make_assets(["100", "110", "121"])
    # 两个策略，含盈亏，平仓落在不同月份，便于校验胜率/月度/策略对比
    trade_repo.get_trades_by_range.return_value = [
        make_trade("100", trade_id=1, strategy_id="s1", return_rate="0.10", close_day_offset=10),
        make_trade("-50", trade_id=2, strategy_id="s1", return_rate="-0.05", close_day_offset=40),
        make_trade("80", trade_id=3, strategy_id="s2", return_rate="0.08", close_day_offset=12),
    ]
    deal_repo.get_deals_by_range.return_value = [
        make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10",
                  position_after="100", strategy_id="s1", symbol_code="600001.SH", operation_id=1),
        make_deal(2, 1, deal_type=1, deal_quantity="50", deal_price="20",
                  position_after="50", strategy_id="s2", symbol_code="600002.SH", operation_id=2),
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
        resp = client.get("/api/v1/analysis/returns", params={**_ACCOUNT, "period": "3m"})
        assert resp.status_code == 200
        body = resp.json()
        # ApiResponse 信封
        assert body["code"] == 200 and body["msg"] == "success"
        summary = body["data"]["summary"]
        assert set(summary) == {
            "totalReturn", "annualReturn", "sharpeRatio",
            "maxDrawdown", "calmarRatio", "winRate",
        }
        assert summary["totalReturn"] == pytest.approx(21.0)   # 100 -> 121
        assert summary["winRate"] == pytest.approx(66.7)       # 3 笔 2 胜
        daily = body["data"]["dailyReturns"]
        assert len(daily) == 3
        assert set(daily[0]) == {"date", "dailyReturn", "cumulativeReturn", "netValue"}
        assert daily[-1]["cumulativeReturn"] == pytest.approx(21.0)

    def test_risk(self, client):
        resp = client.get("/api/v1/analysis/risk", params={**_ACCOUNT, "period": "3m"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert set(data) == {"volatility", "downsideVolatility", "drawdownDistribution", "riskExposure"}
        assert {item["range"] for item in data["drawdownDistribution"]} == {
            "0~2%", "2~4%", "4~6%", "6~8%", "8%+",
        }
        exposure = data["riskExposure"]
        assert set(exposure) == {"sectors", "strategies", "heatmapData"}
        assert exposure["strategies"] == ["s1", "s2"]

    def test_trading(self, client):
        resp = client.get("/api/v1/analysis/trading", params={**_ACCOUNT, "period": "3m"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert set(data) == {
            "winRate", "profitLossRatio", "avgProfit", "avgLoss", "tradeCount",
            "tradeFrequency", "totalCommission", "slippage", "monthlyTrades",
        }
        assert data["profitLossRatio"] == pytest.approx(1.8)   # avg win 90 / avg loss 50
        assert data["avgProfit"] == pytest.approx(90.0)
        assert data["avgLoss"] == pytest.approx(-50.0)
        assert data["tradeCount"] == 3
        months = {m["month"]: m for m in data["monthlyTrades"]}
        assert months["2024-01"]["count"] == 2 and months["2024-01"]["winRate"] == pytest.approx(100.0)
        assert months["2024-02"]["winRate"] == pytest.approx(0.0)

    def test_strategy(self, client):
        resp = client.get("/api/v1/analysis/strategy", params=_ACCOUNT)
        assert resp.status_code == 200
        rows = resp.json()["data"]
        assert isinstance(rows, list) and len(rows) == 2
        keys = {"strategyId", "strategyName", "totalReturn", "sharpeRatio",
                "maxDrawdown", "winRate", "tradeCount", "contribution", "correlation"}
        assert all(set(r) == keys for r in rows)
        by_id = {r["strategyId"]: r for r in rows}
        # 贡献度合计 ~100%（s1 已实现 50，s2 80）
        assert by_id["s1"]["contribution"] + by_id["s2"]["contribution"] == pytest.approx(100.0, abs=0.2)
        assert by_id["s1"]["winRate"] == pytest.approx(50.0)
        # 相关性为 [{strategy,value}] 数组，自相关为 1
        self_corr = next(c["value"] for c in by_id["s1"]["correlation"] if c["strategy"] == "s1")
        assert self_corr == pytest.approx(1.0)

    @pytest.mark.parametrize("period", ["1m", "3m", "6m", "1y", "bogus"])
    def test_period_param_accepted(self, client, period):
        # 任意 period（含非法值回退默认）都应正常返回，不报错
        resp = client.get("/api/v1/analysis/returns", params={**_ACCOUNT, "period": period})
        assert resp.status_code == 200
