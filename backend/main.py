from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from common.models import ApiResponse
import common.utils
from data_analysis.api import frontend_controller as analysis_frontend_controller
from data_analysis.api import report_controller
from data_analysis.services.analysis_service import AnalysisService
from data_analysis.services.report.report_service import ReportService
from infrastructure.db.repositories.report_metadata_repo import ReportFileStoreImpl
from execution.adapters.mock_adapter import MockBrokerAdapter
from execution.api import configure_execution_dependencies, router as execution_router
from execution.services import (
    ExecutionPriceProvider,
    ManualExecutionService,
    PositionService,
)
from infrastructure.db.connection import Database, DatabaseConfig
from infrastructure.db.repositories.execution_db_repository import ExecutionDbRepository
from infrastructure.db.repositories.log_repo import DbLogger
from infrastructure.db.repositories.notification_repo import NotificationRepository
from infrastructure.db.repositories.risk_repo import RiskRepository
from notification.api import configure_notification_dependencies, router as notification_router
from notification.services import NotificationService
from risk_control.api import configure_risk_dependencies, router as risk_router
from risk_control.services import RiskEventService

# ── 数据库模式组装 ───────────────────────────────────────────────────
db_config = DatabaseConfig(
    host="192.16.1.112",
    port=3306,
    user="root",
    password="",
    database="strategy_system",
)
db = Database(db_config)
db.connect()

execution_repository = ExecutionDbRepository(db)
broker_adapter = MockBrokerAdapter()
notification_repository = NotificationRepository(db)
risk_repository = RiskRepository(db)

notification_service = NotificationService(repository=notification_repository)
risk_service = RiskEventService(
    repository=risk_repository,
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
report_store = ReportFileStoreImpl(db)
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

# 替换全局日志为数据库日志
db_logger = DbLogger(db)
common.utils.set_app_logger(db_logger)

# ── 启动日志 ────────────────────────────────────────────────────────
common.utils.app_logger.log_system("INFO", "system", "量化交易系统后端启动成功（MySQL 模式）")


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


# 各市场下的账户及策略配置
_MARKET_ACCOUNTS: dict[int, list[dict]] = {
    1: [  # A股
        {"id": "ag1", "strategies": ["alpha", "beta"], "label": "A股账户1"},
        {"id": "ag2", "strategies": ["gamma", "delta"], "label": "A股账户2"},
    ],
    2: [  # 港股
        {"id": "ggt", "strategies": ["marsi", "value"], "label": "MAIN"},
        {"id": "test", "strategies": ["demo", "trend"], "label": "TEST"},
    ],
    3: [  # 美股
        {"id": "us1", "strategies": ["growth", "value"], "label": "美股账户1"},
        {"id": "us2", "strategies": ["tech", "index"], "label": "美股账户2"},
    ],
}


@app.get("/api/v1/markets", response_model=ApiResponse[list[dict]])
async def list_markets():
    market_names = {1: "沪深A股", 2: "港股", 3: "美股"}
    return ApiResponse(
        data=[{"id": mid, "name": market_names[mid]} for mid in _MARKET_ACCOUNTS]
    )


@app.get("/api/v1/accounts", response_model=ApiResponse[list[dict]])
async def list_accounts(market_id: int = Query(None)):
    result = []
    for mid, accs in _MARKET_ACCOUNTS.items():
        # 不传 market_id 时，只返回第一个市场（港股）的账户，避免全局污染
        if market_id is not None:
            if market_id != mid:
                continue
        elif mid != 2:  # 默认只显示港股
            continue
        for a in accs:
            result.append({**a, "market_id": mid})
    return ApiResponse(data=result)
