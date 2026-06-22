"""通知层 HTTP API。

通过 FastAPI 暴露通知列表查询接口。
"""

from fastapi import APIRouter, Query

from common.models import ApiResponse, PagedResult
from notification.services.notification_service import NotificationService

router = APIRouter(prefix="/api/v1", tags=["通知"])

notification_service = NotificationService()


def configure_notification_dependencies(service: NotificationService) -> None:
    """在 main.py 中注入通知服务，保持 API 层与具体实现解耦。"""
    global notification_service
    notification_service = service


@router.get("/notifications", response_model=ApiResponse[PagedResult[dict]])
async def list_notifications(
    account_id: str | None = Query(None),
    strategy_id: str | None = Query(None),
    type: str | None = Query(None, description="email / risk / system"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    result = await notification_service.list_notifications(
        notification_type=type,
        page=page,
        size=size,
        account_id=account_id,
        strategy_id=strategy_id,
    )
    return ApiResponse(data=result)
