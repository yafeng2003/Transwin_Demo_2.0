from decimal import Decimal

import pytest

from data_analysis.services.metrics import trade_metrics as tm
from data_analysis.tests.conftest import make_deal, make_operation


class TestSlippage:

    def test_adverse_buy_fill(self):
        # 开多成交价 10.1，委托价 10.0，劣于委托：+100bps，成本 0.1*100=10
        deals = [make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10.1",
                           position_after="100", direction=1, operation_id=1)]
        ops = [make_operation(1, "10.0", direction=1, operation_type=1)]
        result = tm.compute_slippage(deals, ops)
        assert result.matched_count == 1
        assert result.avg_slippage_bps == pytest.approx(100.0)
        assert result.total_slippage_cost == Decimal("10.0")

    def test_favorable_buy_fill_is_negative(self):
        deals = [make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="9.9",
                           position_after="100", direction=1, operation_id=1)]
        ops = [make_operation(1, "10.0", direction=1, operation_type=1)]
        result = tm.compute_slippage(deals, ops)
        assert result.total_slippage_cost < Decimal("0")

    def test_unmatched_deal_skipped(self):
        deals = [make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10.1",
                           position_after="100", direction=1, operation_id=99)]
        ops = [make_operation(1, "10.0")]
        result = tm.compute_slippage(deals, ops)
        assert result.deal_count == 1
        assert result.matched_count == 0

    def test_deal_without_operation_id_skipped(self):
        deal = make_deal(1, 0, deal_type=1, deal_quantity="100", deal_price="10.1",
                         position_after="100", direction=1)
        deal.operation_id = None
        deals = [deal]
        ops = [make_operation(1, "10.0")]
        result = tm.compute_slippage(deals, ops)
        assert result.deal_count == 1
        assert result.matched_count == 0
