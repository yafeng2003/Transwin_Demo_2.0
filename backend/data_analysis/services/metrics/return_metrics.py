from decimal import Decimal

import numpy as np
import pandas as pd

from common.models.analytics import (
    EquityCurve,
    EquityPoint,
    PeriodReturn,
    PeriodReturns,
    ReturnMetrics,
)
from common.models.asset import Asset

_PANDAS_FREQ = {"daily": "D", "weekly": "W", "monthly": "ME"}


def _sorted_assets(assets: list[Asset]) -> list[Asset]:
    return sorted(assets, key=lambda a: a.created_at)


def _series(assets: list[Asset], equity_field: str) -> list[float]:
    return [float(getattr(a, equity_field)) for a in _sorted_assets(assets)]


def simple_returns(values: list[float]) -> np.ndarray:
    if len(values) < 2:
        return np.array([], dtype=float)
    arr = np.asarray(values, dtype=float)
    prev = arr[:-1]
    # 净值为 0 无法定义收益率，过滤该步以免产生 inf。
    valid = prev != 0.0
    return (arr[1:][valid] / prev[valid]) - 1.0


def build_equity_curve(assets: list[Asset], equity_field: str = "net_value") -> EquityCurve:
    ordered = _sorted_assets(assets)
    if not ordered:
        return EquityCurve(points=[])

    base = float(getattr(ordered[0], equity_field))
    points: list[EquityPoint] = []
    for a in ordered:
        nv = getattr(a, equity_field)
        cum = (float(nv) / base - 1.0) if base != 0.0 else 0.0
        points.append(EquityPoint(time=a.created_at, net_value=nv, cumulative_return=cum))
    return EquityCurve(points=points)


def cumulative_return(values: list[float]) -> float:
    if len(values) < 2 or values[0] == 0.0:
        return 0.0
    return values[-1] / values[0] - 1.0


def annualized_return(values: list[float], periods_per_year: int) -> float:
    returns = simple_returns(values)
    n = returns.size
    if n == 0 or values[0] <= 0.0:
        return 0.0
    growth = values[-1] / values[0]
    if growth <= 0.0:
        return -1.0
    return float(growth ** (periods_per_year / n) - 1.0)


def sharpe_ratio(values: list[float], periods_per_year: int, annual_risk_free_rate: float) -> float:
    returns = simple_returns(values)
    if returns.size < 2:
        return 0.0
    rf_per_period = annual_risk_free_rate / periods_per_year
    std = returns.std(ddof=1)
    if std == 0.0:
        return 0.0
    excess_mean = (returns - rf_per_period).mean()
    return float(excess_mean / std * np.sqrt(periods_per_year))


def _format_label(ts: pd.Timestamp, granularity: str) -> str:
    if granularity == "weekly":
        iso = ts.isocalendar()
        return f"{iso.year}-W{int(iso.week):02d}"
    if granularity == "monthly":
        return ts.strftime("%Y-%m")
    return ts.strftime("%Y-%m-%d")


def period_returns(
    assets: list[Asset], granularity: str, equity_field: str = "net_value"
) -> PeriodReturns:
    if granularity not in _PANDAS_FREQ:
        raise ValueError(f"不支持的粒度：{granularity}")

    ordered = _sorted_assets(assets)
    if len(ordered) < 2:
        return PeriodReturns(granularity=granularity, items=[])

    index = pd.to_datetime([a.created_at for a in ordered])
    series = pd.Series(_series(ordered, equity_field), index=index)
    # 取每个周期最后一个净值后做环比，pandas 3 需显式关闭 fill_method 以免告警。
    resampled = series.resample(_PANDAS_FREQ[granularity]).last().dropna()
    changes = resampled.pct_change(fill_method=None).dropna()

    items: list[PeriodReturn] = []
    timestamps = list(resampled.index)
    for i in range(1, len(timestamps)):
        ts = timestamps[i]
        prev_ts = timestamps[i - 1]
        if ts not in changes.index:
            continue
        items.append(
            PeriodReturn(
                period_label=_format_label(ts, granularity),
                period_start=prev_ts.to_pydatetime(),
                period_end=ts.to_pydatetime(),
                return_rate=float(changes.loc[ts]),
            )
        )
    return PeriodReturns(granularity=granularity, items=items)


def analyze_returns(
    assets: list[Asset],
    periods_per_year: int,
    annual_risk_free_rate: float = 0.0,
    equity_field: str = "net_value",
) -> ReturnMetrics:
    ordered = _sorted_assets(assets)
    values = _series(ordered, equity_field)
    returns = simple_returns(values)
    return ReturnMetrics(
        period_count=int(returns.size),
        cumulative_return=cumulative_return(values),
        annualized_return=annualized_return(values, periods_per_year),
        sharpe_ratio=sharpe_ratio(values, periods_per_year, annual_risk_free_rate),
        start_net_value=getattr(ordered[0], equity_field) if ordered else None,
        end_net_value=getattr(ordered[-1], equity_field) if ordered else None,
    )


def calmar_ratio(annualized_ret: float, max_dd: float) -> float:
    """Calmar 比率 = 年化收益 / 最大回撤(绝对值)。回撤为 0 时无定义，返回 0。"""
    if max_dd <= 0.0:
        return 0.0
    return annualized_ret / max_dd
