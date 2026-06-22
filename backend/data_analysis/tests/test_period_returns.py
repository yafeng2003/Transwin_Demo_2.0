import pytest

from data_analysis.services.metrics import return_metrics as rm
from data_analysis.tests.conftest import make_asset, make_assets


class TestPeriodReturns:

    def test_daily_returns(self):
        result = rm.period_returns(make_assets(["100", "110", "121"]), "daily")
        assert result.granularity == "daily"
        assert len(result.items) == 2
        assert result.items[0].return_rate == pytest.approx(0.1)
        assert result.items[1].return_rate == pytest.approx(0.1)

    def test_monthly_returns_span_two_months(self):
        # Jan 1 与 Feb 10，月末重采样后得到一段月度收益 0.3
        assets = [make_asset(0, "100"), make_asset(40, "130")]
        result = rm.period_returns(assets, "monthly")
        assert len(result.items) == 1
        assert result.items[0].return_rate == pytest.approx(0.3)
        assert result.items[0].period_label == "2024-02"

    def test_insufficient_data_returns_empty(self):
        assert rm.period_returns(make_assets(["100"]), "daily").items == []

    def test_invalid_granularity_raises(self):
        with pytest.raises(ValueError):
            rm.period_returns(make_assets(["100", "110"]), "yearly")
