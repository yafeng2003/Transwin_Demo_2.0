from datetime import datetime
from decimal import Decimal

import pytest

from common.models.trading import ActivePosition, ActivePositions
from data_analysis.services.metrics import position_metrics as pm


def _positions():
    base = dict(open_price=Decimal("10"), open_time=datetime(2024, 1, 1), unrealized_pnl=Decimal("0"))
    return ActivePositions(
        market_id=1, account_id="acc_001", strategy_id="s1", current_time=datetime(2024, 1, 1),
        active_positions=[
            ActivePosition(symbol_code="A", position_type=1, direction=1,
                           holding_quantity=Decimal("60"), holding_amount=Decimal("600"), **base),
            ActivePosition(symbol_code="B", position_type=2, direction=2,
                           holding_quantity=Decimal("40"), holding_amount=Decimal("400"), **base),
        ],
    )


class TestPositionDistribution:

    def test_weights_sum_and_order(self):
        dist = pm.position_distribution(_positions())
        assert dist.total_amount == Decimal("1000")
        # 降序：占比大的 A 在前
        assert dist.weights[0].symbol_code == "A"
        assert dist.weights[0].weight == pytest.approx(0.6)
        assert sum(w.weight for w in dist.weights) == pytest.approx(1.0)


class TestExposure:

    def test_gross_and_net(self):
        exp = pm.exposure(_positions())
        assert exp.long_exposure == Decimal("600")
        assert exp.short_exposure == Decimal("400")
        assert exp.gross_exposure == Decimal("1000")
        assert exp.net_exposure == Decimal("200")
        assert exp.position_count == 2
