from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ----------------------------- 收益曲线 -----------------------------

class EquityPoint(BaseModel):

    time: datetime = Field(description="时间点")
    net_value: Decimal = Field(description="净值")
    cumulative_return: float = Field(description="相对首日的累计收益率")


class EquityCurve(BaseModel):

    points: list[EquityPoint] = Field(default_factory=list, description="净值/累计收益序列")


class PeriodReturn(BaseModel):

    period_label: str = Field(description="周期标签，如 2024-01-05 / 2024-W02 / 2024-01")
    period_start: datetime = Field(description="周期起")
    period_end: datetime = Field(description="周期止")
    return_rate: float = Field(description="该周期收益率")


class PeriodReturns(BaseModel):

    granularity: str = Field(description="粒度：daily / weekly / monthly")
    items: list[PeriodReturn] = Field(default_factory=list, description="各周期收益")


# ----------------------------- 收益指标 -----------------------------

class ReturnMetrics(BaseModel):

    period_count: int = Field(description="参与计算的收益周期数")
    cumulative_return: float = Field(description="区间累计收益率")
    annualized_return: float = Field(description="年化收益率（CAGR）")
    sharpe_ratio: float = Field(description="年化夏普比率")
    start_net_value: Decimal | None = Field(default=None, description="区间起始净值")
    end_net_value: Decimal | None = Field(default=None, description="区间结束净值")


# ----------------------------- 风险指标 -----------------------------

class DrawdownPoint(BaseModel):

    time: datetime = Field(description="时间点")
    drawdown: float = Field(description="相对历史峰值的回撤，<=0")


class HistogramBin(BaseModel):

    lower: float = Field(description="区间下界")
    upper: float = Field(description="区间上界")
    count: int = Field(description="落入区间的样本数")


class ReturnDistribution(BaseModel):

    bins: list[HistogramBin] = Field(default_factory=list, description="收益直方图")
    mean: float = Field(description="均值")
    std: float = Field(description="样本标准差")
    skewness: float = Field(description="偏度")
    kurtosis: float = Field(description="超额峰度")
    min_return: float = Field(description="最小单期收益")
    max_return: float = Field(description="最大单期收益")


class RiskMetrics(BaseModel):

    max_drawdown: float = Field(description="最大回撤，正数表示回撤幅度")
    max_drawdown_duration: int = Field(description="最长水下周期数")
    annualized_volatility: float = Field(description="年化波动率")
    return_mean: float = Field(description="周期收益均值")
    return_std: float = Field(description="周期收益标准差（样本，ddof=1）")
    var_95: float = Field(description="历史模拟法 95% 风险价值，正数表示潜在损失")


# ----------------------------- 交易指标 -----------------------------

class TradeMetrics(BaseModel):

    total_trades: int = Field(description="完整交易笔数")
    winning_trades: int = Field(description="盈利笔数")
    losing_trades: int = Field(description="亏损笔数")
    win_rate: float = Field(description="胜率")
    gross_profit: Decimal = Field(description="总盈利")
    gross_loss: Decimal = Field(description="总亏损（正数）")
    profit_factor: float | None = Field(default=None, description="总盈利/总亏损，无亏损时为 None")
    payoff_ratio: float | None = Field(default=None, description="盈亏比=平均盈利/平均亏损，无法定义时为 None")
    avg_trade_pnl: Decimal = Field(description="单笔平均盈亏")
    expectancy: Decimal = Field(description="单笔期望收益")
    total_commission: Decimal = Field(description="总手续费")
    avg_holding_seconds: float = Field(description="平均持仓时长（秒）")


class TradeFrequency(BaseModel):

    total_trades: int = Field(description="交易笔数")
    span_days: float = Field(description="区间跨度（天）")
    trades_per_day: float = Field(description="日均交易笔数")
    trades_per_week: float = Field(description="周均交易笔数")
    trades_per_month: float = Field(description="月均交易笔数")


class SlippageMetrics(BaseModel):

    deal_count: int = Field(description="参与统计的成交数")
    matched_count: int = Field(description="能匹配到委托价的成交数")
    avg_slippage_bps: float = Field(description="平均滑点（基点），正数表示成交劣于委托")
    total_slippage_cost: Decimal = Field(description="滑点总成本，正数表示损失")
    avg_slippage_per_deal: Decimal = Field(description="单笔平均滑点成本")


# ----------------------------- 持仓分析 -----------------------------

class PositionWeight(BaseModel):

    symbol_code: str = Field(description="标的代码")
    holding_amount: Decimal = Field(description="持仓成本金额")
    weight: float = Field(description="占总持仓比例")


class PositionDistribution(BaseModel):

    total_amount: Decimal = Field(description="持仓总额")
    weights: list[PositionWeight] = Field(default_factory=list, description="各标的占比")


class SectorWeight(BaseModel):

    sector: str = Field(description="一级行业")
    holding_amount: Decimal = Field(description="该行业持仓成本金额")
    weight: float = Field(description="占总持仓金额比例")


class SectorDistribution(BaseModel):

    total_amount: Decimal = Field(description="持仓总额")
    coverage_ratio: float = Field(description="已匹配到行业的金额占比，越低说明映射缺口越大")
    sectors: list[SectorWeight] = Field(default_factory=list, description="各行业占比，按占比降序")
    unmatched_symbols: list[str] = Field(
        default_factory=list, description="未匹配到行业、归入未分类的标的代码"
    )


class ExposureMetrics(BaseModel):

    gross_exposure: Decimal = Field(description="总敞口（多+空）")
    net_exposure: Decimal = Field(description="净敞口（多-空）")
    long_exposure: Decimal = Field(description="多头敞口")
    short_exposure: Decimal = Field(description="空头敞口")
    position_count: int = Field(description="持仓标的数")


# ----------------------------- 策略分析 -----------------------------

class StrategyContribution(BaseModel):

    strategy_id: str = Field(description="策略标识")
    realized_pnl: Decimal = Field(description="该策略已实现收益")
    contribution: float = Field(description="收益贡献度占比")


class StrategyPerformance(BaseModel):

    strategy_id: str = Field(description="策略标识")
    realized_pnl: Decimal = Field(description="已实现收益")
    total_trades: int = Field(description="交易笔数")
    win_rate: float = Field(description="胜率")
    profit_factor: float | None = Field(default=None, description="盈亏比例（总盈利/总亏损）")
    avg_return_rate: float = Field(description="单笔平均收益率")
    return_rate_std: float = Field(description="单笔收益率标准差")
    trade_sharpe: float = Field(description="交易级夏普（均值/标准差，未年化）")
    max_drawdown_amount: Decimal = Field(description="累计已实现收益曲线的最大金额回撤")


class CorrelationMatrix(BaseModel):

    labels: list[str] = Field(description="策略标识顺序")
    matrix: list[list[float]] = Field(description="按 labels 顺序的相关系数方阵")


class StrategyComparison(BaseModel):

    performances: list[StrategyPerformance] = Field(default_factory=list, description="各策略绩效（收益/风险对比）")
    contributions: list[StrategyContribution] = Field(default_factory=list, description="各策略贡献度")
    correlation: CorrelationMatrix | None = Field(default=None, description="策略日盈亏相关性，序列不足时为 None")


# ----------------------------- 报表 -----------------------------

class ReportSection(BaseModel):

    title: str = Field(description="小节标题")
    headers: list[str] = Field(description="表头")
    rows: list[list[str]] = Field(default_factory=list, description="数据行")


class ReportContent(BaseModel):

    report_type: str = Field(description="报表类型：daily / weekly / monthly")
    title: str = Field(description="报表标题")
    market_id: int = Field(description="市场标识")
    account_id: str = Field(description="关联账户")
    strategy_id: str | None = Field(default=None, description="关联策略，账户级为 None")
    period_start: datetime = Field(description="周期起")
    period_end: datetime = Field(description="周期止")
    summary: list[tuple[str, str]] = Field(default_factory=list, description="关键指标摘要")
    sections: list[ReportSection] = Field(default_factory=list, description="明细小节")
    generated_at: datetime = Field(description="生成时间")


class ReportFile(BaseModel):

    report_type: str = Field(description="报表类型：daily / weekly / monthly")
    market_id: int = Field(description="市场标识")
    account_id: str = Field(description="关联账户")
    strategy_id: str | None = Field(default=None, description="关联策略，账户级报表为 None")
    period_start: datetime = Field(description="报表周期起")
    period_end: datetime = Field(description="报表周期止")
    file_format: str = Field(description="导出格式：pdf / xlsx / csv")
    content: bytes = Field(description="渲染后的报表字节流，由基础服务负责落盘")
    generated_at: datetime = Field(description="生成时间")


class ReportFileResult(BaseModel):

    report_id: int = Field(description="报表记录 ID")
    file_uri: str = Field(description="文件访问地址")
    status: str = Field(description="保存状态：saved / failed")


class ReportMetadata(BaseModel):

    report_id: int = Field(description="报表记录 ID")
    report_type: str = Field(description="报表类型")
    market_id: int = Field(description="市场标识")
    account_id: str = Field(description="关联账户")
    strategy_id: str | None = Field(default=None, description="关联策略")
    period_start: datetime = Field(description="周期起")
    period_end: datetime = Field(description="周期止")
    file_format: str = Field(description="导出格式")
    file_uri: str = Field(description="文件访问地址")
    file_size: int = Field(description="文件字节数")
    status: str = Field(description="状态")
    generated_at: datetime = Field(description="生成时间")


# ----------------------------- 预聚合 -----------------------------

class DailyMetric(BaseModel):

    stat_date: date = Field(description="统计日期")
    market_id: int = Field(description="市场标识")
    account_id: str = Field(description="关联账户")
    strategy_id: str | None = Field(default=None, description="关联策略，账户级为 None")
    net_value: Decimal | None = Field(default=None, description="当日净值")
    daily_return: float = Field(description="当日收益率")
    cumulative_return: float = Field(description="累计收益率")
    drawdown: float = Field(description="当日回撤，<=0")
    trade_count: int = Field(description="当日平仓交易笔数")
    realized_pnl: Decimal = Field(description="当日已实现收益")
    commission: Decimal = Field(description="当日手续费")
