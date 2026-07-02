from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.models import ApiResponse
from data_analysis.api import frontend_controller as analysis_frontend_controller
from data_analysis.api import report_controller
from data_analysis.services.analysis_service import AnalysisService
from data_analysis.services.report.in_memory_report_store import InMemoryReportFileStore
from data_analysis.services.report.report_service import ReportService
from execution.adapters.mock_adapter import MockBrokerAdapter
from execution.api import configure_execution_dependencies, router as execution_router
from execution.services import (
    ExecutionPriceProvider,
    InMemoryExecutionRepository,
    ManualExecutionService,
    PositionService,
)
from notification.api import configure_notification_dependencies, router as notification_router
from notification.services import InMemoryNotificationRepository, NotificationService
from risk_control.api import configure_risk_dependencies, router as risk_router
from risk_control.services import InMemoryRiskRepository, RiskEventService

# ── Mock 模式组装 ───────────────────────────────────────────────────
execution_repository = InMemoryExecutionRepository()
broker_adapter = MockBrokerAdapter()
notification_service = NotificationService(repository=InMemoryNotificationRepository())
risk_service = RiskEventService(
    repository=InMemoryRiskRepository(),
    notification_sender=notification_service,
)
manual_service = ManualExecutionService(
    broker_adapter,
    repository=execution_repository,
    deal_repository=execution_repository,
    risk_handler=risk_service,
)
position_service = PositionService(broker_adapter, execution_repository)
price_provider = ExecutionPriceProvider(broker_adapter)
analysis_service = AnalysisService(
    asset_repository=execution_repository,
    trade_repository=execution_repository,
    deal_repository=execution_repository,
    operation_repository=execution_repository,
    price_provider=price_provider,
)
report_store = InMemoryReportFileStore()
report_service = ReportService(
    asset_repository=execution_repository,
    trade_repository=execution_repository,
    deal_repository=execution_repository,
    report_store=report_store,
    price_provider=price_provider,
)

configure_execution_dependencies(execution_repository, manual_service, position_service)
configure_notification_dependencies(notification_service)
configure_risk_dependencies(risk_service)

app = FastAPI(
    title="量化交易系统后端",
    version="1.0.0",
    description="支持策略生成、订单执行、风控监控、数据分析的量化交易平台",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(execution_router)
app.include_router(risk_router)
app.include_router(notification_router)
app.include_router(analysis_frontend_controller.router)
app.include_router(report_controller.router)
app.dependency_overrides[analysis_frontend_controller.get_frontend_analysis_service] = lambda: analysis_service
app.dependency_overrides[report_controller.get_report_store] = lambda: report_store
app.dependency_overrides[report_controller.get_report_service] = lambda: report_service

# ── 启动日志 ────────────────────────────────────────────────────────
from common.utils import app_logger
app_logger.log_system("INFO", "system", "量化交易系统后端启动成功（Mock 模式）")


@app.get("/api/v1/health", response_model=ApiResponse[dict])
async def health_check():
    return ApiResponse(
        data={
            "status": "running",
            "services": {
                "strategy": "ok",
                "executor": "ok",
                "risk": "ok",
                "analysis": "ok",
            },
            "lastSync": "",
            "uptime": "",
        }
    )


@app.get("/api/v1/markets", response_model=ApiResponse[list[dict]])
async def list_markets():
    return ApiResponse(
        data=[
            {"id": 1, "name": "沪深A股"},
            {"id": 2, "name": "港股"},
            {"id": 3, "name": "美股"},
        ]
    )


@app.get("/api/v1/accounts", response_model=ApiResponse[list[dict]])
async def list_accounts():
    return ApiResponse(
        data=[
            {"id": "ggt", "name": "marsi", "label": "MAIN"},
        ]
    )
