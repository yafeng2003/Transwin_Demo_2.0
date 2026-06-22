from fastapi import FastAPI

from common.interfaces.analysis_interface import ReportFileStore
from common.models import ApiResponse
from common.models.analytics import ReportFileResult, ReportMetadata
from data_analysis.api import analysis_controller, report_controller
from data_analysis.services.analysis_service import AnalysisService
from data_analysis.services.report.report_service import ReportService
from execution.adapters.mock_adapter import MockBrokerAdapter
from execution.api import configure_execution_dependencies, router as execution_router
from execution.services import InMemoryExecutionRepository, ManualExecutionService
from notification.api import configure_notification_dependencies, router as notification_router
from notification.services import InMemoryNotificationRepository, NotificationService
from risk_control.api import configure_risk_dependencies, router as risk_router
from risk_control.services import InMemoryRiskRepository, RiskEventService


class InMemoryReportStore(ReportFileStore):
    """内存版报表存储，用于 Demo/Mock 环境。"""

    def __init__(self):
        self._reports: dict[int, ReportMetadata] = {}
        self._files: dict[int, bytes] = {}

    async def save_report_file(self, report) -> ReportFileResult:
        rid = len(self._reports) + 1
        meta = ReportMetadata(
            report_id=rid,
            report_type=report.report_type,
            market_id=report.market_id,
            account_id=report.account_id,
            strategy_id=report.strategy_id,
            period_start=report.period_start,
            period_end=report.period_end,
            file_format=report.file_format,
            file_size=len(report.content),
            status="generated",
        )
        self._reports[rid] = meta
        self._files[rid] = report.content
        return ReportFileResult(report_id=rid, status="generated")

    async def list_reports(self, market_id, account_id, report_type=None,
                           strategy_id=None, start_time=None, end_time=None):
        return list(self._reports.values())

    async def get_report(self, report_id):
        return self._reports.get(report_id)

    async def load_report_bytes(self, report_id):
        return self._files.get(report_id)


execution_repository = InMemoryExecutionRepository()
notification_service = NotificationService(repository=InMemoryNotificationRepository())
risk_service = RiskEventService(
    repository=InMemoryRiskRepository(),
    notification_sender=notification_service,
)
manual_service = ManualExecutionService(
    MockBrokerAdapter(),
    repository=execution_repository,
    deal_repository=execution_repository,
    risk_handler=risk_service,
)

configure_execution_dependencies(execution_repository, manual_service)
configure_notification_dependencies(notification_service)
configure_risk_dependencies(risk_service)

# 分析层与报表层
analysis_service = AnalysisService(
    asset_repository=execution_repository,
    trade_repository=execution_repository,
    deal_repository=execution_repository,
    operation_repository=execution_repository,
)
report_store = InMemoryReportStore()
report_service = ReportService(
    asset_repository=execution_repository,
    trade_repository=execution_repository,
    deal_repository=execution_repository,
    report_store=report_store,
)

app = FastAPI(
    title="量化交易系统后端",
    version="1.0.0",
    description="支持策略生成、订单执行、风控监控、数据分析的量化交易平台",
)

app.dependency_overrides[analysis_controller.get_analysis_service] = lambda: analysis_service
app.dependency_overrides[report_controller.get_report_service] = lambda: report_service
app.dependency_overrides[report_controller.get_report_store] = lambda: report_store

app.include_router(execution_router)
app.include_router(risk_router)
app.include_router(notification_router)
app.include_router(analysis_controller.router)
app.include_router(report_controller.router)
app.include_router(analysis_controller.router)


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
            {"id": "acc_main", "name": "acc_main", "label": "MAIN"},
            {"id": "acc_growth", "name": "acc_growth", "label": "GROWTH"},
            {"id": "acc_hedge", "name": "acc_hedge", "label": "HEDGE"},
        ]
    )
