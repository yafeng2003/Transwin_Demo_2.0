from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from common.interfaces.analysis_interface import DailyMetricsStore
from common.interfaces.asset_repository import AssetRepository
from common.interfaces.trade_repository import TradeRepository
from common.models.analytics import DailyMetric
from common.models.asset import Asset
from common.models.trade import Trade

_ZERO = Decimal("0")


def _daily_last_net_value(assets: list[Asset], equity_field: str) -> dict[date, Decimal]:
    # 同一天多条资产快照取最后一条，作为当日收盘净值。
    by_day: dict[date, tuple[datetime, Decimal]] = {}
    for a in assets:
        day = a.created_at.date()
        value = getattr(a, equity_field)
        if day not in by_day or a.created_at >= by_day[day][0]:
            by_day[day] = (a.created_at, value)
    return {day: value for day, (_, value) in by_day.items()}


def compute_daily_metrics(
    assets: list[Asset],
    trades: list[Trade],
    market_id: int,
    account_id: str,
    strategy_id: str | None,
    equity_field: str = "net_value",
) -> list[DailyMetric]:
    """按天汇总净值与交易，供看板/报表快速读取。

    净值序列为账户级，trades 为单策略；strategy_id 为 None 时表示账户级汇总。
    """
    net_value_by_day = _daily_last_net_value(assets, equity_field)
    if not net_value_by_day:
        return []

    trade_count: dict[date, int] = defaultdict(int)
    realized_by_day: dict[date, Decimal] = defaultdict(lambda: _ZERO)
    commission_by_day: dict[date, Decimal] = defaultdict(lambda: _ZERO)
    for t in trades:
        if t.close_time is None:
            continue
        day = t.close_time.date()
        trade_count[day] += 1
        realized_by_day[day] += t.realized_pnl
        commission_by_day[day] += t.commission

    days = sorted(net_value_by_day)
    base = float(net_value_by_day[days[0]])
    peak = float(net_value_by_day[days[0]])
    prev: float | None = None

    metrics: list[DailyMetric] = []
    for day in days:
        nv = float(net_value_by_day[day])
        daily_return = (nv / prev - 1.0) if prev not in (None, 0.0) else 0.0
        cumulative = (nv / base - 1.0) if base != 0.0 else 0.0
        peak = max(peak, nv)
        drawdown = (nv / peak - 1.0) if peak != 0.0 else 0.0
        metrics.append(
            DailyMetric(
                stat_date=day,
                market_id=market_id,
                account_id=account_id,
                strategy_id=strategy_id,
                net_value=net_value_by_day[day],
                daily_return=daily_return,
                cumulative_return=cumulative,
                drawdown=drawdown,
                trade_count=trade_count.get(day, 0),
                realized_pnl=realized_by_day.get(day, _ZERO),
                commission=commission_by_day.get(day, _ZERO),
            )
        )
        prev = nv
    return metrics


class DailyAggregationService:

    def __init__(
        self,
        asset_repository: AssetRepository,
        trade_repository: TradeRepository,
        store: DailyMetricsStore,
    ) -> None:
        self._asset_repo = asset_repository
        self._trade_repo = trade_repository
        self._store = store

    async def run(
        self,
        market_id: int,
        account_id: str,
        strategy_id: str,
        start_time: datetime,
        end_time: datetime,
        equity_field: str = "net_value",
    ) -> int:
        assets = await self._asset_repo.get_assets_by_range(account_id, market_id, start_time, end_time)
        trades = await self._trade_repo.get_trades_by_range(
            account_id, strategy_id, market_id, start_time, end_time
        )
        metrics = compute_daily_metrics(
            assets, trades, market_id, account_id, strategy_id, equity_field
        )
        if not metrics:
            return 0
        return await self._store.upsert_daily_metrics(metrics)
