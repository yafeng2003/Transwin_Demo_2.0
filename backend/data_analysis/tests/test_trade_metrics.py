from decimal import Decimal

import pytest

from data_analysis.services.metrics import trade_metrics as tm
from data_analysis.tests.conftest import make_trade


class TestTradeMetrics:

    def test_mixed_trades(self):
        trades = [
            make_trade("100", trade_id=1),
            make_trade("50", trade_id=2),
            make_trade("-40", trade_id=3),
            make_trade("-10", trade_id=4),
        ]
        m = tm.analyze_trades(trades)

        assert m.total_trades == 4
        assert m.winning_trades == 2
        assert m.losing_trades == 2
        assert m.win_rate == pytest.approx(0.5)
        assert m.gross_profit == Decimal("150")
        assert m.gross_loss == Decimal("50")
        assert m.profit_factor == pytest.approx(3.0)
        assert m.payoff_ratio == pytest.approx(3.0)
        assert m.avg_trade_pnl == Decimal("25")
        assert m.expectancy == pytest.approx(Decimal("25"))
        assert m.total_commission == Decimal("4")
        assert m.avg_holding_seconds == pytest.approx(3600.0)

    def test_empty(self):
        m = tm.analyze_trades([])
        assert m.total_trades == 0
        assert m.win_rate == 0.0
        assert m.profit_factor is None
        assert m.payoff_ratio is None

    def test_all_wins_profit_factor_none(self):
        trades = [make_trade("10", trade_id=1), make_trade("20", trade_id=2)]
        m = tm.analyze_trades(trades)
        assert m.profit_factor is None
        assert m.payoff_ratio is None
        assert m.win_rate == 1.0

    def test_breakeven_not_counted_as_win(self):
        trades = [make_trade("0", trade_id=1), make_trade("10", trade_id=2)]
        m = tm.analyze_trades(trades)
        assert m.winning_trades == 1
        assert m.losing_trades == 0

    def test_open_trade_is_ignored(self):
        open_trade = make_trade("999", trade_id=2)
        open_trade.close_time = None
        open_trade.close_price = None

        m = tm.analyze_trades([make_trade("10", trade_id=1), open_trade])

        assert m.total_trades == 1
        assert m.gross_profit == Decimal("10")
