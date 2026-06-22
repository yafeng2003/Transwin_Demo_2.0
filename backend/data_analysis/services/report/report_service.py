from datetime import date, datetime, time, timedelta
from decimal import Decimal

from common.interfaces.analysis_interface import (
    PriceProvider,
    ReportFileStore,
)
from common.interfaces.asset_repository import AssetRepository
from common.interfaces.deal_repository import DealRepository
from common.interfaces.trade_repository import TradeRepository
from common.models.analytics import ReportContent, ReportFile, ReportFileResult
from common.models.trading import ActivePositions
from data_analysis.config import AnalysisConfig
from data_analysis.services.metrics import (
    return_metrics,
    risk_metrics,
    strategy_metrics,
    trade_metrics,
)
from data_analysis.services.position_reconstructor import reconstruct_positions
from data_analysis.services.report import report_content, report_renderer
from data_analysis.services.sector_map import SectorMap

_ZERO = Decimal("0")


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    return datetime.combine(day, time.min), datetime.combine(day, time.max)


class ReportService:

    def __init__(
        self,
        asset_repository: AssetRepository,
        trade_repository: TradeRepository,
        deal_repository: DealRepository,
        report_store: ReportFileStore,
        config: AnalysisConfig | None = None,
        price_provider: PriceProvider | None = None,
        sector_map: SectorMap | None = None,
    ) -> None:
        self._asset_repo = asset_repository
        self._trade_repo = trade_repository
        self._deal_repo = deal_repository
        self._store = report_store
        self._config = config or AnalysisConfig()
        self._price_provider = price_provider
        self._sector_map = sector_map

    async def _assets(self, market_id: int, account_id: str, start: datetime, end: datetime):
        return await self._asset_repo.get_assets_by_range(account_id, market_id, start, end)

    async def _trades(self, market_id: int, account_id: str, strategy_id: str, start: datetime, end: datetime):
        return await self._trade_repo.get_trades_by_range(account_id, strategy_id, market_id, start, end)

    async def _deals(self, market_id: int, account_id: str, strategy_id: str, start: datetime, end: datetime):
        return await self._deal_repo.get_deals_by_range(account_id, strategy_id, market_id, start, end)

    async def _positions(
        self, market_id: int, account_id: str, strategy_id: str, as_of: datetime
    ) -> ActivePositions:
        deals = await self._deals(market_id, account_id, strategy_id, datetime.min, as_of)
        prices = None
        if self._price_provider is not None:
            symbols = sorted({d.symbol_code for d in deals})
            prices = await self._price_provider.get_prices(market_id, symbols, as_of)
        return reconstruct_positions(deals, market_id, account_id, strategy_id, as_of, prices)

    def _metrics(self, assets, trades):
        ppy = self._config.periods_per_year(assets[0].market_id) if assets else 252
        returns = return_metrics.analyze_returns(
            assets, ppy, self._config.annual_risk_free_rate, self._config.equity_field
        )
        risk = risk_metrics.analyze_risk(
            assets, ppy, self._config.var_confidence, self._config.equity_field
        )
        trades_m = trade_metrics.analyze_trades(trades)
        return returns, risk, trades_m

    async def _persist(self, content: ReportContent, file_format: str) -> ReportFileResult:
        payload = report_renderer.render(file_format, content)
        report = ReportFile(
            report_type=content.report_type,
            market_id=content.market_id,
            account_id=content.account_id,
            strategy_id=content.strategy_id,
            period_start=content.period_start,
            period_end=content.period_end,
            file_format=file_format,
            content=payload,
            generated_at=content.generated_at,
        )
        return await self._store.save_report_file(report)

    async def generate_daily_report(
        self,
        market_id: int,
        account_id: str,
        strategy_id: str,
        day: date,
        file_format: str = "pdf",
    ) -> ReportFileResult:
        start, end = _day_bounds(day)
        deals = await self._deals(market_id, account_id, strategy_id, start, end)
        trades = await self._trades(market_id, account_id, strategy_id, start, end)
        assets = await self._assets(market_id, account_id, start, end)
        positions = await self._positions(market_id, account_id, strategy_id, end)
        returns, risk, trades_m = self._metrics(assets, trades)

        content = report_content.build_daily_report(
            market_id, account_id, strategy_id, start, end,
            deals, positions, assets, returns, risk, trades_m, datetime.now(),
        )
        return await self._persist(content, file_format)

    async def generate_weekly_report(
        self,
        market_id: int,
        account_id: str,
        strategy_id: str,
        week_start: date,
        file_format: str = "pdf",
    ) -> ReportFileResult:
        start = datetime.combine(week_start, time.min)
        end = datetime.combine(week_start + timedelta(days=6), time.max)
        trades = await self._trades(market_id, account_id, strategy_id, start, end)
        assets = await self._assets(market_id, account_id, start, end)
        returns, risk, trades_m = self._metrics(assets, trades)

        content = report_content.build_weekly_report(
            market_id, account_id, strategy_id, start, end,
            trades, assets, returns, risk, trades_m, datetime.now(),
        )
        return await self._persist(content, file_format)

    async def generate_monthly_report(
        self,
        market_id: int,
        account_id: str,
        strategy_ids: list[str],
        month_start: date,
        file_format: str = "pdf",
    ) -> ReportFileResult:
        start = datetime.combine(month_start.replace(day=1), time.min)
        # 下月一号减一天得到本月最后一天，避免手算每月天数。
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = datetime.combine(next_month - timedelta(days=1), time.max)

        assets = await self._assets(market_id, account_id, start, end)
        trades_by_strategy: dict[str, list] = {}
        merged_positions = []
        all_trades = []
        for strategy_id in strategy_ids:
            strat_trades = await self._trades(market_id, account_id, strategy_id, start, end)
            trades_by_strategy[strategy_id] = strat_trades
            all_trades.extend(strat_trades)
            positions = await self._positions(market_id, account_id, strategy_id, end)
            merged_positions.extend(positions.active_positions)

        comparison = strategy_metrics.compare_strategies(trades_by_strategy)
        returns, risk, trades_m = self._metrics(assets, all_trades)
        account_positions = ActivePositions(
            market_id=market_id, account_id=account_id, strategy_id="*",
            current_time=end, active_positions=merged_positions,
        )

        content = report_content.build_monthly_report(
            market_id, account_id, start, end,
            account_positions, comparison, returns, risk, trades_m, datetime.now(),
            sector_map=self._sector_map,
        )
        return await self._persist(content, file_format)
