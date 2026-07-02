from datetime import datetime, timedelta

from common.interfaces.analysis_interface import PriceProvider
from common.interfaces.asset_repository import AssetRepository
from common.interfaces.deal_repository import DealRepository
from common.interfaces.operation_repository import OperationRepository
from common.interfaces.trade_repository import TradeRepository
from common.models.analytics import (
    EquityCurve,
    ExposureMetrics,
    PeriodReturns,
    PositionDistribution,
    ReturnDistribution,
    ReturnMetrics,
    RiskMetrics,
    SectorDistribution,
    SlippageMetrics,
    StrategyComparison,
    TradeFrequency,
    TradeMetrics,
)
from common.models.analytics import DrawdownPoint
from common.models.trading import ActivePositions
from data_analysis.config import AnalysisConfig
from data_analysis.services.metrics import (
    position_metrics,
    return_metrics,
    risk_metrics,
    strategy_metrics,
    trade_metrics,
)
from data_analysis.services import frontend_views
from data_analysis.services.metrics.risk_metrics import build_drawdown_series
from data_analysis.services.position_reconstructor import reconstruct_positions
from data_analysis.services.sector_map import SectorMap, sector_distribution

# 前端 period 入参到回看天数的映射。period 相对“当前时间”取窗口。
_PERIOD_DAYS = {"1m": 30, "3m": 90, "6m": 180, "1y": 365}
_DEFAULT_PERIOD = "3m"
# 跨策略/账户级查询时传给各 repository 的 strategy_id 约定值，表示“该账户全部策略”。
# 需基础服务在仓储实现中将空串(或等价)解释为不按策略过滤。
_ALL_STRATEGIES = ""


def _resolve_period(period: str | None) -> tuple[datetime, datetime]:
    """把 1m/3m/6m/1y 解析成 [start, end] 时间窗(end 取当前时间)。"""
    end = datetime.now()
    days = _PERIOD_DAYS.get(period or _DEFAULT_PERIOD, _PERIOD_DAYS[_DEFAULT_PERIOD])
    return end - timedelta(days=days), end


class AnalysisService:
    """数据分析层对外的业务编排入口。

    依赖通过构造函数注入：各 repository 提供只读数据，price_provider 由执行层提供现价，
    config 决定计算口径。本类只负责拉数据 + 调用纯计算函数，不直连数据库、不做渲染。
    """

    def __init__(
        self,
        asset_repository: AssetRepository,
        trade_repository: TradeRepository,
        deal_repository: DealRepository,
        operation_repository: OperationRepository,
        config: AnalysisConfig | None = None,
        price_provider: PriceProvider | None = None,
        sector_map: SectorMap | None = None,
    ) -> None:
        self._asset_repo = asset_repository
        self._trade_repo = trade_repository
        self._deal_repo = deal_repository
        self._operation_repo = operation_repository
        self._config = config or AnalysisConfig()
        self._price_provider = price_provider
        self._sector_map = sector_map

    def _ppy(self, market_id: int) -> int:
        return self._config.periods_per_year(market_id)

    async def _assets(self, market_id: int, account_id: str, start_time: datetime, end_time: datetime):
        return await self._asset_repo.get_assets_by_range(account_id, market_id, start_time, end_time)

    async def _trades(
        self, market_id: int, account_id: str, strategy_id: str,
        start_time: datetime, end_time: datetime,
    ):
        return await self._trade_repo.get_trades_by_range(
            account_id, strategy_id, market_id, start_time, end_time
        )

    async def _deals(
        self, market_id: int, account_id: str, strategy_id: str,
        start_time: datetime, end_time: datetime,
    ):
        return await self._deal_repo.get_deals_by_range(
            account_id, strategy_id, market_id, start_time, end_time
        )

    async def _operations(
        self, market_id: int, account_id: str, strategy_id: str,
        start_time: datetime, end_time: datetime,
    ):
        return await self._operation_repo.get_operations_by_range(
            account_id, strategy_id, market_id, start_time, end_time
        )

    # ---------------------- 收益分析 ----------------------

    async def get_return_metrics(
        self, market_id: int, account_id: str, start_time: datetime, end_time: datetime
    ) -> ReturnMetrics:
        assets = await self._assets(market_id, account_id, start_time, end_time)
        return return_metrics.analyze_returns(
            assets, self._ppy(market_id), self._config.annual_risk_free_rate, self._config.equity_field
        )

    async def get_equity_curve(
        self, market_id: int, account_id: str, start_time: datetime, end_time: datetime
    ) -> EquityCurve:
        assets = await self._assets(market_id, account_id, start_time, end_time)
        return return_metrics.build_equity_curve(assets, self._config.equity_field)

    async def get_period_returns(
        self, market_id: int, account_id: str, granularity: str,
        start_time: datetime, end_time: datetime,
    ) -> PeriodReturns:
        assets = await self._assets(market_id, account_id, start_time, end_time)
        return return_metrics.period_returns(assets, granularity, self._config.equity_field)

    # ---------------------- 风险分析 ----------------------

    async def get_risk_metrics(
        self, market_id: int, account_id: str, start_time: datetime, end_time: datetime
    ) -> RiskMetrics:
        assets = await self._assets(market_id, account_id, start_time, end_time)
        return risk_metrics.analyze_risk(
            assets, self._ppy(market_id), self._config.var_confidence, self._config.equity_field
        )

    async def get_drawdown_series(
        self, market_id: int, account_id: str, start_time: datetime, end_time: datetime
    ) -> list[DrawdownPoint]:
        assets = await self._assets(market_id, account_id, start_time, end_time)
        return build_drawdown_series(assets, self._config.equity_field)

    async def get_return_distribution(
        self, market_id: int, account_id: str, start_time: datetime, end_time: datetime, bins: int = 20
    ) -> ReturnDistribution:
        assets = await self._assets(market_id, account_id, start_time, end_time)
        values = [float(getattr(a, self._config.equity_field)) for a in sorted(assets, key=lambda x: x.created_at)]
        return risk_metrics.return_distribution(values, bins)

    # ---------------------- 交易分析 ----------------------

    async def get_trade_metrics(
        self, market_id: int, account_id: str, strategy_id: str,
        start_time: datetime, end_time: datetime,
    ) -> TradeMetrics:
        trades = await self._trades(market_id, account_id, strategy_id, start_time, end_time)
        return trade_metrics.analyze_trades(trades)

    async def get_trade_frequency(
        self, market_id: int, account_id: str, strategy_id: str,
        start_time: datetime, end_time: datetime,
    ) -> TradeFrequency:
        trades = await self._trades(market_id, account_id, strategy_id, start_time, end_time)
        return trade_metrics.compute_trade_frequency(trades)

    async def get_slippage(
        self, market_id: int, account_id: str, strategy_id: str,
        start_time: datetime, end_time: datetime,
    ) -> SlippageMetrics:
        deals = await self._deals(market_id, account_id, strategy_id, start_time, end_time)
        operations = await self._operations(market_id, account_id, strategy_id, start_time, end_time)
        return trade_metrics.compute_slippage(deals, operations)

    async def get_monthly_trade_stats(
        self, market_id: int, account_id: str, strategy_id: str,
        start_time: datetime, end_time: datetime,
    ) -> list[tuple[str, int, float]]:
        trades = await self._trades(market_id, account_id, strategy_id, start_time, end_time)
        return trade_metrics.monthly_trade_stats(trades)

    # ---------------------- 持仓分析 ----------------------

    async def get_positions(
        self, market_id: int, account_id: str, strategy_id: str, query_time: datetime
    ) -> ActivePositions:
        # 持仓非存储字段，拉全量成交后重放至 query_time，有现价源则盯市。
        deals = await self._deals(market_id, account_id, strategy_id, datetime.min, query_time)
        prices = None
        if self._price_provider is not None:
            symbols = sorted({d.symbol_code for d in deals})
            prices = await self._price_provider.get_prices(market_id, symbols, query_time)
        return reconstruct_positions(deals, market_id, account_id, strategy_id, query_time, prices)

    async def get_position_distribution(
        self, market_id: int, account_id: str, strategy_id: str, query_time: datetime
    ) -> PositionDistribution:
        positions = await self.get_positions(market_id, account_id, strategy_id, query_time)
        return position_metrics.position_distribution(positions)

    async def get_exposure(
        self, market_id: int, account_id: str, strategy_id: str, query_time: datetime
    ) -> ExposureMetrics:
        positions = await self.get_positions(market_id, account_id, strategy_id, query_time)
        return position_metrics.exposure(positions)

    async def get_sector_distribution(
        self, market_id: int, account_id: str, strategy_id: str, query_time: datetime
    ) -> SectorDistribution:
        # 行业映射为分析层引用数据（注入）；持仓重建后按标的归一化查表汇总。
        positions = await self.get_positions(market_id, account_id, strategy_id, query_time)
        return sector_distribution(positions, self._sector_map)

    # ---------------------- 策略分析 ----------------------

    async def compare_strategies(
        self, market_id: int, account_id: str, strategy_ids: list[str],
        start_time: datetime, end_time: datetime,
    ) -> StrategyComparison:
        trades_by_strategy = {}
        for strategy_id in strategy_ids:
            trades_by_strategy[strategy_id] = await self._trades(
                market_id, account_id, strategy_id, start_time, end_time
            )
        return strategy_metrics.compare_strategies(trades_by_strategy)

    # ---------------------- 前端组合接口 ----------------------

    async def returns_analysis(self, market_id: int, account_id: str, period: str | None) -> dict:
        """收益分析(GET /analysis/returns)：summary + 每日收益序列。"""
        start, end = _resolve_period(period)
        assets = await self._assets(market_id, account_id, start, end)
        trades = await self._trades(market_id, account_id, _ALL_STRATEGIES, start, end)
        return frontend_views.build_returns_view(
            assets, trades, self._ppy(market_id),
            self._config.annual_risk_free_rate, self._config.equity_field,
        )

    async def risk_analysis(self, market_id: int, account_id: str, period: str | None) -> dict:
        """风险分析(GET /analysis/risk)：波动率/下行波动率/回撤分布/风险敞口。"""
        start, end = _resolve_period(period)
        assets = await self._assets(market_id, account_id, start, end)
        exposure = await self._risk_exposure(market_id, account_id, end)
        return frontend_views.build_risk_view(
            assets, exposure, self._ppy(market_id),
            self._config.var_confidence, self._config.equity_field,
        )

    async def trading_analysis(
        self, market_id: int, account_id: str, strategy_id: str | None, period: str | None
    ) -> dict:
        """交易分析(GET /analysis/trading)。strategy_id 为空表示该账户全部策略。"""
        start, end = _resolve_period(period)
        sid = strategy_id or _ALL_STRATEGIES
        trades = await self._trades(market_id, account_id, sid, start, end)
        deals = await self._deals(market_id, account_id, sid, start, end)
        operations = await self._operations(market_id, account_id, sid, start, end)
        return frontend_views.build_trading_view(trades, deals, operations)

    async def strategy_analysis(self, market_id: int, account_id: str) -> list[dict]:
        """策略对比(GET /analysis/strategy)。前端不传周期，取该账户全部可得交易。"""
        trades = await self._trades(
            market_id, account_id, _ALL_STRATEGIES, datetime.min, datetime.now()
        )
        trades_by_strategy: dict[str, list] = {}
        for t in trades:
            trades_by_strategy.setdefault(t.strategy_id, []).append(t)
        return frontend_views.build_strategy_view(trades_by_strategy)

    async def _risk_exposure(self, market_id: int, account_id: str, as_of: datetime) -> dict:
        """风险敞口：板块 × 策略 的持仓占比热力图。

        按账户全部成交分策略重建持仓，映射板块后按持仓金额占比构矩阵。
        ⚠ heatmapData 的 value 当前取“占账户总持仓金额的百分比”，语义需与前端确认。
        """
        deals = await self._deals(market_id, account_id, _ALL_STRATEGIES, datetime.min, as_of)
        deals_by_strategy: dict[str, list] = {}
        for d in deals:
            deals_by_strategy.setdefault(d.strategy_id, []).append(d)

        cell: dict[tuple[str, str], float] = {}
        for sid, strategy_deals in deals_by_strategy.items():
            positions = reconstruct_positions(
                strategy_deals, market_id, account_id, sid, as_of, None
            )
            for p in positions.active_positions:
                sector = self._sector_map.lookup(market_id, p.symbol_code) or "未分类"
                cell[(sector, sid)] = cell.get((sector, sid), 0.0) + float(p.holding_amount)

        sectors = sorted({sector for sector, _ in cell})
        strategies = sorted(deals_by_strategy)
        total = sum(cell.values()) or 1.0
        heatmap: list[list[float]] = []
        for si, sector in enumerate(sectors):
            for ti, strategy in enumerate(strategies):
                amount = cell.get((sector, strategy), 0.0)
                if amount > 0:
                    heatmap.append([si, ti, round(amount / total * 100, 2)])
        return {"sectors": sectors, "strategies": strategies, "heatmapData": heatmap}
