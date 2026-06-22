from fastapi import FastAPI

from common.interfaces.analysis_interface import (
    DailyMetricsStore,
    PriceProvider,
    ReportFileStore,
)
from common.interfaces.asset_repository import AssetRepository
from common.interfaces.deal_repository import DealRepository
from common.interfaces.operation_repository import OperationRepository
from common.interfaces.trade_repository import TradeRepository
from data_analysis.api import analysis_controller, report_controller
from data_analysis.config import AnalysisConfig
from data_analysis.services.analysis_service import AnalysisService
from data_analysis.services.report.report_service import ReportService
from data_analysis.services.sector_map import SectorMap, default_sector_map


def build_app(
    asset_repository: AssetRepository,
    trade_repository: TradeRepository,
    deal_repository: DealRepository,
    operation_repository: OperationRepository,
    report_store: ReportFileStore,
    daily_metrics_store: DailyMetricsStore | None = None,
    price_provider: PriceProvider | None = None,
    config: AnalysisConfig | None = None,
    sector_map: SectorMap | None = None,
) -> FastAPI:
    """组装数据分析层应用。

    所有跨层依赖（数据源、报表存储、现价源、预聚合存储）由调用方注入，
    本模块只负责装配与路由挂载，符合面向接口编程与依赖注入约束。
    行业映射为分析层引用数据，未显式注入时载入随包内置的港股映射。
    """
    config = config or AnalysisConfig()
    sector_map = sector_map or default_sector_map()
    app = FastAPI(title="数据分析层", version="1.0.0")

    analysis_service = AnalysisService(
        asset_repository,
        trade_repository,
        deal_repository,
        operation_repository,
        config,
        price_provider,
        sector_map,
    )
    report_service = ReportService(
        asset_repository,
        trade_repository,
        deal_repository,
        report_store,
        config,
        price_provider,
        sector_map,
    )

    app.dependency_overrides[analysis_controller.get_analysis_service] = lambda: analysis_service
    app.dependency_overrides[report_controller.get_report_service] = lambda: report_service
    app.dependency_overrides[report_controller.get_report_store] = lambda: report_store

    app.include_router(analysis_controller.router)
    app.include_router(report_controller.router)

    # 预聚合存储仅供定时任务使用，挂在 state 上以便调度器取用。
    app.state.daily_metrics_store = daily_metrics_store

    @app.get("/health", tags=["健康检查"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
