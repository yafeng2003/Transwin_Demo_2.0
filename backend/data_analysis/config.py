from pydantic import BaseModel, Field

# 年化因子按市场区分：交易日数量不同会直接改变夏普与波动率口径。
_PERIODS_PER_YEAR_BY_MARKET: dict[int, int] = {
    1: 244,  # 沪深
    2: 244,  # 港股
    3: 252,  # 美股
    4: 244,  # 期货
    5: 365,  # 加密货币，全年无休
}

_DEFAULT_PERIODS_PER_YEAR = 252


class AnalysisConfig(BaseModel):

    annual_risk_free_rate: float = Field(default=0.0, description="年化无风险利率，用于夏普计算")
    equity_field: str = Field(default="net_value", description="收益曲线取值字段：net_value 或 total_asset")
    var_confidence: float = Field(default=0.95, description="VaR 置信度")

    def periods_per_year(self, market_id: int) -> int:
        return _PERIODS_PER_YEAR_BY_MARKET.get(market_id, _DEFAULT_PERIODS_PER_YEAR)
