from decimal import Decimal

from common.models.analytics import ExposureMetrics, PositionDistribution, PositionWeight
from common.models.trading import ActivePositions

_ZERO = Decimal("0")
_LONG = 1
_SHORT = 2


def position_distribution(positions: ActivePositions) -> PositionDistribution:
    total = sum((p.holding_amount for p in positions.active_positions), _ZERO)
    weights = [
        PositionWeight(
            symbol_code=p.symbol_code,
            holding_amount=p.holding_amount,
            weight=float(p.holding_amount / total) if total > _ZERO else 0.0,
        )
        for p in positions.active_positions
    ]
    # 占比从大到小排序，便于前端直接画饼图/条形图。
    weights.sort(key=lambda w: w.weight, reverse=True)
    return PositionDistribution(total_amount=total, weights=weights)


def exposure(positions: ActivePositions) -> ExposureMetrics:
    long_exposure = sum(
        (p.holding_amount for p in positions.active_positions if p.direction == _LONG), _ZERO
    )
    short_exposure = sum(
        (p.holding_amount for p in positions.active_positions if p.direction == _SHORT), _ZERO
    )
    return ExposureMetrics(
        gross_exposure=long_exposure + short_exposure,
        net_exposure=long_exposure - short_exposure,
        long_exposure=long_exposure,
        short_exposure=short_exposure,
        position_count=len(positions.active_positions),
    )
