from decimal import Decimal

import pytest

from data_analysis.services.metrics import strategy_metrics as sm
from data_analysis.tests.conftest import make_trade


class TestStrategyContribution:

    def test_contribution_shares(self):
        result = sm.compute_contributions({"A": Decimal("60"), "B": Decimal("40")})
        by_id = {c.strategy_id: c.contribution for c in result}
        assert by_id["A"] == pytest.approx(0.6)
        assert by_id["B"] == pytest.approx(0.4)

    def test_contribution_zero_total(self):
        result = sm.compute_contributions({"A": Decimal("10"), "B": Decimal("-10")})
        assert all(c.contribution == 0.0 for c in result)


class TestStrategyCorrelation:

    def test_perfect_positive_correlation(self):
        series = {"A": [0.1, 0.2, 0.3], "B": [0.2, 0.4, 0.6]}
        corr = sm.compute_correlation(series)
        assert corr is not None
        assert corr.matrix[0][1] == pytest.approx(1.0)

    def test_perfect_negative_correlation(self):
        series = {"A": [0.1, 0.2, 0.3], "B": [-0.1, -0.2, -0.3]}
        corr = sm.compute_correlation(series)
        assert corr.matrix[0][1] == pytest.approx(-1.0)

    def test_single_strategy_returns_none(self):
        assert sm.compute_correlation({"A": [0.1, 0.2]}) is None

    def test_mismatched_lengths_returns_none(self):
        assert sm.compute_correlation({"A": [0.1, 0.2], "B": [0.1]}) is None


class TestStrategyPerformance:

    def test_performance_basic_stats(self):
        trades = [
            make_trade("100", return_rate="0.1", trade_id=1),
            make_trade("-40", return_rate="-0.04", trade_id=2),
            make_trade("60", return_rate="0.06", trade_id=3),
        ]
        perf = sm.strategy_performance("A", trades)
        assert perf.total_trades == 3
        assert perf.realized_pnl == Decimal("120")
        assert perf.win_rate == pytest.approx(2 / 3)
        # Profit Factor = 总盈利160 / 总亏损40 = 4.0
        assert perf.profit_factor == pytest.approx(4.0)

    def test_max_drawdown_amount_on_cumulative_pnl(self):
        # 累计已实现：100 -> 60 -> 110，峰值100后回落到60，金额回撤=40
        trades = [
            make_trade("100", trade_id=1, close_day_offset=0),
            make_trade("-40", trade_id=2, close_day_offset=1),
            make_trade("50", trade_id=3, close_day_offset=2),
        ]
        amount = sm.max_drawdown_amount(sm.build_cumulative_realized_pnl(trades))
        assert amount == Decimal("40")

    def test_empty_trades(self):
        perf = sm.strategy_performance("A", [])
        assert perf.total_trades == 0
        assert perf.realized_pnl == Decimal("0")

    def test_open_trade_is_ignored(self):
        open_trade = make_trade("999", trade_id=2)
        open_trade.close_time = None
        open_trade.close_price = None

        perf = sm.strategy_performance("A", [make_trade("10", trade_id=1), open_trade])

        assert perf.total_trades == 1
        assert perf.realized_pnl == Decimal("10")


class TestCompareStrategies:

    def test_compare_builds_contributions_and_performances(self):
        trades_by_strategy = {
            "A": [make_trade("60", trade_id=1, strategy_id="A", close_day_offset=0)],
            "B": [make_trade("40", trade_id=2, strategy_id="B", close_day_offset=1)],
        }
        result = sm.compare_strategies(trades_by_strategy)
        assert len(result.contributions) == 2
        assert len(result.performances) == 2
        by_id = {c.strategy_id: c.contribution for c in result.contributions}
        assert by_id["A"] == pytest.approx(0.6)

    def test_correlation_from_aligned_daily_pnl(self):
        # 两策略每日盈亏完全同向，相关性应为 1
        trades_by_strategy = {
            "A": [
                make_trade("10", trade_id=1, strategy_id="A", close_day_offset=0),
                make_trade("20", trade_id=2, strategy_id="A", close_day_offset=1),
            ],
            "B": [
                make_trade("5", trade_id=3, strategy_id="B", close_day_offset=0),
                make_trade("10", trade_id=4, strategy_id="B", close_day_offset=1),
            ],
        }
        result = sm.compare_strategies(trades_by_strategy)
        assert result.correlation is not None
        assert result.correlation.matrix[0][1] == pytest.approx(1.0)
