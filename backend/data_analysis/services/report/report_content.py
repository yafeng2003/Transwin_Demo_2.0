from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from common.models.analytics import (
    ReportContent,
    ReportSection,
    ReturnMetrics,
    RiskMetrics,
    StrategyComparison,
    TradeMetrics,
)
from common.models.trading import ActivePositions
from common.models.asset import Asset
from common.models.deal import Deal
from common.models.trade import Trade
from data_analysis.services.metrics import position_metrics
from data_analysis.services.sector_map import SectorMap, sector_distribution

_ZERO = Decimal("0")
_DIRECTION = {1: "多", 2: "空"}
_DEAL_TYPE = {1: "开仓", 2: "平仓"}


def _money(value: Decimal) -> str:
    return f"{value:.2f}"


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _deal_rows(deals: list[Deal]) -> list[list[str]]:
    return [
        [
            d.deal_time.strftime("%Y-%m-%d %H:%M:%S"),
            f"{d.symbol_name}({d.symbol_code})",
            _DIRECTION.get(d.direction, "-"),
            _DEAL_TYPE.get(d.deal_type, "-"),
            _money(d.deal_price),
            _money(d.deal_quantity),
            _money(d.deal_amount),
            _money(d.commission),
        ]
        for d in sorted(deals, key=lambda x: x.deal_time)
    ]


def _vwap_rows(deals: list[Deal]) -> list[list[str]]:
    amount_by_symbol: dict[str, Decimal] = defaultdict(lambda: _ZERO)
    quantity_by_symbol: dict[str, Decimal] = defaultdict(lambda: _ZERO)
    for d in deals:
        amount_by_symbol[d.symbol_code] += d.deal_amount
        quantity_by_symbol[d.symbol_code] += d.deal_quantity
    rows = []
    for symbol, quantity in quantity_by_symbol.items():
        vwap = (amount_by_symbol[symbol] / quantity) if quantity > _ZERO else _ZERO
        rows.append([symbol, _money(vwap), _money(quantity)])
    return rows


def _position_rows(positions: ActivePositions) -> list[list[str]]:
    distribution = position_metrics.position_distribution(positions)
    weight_by_symbol = {w.symbol_code: w.weight for w in distribution.weights}
    return [
        [
            p.symbol_code,
            _DIRECTION.get(p.direction, "-"),
            _money(p.holding_quantity),
            _money(p.holding_amount),
            _pct(weight_by_symbol.get(p.symbol_code, 0.0)),
        ]
        for p in positions.active_positions
    ]


def _net_value_rows(assets: list[Asset], equity_field: str = "net_value") -> list[list[str]]:
    ordered = sorted(assets, key=lambda a: a.created_at)
    if not ordered:
        return []
    base = float(getattr(ordered[0], equity_field))
    rows = []
    for a in ordered:
        nv = getattr(a, equity_field)
        cum = (float(nv) / base - 1.0) if base != 0.0 else 0.0
        rows.append([a.created_at.strftime("%Y-%m-%d"), _money(nv), _pct(cum)])
    return rows


def _summary(returns: ReturnMetrics, risk: RiskMetrics, trades: TradeMetrics) -> list[tuple[str, str]]:
    return [
        ("累计收益率", _pct(returns.cumulative_return)),
        ("年化收益率", _pct(returns.annualized_return)),
        ("夏普比率", f"{returns.sharpe_ratio:.4f}"),
        ("最大回撤", _pct(risk.max_drawdown)),
        ("年化波动率", _pct(risk.annualized_volatility)),
        ("交易笔数", str(trades.total_trades)),
        ("胜率", _pct(trades.win_rate)),
        ("总手续费", _money(trades.total_commission)),
    ]


def build_daily_report(
    market_id: int,
    account_id: str,
    strategy_id: str | None,
    period_start: datetime,
    period_end: datetime,
    deals: list[Deal],
    positions: ActivePositions,
    assets: list[Asset],
    returns: ReturnMetrics,
    risk: RiskMetrics,
    trades: TradeMetrics,
    generated_at: datetime,
) -> ReportContent:
    sections = [
        ReportSection(
            title="当日成交记录",
            headers=["时间", "标的", "方向", "开平", "成交价", "数量", "金额", "手续费"],
            rows=_deal_rows(deals),
        ),
        ReportSection(title="成交均价", headers=["标的", "成交均价", "成交数量"], rows=_vwap_rows(deals)),
        ReportSection(
            title="持仓结构与仓位占比",
            headers=["标的", "方向", "持仓数量", "成本金额", "占比"],
            rows=_position_rows(positions),
        ),
        ReportSection(title="净值曲线", headers=["日期", "净值", "累计收益"], rows=_net_value_rows(assets)),
    ]
    return ReportContent(
        report_type="daily",
        title=f"日报 {period_start.strftime('%Y-%m-%d')}",
        market_id=market_id,
        account_id=account_id,
        strategy_id=strategy_id,
        period_start=period_start,
        period_end=period_end,
        summary=_summary(returns, risk, trades),
        sections=sections,
        generated_at=generated_at,
    )


def build_weekly_report(
    market_id: int,
    account_id: str,
    strategy_id: str | None,
    period_start: datetime,
    period_end: datetime,
    trades: list[Trade],
    assets: list[Asset],
    returns: ReturnMetrics,
    risk: RiskMetrics,
    trade_metrics: TradeMetrics,
    generated_at: datetime,
) -> ReportContent:
    trades = [t for t in trades if t.close_time is not None and t.close_price is not None]
    closed_pnl = sum((t.realized_pnl for t in trades), _ZERO)
    ranking_rows = [
        [
            f"{t.symbol_name}({t.symbol_code})",
            _pct(float(t.return_rate)),
            _money(t.realized_pnl),
            t.close_time.strftime("%Y-%m-%d %H:%M"),
        ]
        for t in sorted(trades, key=lambda x: x.return_rate, reverse=True)
    ]

    summary = _summary(returns, risk, trade_metrics)
    summary.insert(0, ("本周交易次数", str(len(trades))))
    summary.insert(1, ("本周已平仓收益", _money(closed_pnl)))

    sections = [
        ReportSection(
            title="收益率排名",
            headers=["标的", "收益率", "已实现收益", "平仓时间"],
            rows=ranking_rows,
        ),
        ReportSection(title="每日资产变化", headers=["日期", "净值", "累计收益"], rows=_net_value_rows(assets)),
    ]
    return ReportContent(
        report_type="weekly",
        title=f"周报 {period_start.strftime('%Y-%m-%d')} ~ {period_end.strftime('%Y-%m-%d')}",
        market_id=market_id,
        account_id=account_id,
        strategy_id=strategy_id,
        period_start=period_start,
        period_end=period_end,
        summary=summary,
        sections=sections,
        generated_at=generated_at,
    )


def build_monthly_report(
    market_id: int,
    account_id: str,
    period_start: datetime,
    period_end: datetime,
    positions: ActivePositions,
    comparison: StrategyComparison,
    returns: ReturnMetrics,
    risk: RiskMetrics,
    trade_metrics: TradeMetrics,
    generated_at: datetime,
    sector_map: SectorMap | None = None,
) -> ReportContent:
    position_count = len(positions.active_positions)
    total_amount = sum((p.holding_amount for p in positions.active_positions), _ZERO)
    avg_market_value = (total_amount / position_count) if position_count else _ZERO

    performance_rows = [
        [
            perf.strategy_id,
            _money(perf.realized_pnl),
            str(perf.total_trades),
            _pct(perf.win_rate),
            "N/A" if perf.profit_factor is None else f"{perf.profit_factor:.2f}",
            f"{perf.trade_sharpe:.4f}",
            _money(perf.max_drawdown_amount),
        ]
        for perf in comparison.performances
    ]

    summary = _summary(returns, risk, trade_metrics)
    summary.insert(0, ("持仓平均市值", _money(avg_market_value)))

    sections = [
        ReportSection(
            title="策略绩效分析",
            headers=["策略", "已实现收益", "交易数", "胜率", "盈亏比", "交易级夏普", "金额回撤"],
            rows=performance_rows,
        ),
        _industry_section(positions, sector_map),
    ]
    return ReportContent(
        report_type="monthly",
        title=f"月报 {period_start.strftime('%Y-%m')}",
        market_id=market_id,
        account_id=account_id,
        strategy_id=None,
        period_start=period_start,
        period_end=period_end,
        summary=summary,
        sections=sections,
        generated_at=generated_at,
    )


def _industry_section(positions: ActivePositions, sector_map: SectorMap | None) -> ReportSection:
    # 未注入映射时保留显式占位；注入后按行业占比填充，并附覆盖率说明。
    if sector_map is None:
        return ReportSection(title="行业配置", headers=["行业", "占比"], rows=[["未接入行业映射", "-"]])
    dist = sector_distribution(positions, sector_map)
    rows = [[w.sector, _pct(w.weight)] for w in dist.sectors] or [["（无持仓）", "-"]]
    rows.append(["— 行业覆盖率 —", _pct(dist.coverage_ratio)])
    return ReportSection(title="行业配置", headers=["行业", "占比"], rows=rows)
