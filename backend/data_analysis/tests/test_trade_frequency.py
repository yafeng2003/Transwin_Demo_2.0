import pytest

from data_analysis.services.metrics import trade_metrics as tm
from data_analysis.tests.conftest import make_trade


class TestTradeFrequency:

    def test_same_day_uses_one_day_floor(self):
        trades = [make_trade("10", trade_id=i, close_day_offset=0) for i in range(4)]
        freq = tm.compute_trade_frequency(trades)
        assert freq.trades_per_day == pytest.approx(4.0)
        assert freq.trades_per_week == pytest.approx(28.0)

    def test_multi_day_span(self):
        trades = [
            make_trade("10", trade_id=1, close_day_offset=0),
            make_trade("10", trade_id=2, close_day_offset=10),
        ]
        freq = tm.compute_trade_frequency(trades)
        assert freq.span_days == pytest.approx(10.0)
        assert freq.trades_per_day == pytest.approx(0.2)

    def test_empty(self):
        freq = tm.compute_trade_frequency([])
        assert freq.total_trades == 0
        assert freq.trades_per_day == 0.0
