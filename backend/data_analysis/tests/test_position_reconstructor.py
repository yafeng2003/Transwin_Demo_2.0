from datetime import datetime, timedelta
from decimal import Decimal

from data_analysis.services.position_reconstructor import reconstruct_positions
from data_analysis.tests.conftest import _BASE, make_deal


class TestPositionReconstructor:

    def test_weighted_average_cost_after_partial_close(self):
        deals = [
            make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100"),
            make_deal(2, 1, deal_type=1, deal_quantity="100", deal_price="12", position_after="200"),
            make_deal(3, 2, deal_type=2, deal_quantity="50", deal_price="13", position_after="150"),
        ]
        snapshot = reconstruct_positions(
            deals, market_id=1, account_id="acc_001", strategy_id="s1",
            query_time=_BASE + timedelta(days=3),
        )
        assert len(snapshot.active_positions) == 1
        pos = snapshot.active_positions[0]
        assert pos.holding_quantity == Decimal("150")
        # 均价由两笔开仓加权：(10*100 + 12*100) / 200 = 11，平仓不改变成本
        assert pos.open_price == Decimal("11")
        assert pos.holding_amount == Decimal("1650")
        assert pos.open_time == _BASE

    def test_query_time_filters_future_deals(self):
        deals = [
            make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100"),
            make_deal(2, 5, deal_type=1, deal_quantity="100", deal_price="12", position_after="200"),
        ]
        snapshot = reconstruct_positions(
            deals, market_id=1, account_id="acc_001", strategy_id="s1",
            query_time=_BASE + timedelta(days=1),
        )
        assert snapshot.active_positions[0].holding_quantity == Decimal("100")

    def test_fully_closed_position_removed(self):
        deals = [
            make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100"),
            make_deal(2, 1, deal_type=2, deal_quantity="100", deal_price="11", position_after="0"),
        ]
        snapshot = reconstruct_positions(
            deals, market_id=1, account_id="acc_001", strategy_id="s1",
            query_time=_BASE + timedelta(days=2),
        )
        assert snapshot.active_positions == []

    def test_empty_deals(self):
        snapshot = reconstruct_positions(
            [], market_id=1, account_id="acc_001", strategy_id="s1", query_time=_BASE,
        )
        assert snapshot.active_positions == []
        assert snapshot.current_time == _BASE


class TestMarkToMarket:

    def test_long_unrealized_pnl_with_price(self):
        deals = [
            make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100"),
        ]
        # 多头持仓 100 股、均价 10，现价 12 -> 浮盈 (12-10)*100 = 200
        snapshot = reconstruct_positions(
            deals, market_id=1, account_id="acc_001", strategy_id="s1",
            query_time=_BASE + timedelta(days=1), prices={"600001.SH": Decimal("12")},
        )
        assert snapshot.active_positions[0].unrealized_pnl == Decimal("200")

    def test_short_unrealized_pnl_with_price(self):
        deals = [
            make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10",
                      position_after="100", direction=2),
        ]
        # 空头价跌为盈：均价 10、现价 8 -> 浮盈 (10-8)*100 = 200
        snapshot = reconstruct_positions(
            deals, market_id=1, account_id="acc_001", strategy_id="s1",
            query_time=_BASE + timedelta(days=1), prices={"600001.SH": Decimal("8")},
        )
        assert snapshot.active_positions[0].unrealized_pnl == Decimal("200")

    def test_no_price_yields_zero_unrealized(self):
        deals = [
            make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10", position_after="100"),
        ]
        snapshot = reconstruct_positions(
            deals, market_id=1, account_id="acc_001", strategy_id="s1",
            query_time=_BASE + timedelta(days=1),
        )
        assert snapshot.active_positions[0].unrealized_pnl == Decimal("0")
