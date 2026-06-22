"""前端组合接口新增算法与 builder 的单元测试。"""

import math
from decimal import Decimal

import pytest

from data_analysis.services import frontend_views
from data_analysis.services.metrics.return_metrics import calmar_ratio
from data_analysis.services.metrics.risk_metrics import downside_deviation, drawdown_distribution
from data_analysis.services.metrics.trade_metrics import monthly_trade_stats
from data_analysis.tests.conftest import make_assets, make_deal, make_operation, make_trade


class TestNewMetrics:

    def test_calmar(self):
        assert calmar_ratio(0.2, 0.1) == pytest.approx(2.0)
        assert calmar_ratio(-0.1, 0.2) == pytest.approx(-0.5)
        assert calmar_ratio(0.2, 0.0) == 0.0          # 无回撤 -> 0

    def test_downside_deviation(self):
        # 仅一个 -10% 收益：sqrt(0.1^2) * sqrt(ppy)
        assert downside_deviation([100, 90], 252) == pytest.approx(0.1 * math.sqrt(252))
        # 全为正收益 -> 下行波动 0
        assert downside_deviation([100, 110], 252) == 0.0

    def test_drawdown_distribution(self):
        # 深度: 0,0.1,0.05,0,0.2
        dist = dict(drawdown_distribution([100, 90, 95, 100, 80]))
        assert dist["0~2%"] == 2
        assert dist["4~6%"] == 1
        assert dist["8%+"] == 2
        assert dist["2~4%"] == 0

    def test_monthly_trade_stats_groups_by_close_month(self):
        trades = [
            make_trade("10", trade_id=1, close_day_offset=5),    # 1 月，盈
            make_trade("-5", trade_id=2, close_day_offset=20),   # 1 月，亏
            make_trade("20", trade_id=3, close_day_offset=40),   # 2 月，盈
        ]
        stats = dict((m, (c, wr)) for m, c, wr in monthly_trade_stats(trades))
        assert stats["2024-01"] == (2, pytest.approx(0.5))
        assert stats["2024-02"] == (1, pytest.approx(1.0))

    def test_monthly_trade_stats_skips_open_trades(self):
        t = make_trade("10", trade_id=1)
        t.close_time = None      # 未平仓交易不计入
        assert monthly_trade_stats([t]) == []


class TestFrontendBuilders:

    def test_build_returns_view(self):
        assets = make_assets(["100", "110", "121"])
        trades = [make_trade("100", trade_id=1), make_trade("-50", trade_id=2)]
        view = frontend_views.build_returns_view(assets, trades, 244, 0.0, "net_value")
        assert view["summary"]["totalReturn"] == pytest.approx(21.0)
        assert view["summary"]["winRate"] == pytest.approx(50.0)
        assert view["summary"]["maxDrawdown"] == 0.0          # 单调上行无回撤(非 -0.0)
        assert len(view["dailyReturns"]) == 3

    def test_build_trading_view(self):
        trades = [
            make_trade("100", trade_id=1, close_day_offset=10),
            make_trade("-50", trade_id=2, close_day_offset=12),
        ]
        deals = [make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10.1",
                           position_after="100", operation_id=1)]
        operations = [make_operation(1, "10.0")]
        view = frontend_views.build_trading_view(trades, deals, operations)
        assert view["winRate"] == pytest.approx(50.0)
        assert view["avgProfit"] == pytest.approx(100.0)
        assert view["avgLoss"] == pytest.approx(-50.0)
        assert view["profitLossRatio"] == pytest.approx(2.0)

    def test_build_strategy_view_proxies_and_correlation(self):
        trades_by_strategy = {
            "s1": [make_trade("100", trade_id=1, strategy_id="s1", return_rate="0.10", close_day_offset=10),
                   make_trade("-50", trade_id=2, strategy_id="s1", return_rate="-0.05", close_day_offset=40)],
            "s2": [make_trade("80", trade_id=3, strategy_id="s2", return_rate="0.08", close_day_offset=12)],
        }
        rows = frontend_views.build_strategy_view(trades_by_strategy)
        by_id = {r["strategyId"]: r for r in rows}
        # 总收益代理 = 单笔收益率连乘：s1 (1.1*0.95-1)=4.5%
        assert by_id["s1"]["totalReturn"] == pytest.approx(4.5)
        # 最大回撤代理：累计已实现盈亏 100->50，回撤 50%
        assert by_id["s1"]["maxDrawdown"] == pytest.approx(-50.0)
        assert by_id["s2"]["maxDrawdown"] == 0.0
        # 贡献度合计 100%
        assert sum(r["contribution"] for r in rows) == pytest.approx(100.0, abs=0.2)
