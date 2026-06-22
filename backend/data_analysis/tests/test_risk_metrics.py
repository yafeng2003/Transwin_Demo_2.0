import math

import pytest

from data_analysis.services.metrics import risk_metrics as risk
from data_analysis.tests.conftest import make_assets


class TestRiskMetrics:

    def test_max_drawdown(self):
        # 峰值 120，谷底 90，回撤 (90-120)/120 = 25%
        values = [100.0, 120.0, 90.0, 110.0]
        assert risk.max_drawdown(values) == pytest.approx(0.25)

    def test_max_drawdown_no_decline(self):
        assert risk.max_drawdown([100.0, 110.0, 120.0]) == 0.0

    def test_max_drawdown_duration(self):
        values = [100.0, 120.0, 90.0, 110.0]
        # idx2、idx3 连续水下，最长水下周期 = 2
        assert risk.max_drawdown_duration(values) == 2

    def test_drawdown_series_values(self):
        values = [100.0, 120.0, 90.0]
        series = risk.drawdown_series(values).tolist()
        assert series == pytest.approx([0.0, 0.0, -0.25])

    def test_annualized_volatility(self):
        values = [100.0, 120.0, 90.0, 110.0]
        returns = [0.2, -0.25, 110.0 / 90.0 - 1.0]
        mean = sum(returns) / 3
        var = sum((r - mean) ** 2 for r in returns) / 2
        expected = math.sqrt(var) * math.sqrt(252)
        assert risk.annualized_volatility(values, 252) == pytest.approx(expected, rel=1e-9)

    def test_historical_var(self):
        values = [100.0, 120.0, 90.0, 110.0]
        # returns 排序后 5% 分位线性插值 = -0.205，VaR 取正
        assert risk.historical_var(values, 0.95) == pytest.approx(0.205, rel=1e-9)

    def test_analyze_risk_empty(self):
        metrics = risk.analyze_risk([], periods_per_year=252)
        assert metrics.max_drawdown == 0.0
        assert metrics.annualized_volatility == 0.0
        assert metrics.var_95 == 0.0

    def test_build_drawdown_series_aligns_time(self):
        assets = make_assets(["100", "120", "90"])
        points = risk.build_drawdown_series(assets)
        assert len(points) == 3
        assert points[-1].drawdown == pytest.approx(-0.25)
