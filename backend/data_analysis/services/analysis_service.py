from datetime import datetime

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
from data_analysis.services.metrics.risk_metrics import build_drawdown_series
from data_analysis.services.position_reconstructor import reconstruct_positions
from data_analysis.services.sector_map import SectorMap, sector_distribution


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
