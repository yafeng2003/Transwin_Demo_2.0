import numpy as np

from common.models.analytics import (
    DrawdownPoint,
    HistogramBin,
    ReturnDistribution,
    RiskMetrics,
)
from common.models.asset import Asset
from data_analysis.services.metrics.return_metrics import simple_returns


def _sorted_assets(assets: list[Asset]) -> list[Asset]:
    return sorted(assets, key=lambda a: a.created_at)


def drawdown_series(values: list[float]) -> np.ndarray:
    if not values:
        return np.array([], dtype=float)
    arr = np.asarray(values, dtype=float)
    running_peak = np.maximum.accumulate(arr)
    # 峰值为 0 时回撤无意义，置 0 避免除零。
    safe_peak = np.where(running_peak == 0.0, np.nan, running_peak)
    dd = arr / safe_peak - 1.0
    return np.nan_to_num(dd, nan=0.0)


def max_drawdown(values: list[float]) -> float:
    dd = drawdown_series(values)
    if dd.size == 0:
        return 0.0
    return float(-dd.min())


def max_drawdown_duration(values: list[float]) -> int:
    dd = drawdown_series(values)
    if dd.size == 0:
        return 0
    longest = 0
    current = 0
    for d in dd:
        # d < 0 表示仍处于水下，未回到前高。
        if d < 0.0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def annualized_volatility(values: list[float], periods_per_year: int) -> float:
    returns = simple_returns(values)
    if returns.size < 2:
        return 0.0
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year))


def historical_var(values: list[float], confidence: float) -> float:
    returns = simple_returns(values)
    if returns.size == 0:
        return 0.0
    quantile = np.quantile(returns, 1.0 - confidence)
    # 损失以正数表示，收益分位若为正则无下行风险。
    return float(max(0.0, -quantile))


def return_distribution(values: list[float], bins: int = 20) -> ReturnDistribution:
    returns = simple_returns(values)
    if returns.size == 0:
        return ReturnDistribution(
            bins=[], mean=0.0, std=0.0, skewness=0.0, kurtosis=0.0,
            min_return=0.0, max_return=0.0,
        )

    counts, edges = np.histogram(returns, bins=bins)
    hist = [
        HistogramBin(lower=float(edges[i]), upper=float(edges[i + 1]), count=int(counts[i]))
        for i in range(counts.size)
    ]

    mean = float(returns.mean())
    std_sample = float(returns.std(ddof=1)) if returns.size >= 2 else 0.0
    std_pop = returns.std(ddof=0)
    # 偏度/峰度用总体标准差做标准化，标准差为 0 时退化为 0。
    if std_pop > 0:
        z = (returns - mean) / std_pop
        skewness = float(np.mean(z ** 3))
        kurtosis = float(np.mean(z ** 4) - 3.0)
    else:
        skewness = 0.0
        kurtosis = 0.0

    return ReturnDistribution(
        bins=hist,
        mean=mean,
        std=std_sample,
        skewness=skewness,
        kurtosis=kurtosis,
        min_return=float(returns.min()),
        max_return=float(returns.max()),
    )


def build_drawdown_series(assets: list[Asset], equity_field: str = "net_value") -> list[DrawdownPoint]:
    ordered = _sorted_assets(assets)
    values = [float(getattr(a, equity_field)) for a in ordered]
    dd = drawdown_series(values)
    return [DrawdownPoint(time=a.created_at, drawdown=float(d)) for a, d in zip(ordered, dd)]


def analyze_risk(
    assets: list[Asset],
    periods_per_year: int,
    var_confidence: float = 0.95,
    equity_field: str = "net_value",
) -> RiskMetrics:
    values = [float(getattr(a, equity_field)) for a in _sorted_assets(assets)]
    returns = simple_returns(values)
    return RiskMetrics(
        max_drawdown=max_drawdown(values),
        max_drawdown_duration=max_drawdown_duration(values),
        annualized_volatility=annualized_volatility(values, periods_per_year),
        return_mean=float(returns.mean()) if returns.size else 0.0,
        return_std=float(returns.std(ddof=1)) if returns.size >= 2 else 0.0,
        var_95=historical_var(values, var_confidence),
    )


def downside_deviation(values: list[float], periods_per_year: int, mar: float = 0.0) -> float:
    """年化下行波动率(Sortino 下行偏差)：仅对低于最低可接受收益 MAR 的部分计均方根后年化。"""
    returns = simple_returns(values)
    if returns.size < 1:
        return 0.0
    downside = np.minimum(returns - mar, 0.0)
    rms = float(np.sqrt(np.mean(np.square(downside))))
    return rms * float(np.sqrt(periods_per_year))


def drawdown_distribution(
    values: list[float], edges: tuple[float, ...] = (0.02, 0.04, 0.06, 0.08)
) -> list[tuple[str, int]]:
    """回撤深度分布：统计各时点回撤深度落入 0~2% / 2~4% / ... / 8%+ 各档的时点数。

    深度取每个时点相对历史峰值的回撤(>=0)；新高(深度 0)的时点计入首档。
    计数口径(按天含新高日)如与前端不一致可调整 edges 或过滤逻辑。
    """
    dd = drawdown_series(values)
    if dd.size == 0:
        return []
    depths = -dd
    labels = [f"{(0 if i == 0 else edges[i-1]) * 100:.0f}~{e * 100:.0f}%" for i, e in enumerate(edges)]
    labels.append(f"{edges[-1] * 100:.0f}%+")
    counts = [0] * len(labels)
    for d in depths:
        for i, hi in enumerate(edges):
            if d <= hi:
                counts[i] += 1
                break
        else:
            counts[-1] += 1
    return list(zip(labels, counts))
