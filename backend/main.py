from fastapi import FastAPI

from common.models import ApiResponse
from execution.adapters.mock_adapter import MockBrokerAdapter
from execution.api import configure_execution_dependencies, router as execution_router
from execution.services import InMemoryExecutionRepository, ManualExecutionService
from notification.api import configure_notification_dependencies, router as notification_router
from notification.services import InMemoryNotificationRepository, NotificationService
from risk_control.api import configure_risk_dependencies, router as risk_router
from risk_control.services import InMemoryRiskRepository, RiskEventService


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

app = FastAPI(
    title="量化交易系统后端",
    version="1.0.0",
    description="支持策略生成、订单执行、风控监控、数据分析的量化交易平台",
)

app.include_router(execution_router)
app.include_router(risk_router)
app.include_router(notification_router)


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
