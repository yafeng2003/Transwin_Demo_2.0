from datetime import datetime
from decimal import Decimal

from common.models.analytics import (
    ReturnMetrics,
    RiskMetrics,
    StrategyComparison,
    StrategyPerformance,
    TradeMetrics,
)
from common.models.trading import ActivePosition, ActivePositions
from data_analysis.services.report import report_content as rc
from data_analysis.tests.conftest import make_assets, make_deal, make_trade


def _returns():
    return ReturnMetrics(period_count=2, cumulative_return=0.21, annualized_return=0.5, sharpe_ratio=1.2)


def _risk():
    return RiskMetrics(
        max_drawdown=0.1, max_drawdown_duration=2, annualized_volatility=0.3,
        return_mean=0.01, return_std=0.02, var_95=0.05,
    )


def _trades_metric():
    return TradeMetrics(
        total_trades=2, winning_trades=1, losing_trades=1, win_rate=0.5,
        gross_profit=Decimal("100"), gross_loss=Decimal("50"), profit_factor=2.0,
        payoff_ratio=2.0, avg_trade_pnl=Decimal("25"), expectancy=Decimal("25"),
        total_commission=Decimal("2"), avg_holding_seconds=3600.0,
    )


def _positions():
    return ActivePositions(
        market_id=1, account_id="acc_001", strategy_id="s1", current_time=datetime(2024, 1, 1),
        active_positions=[
            ActivePosition(
                symbol_code="600001.SH", position_type=1, direction=1, open_price=Decimal("10"),
                holding_quantity=Decimal("100"), holding_amount=Decimal("1000"),
                open_time=datetime(2024, 1, 1), unrealized_pnl=Decimal("0"),
            )
        ],
    )


class TestDailyReportContent:

    def test_structure_and_sections(self):
        deals = [make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100")]
        content = rc.build_daily_report(
            1, "acc_001", "s1", datetime(2024, 1, 1), datetime(2024, 1, 1, 23, 59),
            deals, _positions(), make_assets(["100", "110"]),
            _returns(), _risk(), _trades_metric(), datetime(2024, 1, 2),
        )
        assert content.report_type == "daily"
        titles = [s.title for s in content.sections]
        assert "当日成交记录" in titles
        assert "持仓结构与仓位占比" in titles
        summary_names = [name for name, _ in content.summary]
        assert "累计收益率" in summary_names


class TestWeeklyReportContent:

    def test_includes_trade_count_and_ranking(self):
        trades = [
            make_trade("100", return_rate="0.1", trade_id=1, close_day_offset=0),
            make_trade("-30", return_rate="-0.03", trade_id=2, close_day_offset=1),
        ]
        content = rc.build_weekly_report(
            1, "acc_001", "s1", datetime(2024, 1, 1), datetime(2024, 1, 7),
            trades, make_assets(["100", "110"]),
            _returns(), _risk(), _trades_metric(), datetime(2024, 1, 8),
        )
        assert content.report_type == "weekly"
        summary = dict(content.summary)
        assert summary["本周交易次数"] == "2"
        ranking = next(s for s in content.sections if s.title == "收益率排名")
        # 收益率降序，盈利标的在前
        assert ranking.rows[0][1].startswith("10")


class TestMonthlyReportContent:

    def test_strategy_performance_section(self):
        comparison = StrategyComparison(
            performances=[
                StrategyPerformance(
                    strategy_id="A", realized_pnl=Decimal("120"), total_trades=3, win_rate=0.66,
                    profit_factor=4.0, avg_return_rate=0.04, return_rate_std=0.07,
                    trade_sharpe=0.57, max_drawdown_amount=Decimal("40"),
                )
            ],
            contributions=[],
            correlation=None,
        )
        content = rc.build_monthly_report(
            1, "acc_001", datetime(2024, 1, 1), datetime(2024, 1, 31),
            _positions(), comparison, _returns(), _risk(), _trades_metric(), datetime(2024, 2, 1),
        )
        assert content.report_type == "monthly"
        perf_section = next(s for s in content.sections if s.title == "策略绩效分析")
        assert perf_section.rows[0][0] == "A"
        # 未注入行业映射时应保留显式占位
        industry = next(s for s in content.sections if s.title == "行业配置")
        assert industry.rows[0][0] == "未接入行业映射"
