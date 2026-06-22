import math

import pytest

from data_analysis.services.metrics import return_metrics as rm
from data_analysis.tests.conftest import make_assets


class TestReturnMetrics:

    def test_cumulative_return(self):
        values = [100.0, 110.0, 121.0]
        assert rm.cumulative_return(values) == pytest.approx(0.21)

    def test_cumulative_return_insufficient_points(self):
        assert rm.cumulative_return([100.0]) == 0.0
        assert rm.cumulative_return([]) == 0.0

    def test_annualized_return_clean(self):
        # 两期各 +10%，ppy=2 时年化应等于区间累计 0.21
        values = [100.0, 110.0, 121.0]
        assert rm.annualized_return(values, periods_per_year=2) == pytest.approx(0.21)

    def test_sharpe_zero_volatility(self):
        # 收益恒定，标准差为 0，夏普定义为 0
        values = [100.0, 110.0, 121.0]
        assert rm.sharpe_ratio(values, periods_per_year=252, annual_risk_free_rate=0.0) == 0.0

    def test_sharpe_known_value(self):
        values = [100.0, 101.0, 104.03]  # 收益 [0.01, 0.03]
        mean, std = 0.02, math.sqrt(0.0002)
        expected = mean / std * math.sqrt(252)
        result = rm.sharpe_ratio(values, periods_per_year=252, annual_risk_free_rate=0.0)
        assert result == pytest.approx(expected, rel=1e-9)

    def test_simple_returns_skips_zero_denominator(self):
        result = rm.simple_returns([0.0, 100.0, 110.0])
        assert result.tolist() == pytest.approx([0.1])

    def test_build_equity_curve(self):
        assets = make_assets(["100", "110", "121"])
        curve = rm.build_equity_curve(assets)
        assert len(curve.points) == 3
        assert curve.points[0].cumulative_return == pytest.approx(0.0)
        assert curve.points[-1].cumulative_return == pytest.approx(0.21)

    def test_build_equity_curve_empty(self):
        assert rm.build_equity_curve([]).points == []

    def test_analyze_returns_uses_sorted_input(self):
        assets = list(reversed(make_assets(["100", "110", "121"])))
        metrics = rm.analyze_returns(assets, periods_per_year=2)
        assert metrics.period_count == 2
        assert metrics.cumulative_return == pytest.approx(0.21)
        assert float(metrics.start_net_value) == 100.0
        assert float(metrics.end_net_value) == 121.0
