import pytest

from data_analysis.services.metrics import risk_metrics as rk


class TestReturnDistribution:

    def test_counts_and_bounds(self):
        # 净值序列 -> 收益 [0.1, -0.1, 0.1]
        dist = rk.return_distribution([100.0, 110.0, 99.0, 108.9], bins=4)
        assert sum(b.count for b in dist.bins) == 3
        assert dist.min_return == pytest.approx(-0.1)
        assert dist.max_return == pytest.approx(0.1)

    def test_empty_series(self):
        dist = rk.return_distribution([100.0])
        assert dist.bins == []
        assert dist.mean == 0.0

    def test_symmetry_zero_skew(self):
        # 对称收益分布偏度约为 0
        dist = rk.return_distribution([100.0, 110.0, 99.0], bins=5)
        assert dist.skewness == pytest.approx(0.0, abs=1e-9)
