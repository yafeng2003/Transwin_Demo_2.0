"""报表中心 HTTP API。

按前端《前端所需后端接口文档》提供报表列表与导出；返回用 ApiResponse 包裹，
列表项为 camelCase。另保留 get / generate 供查询与生成(同样用 ApiResponse 包裹)。
依赖在 main.py 通过 dependency_overrides 注入。
"""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field

from common.interfaces.analysis_interface import ReportFileStore
from common.models import ApiResponse
from common.models.analytics import ReportFileResult, ReportMetadata
from data_analysis.services.report.report_service import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["报表中心"])

_MEDIA_TYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
}
# 前端导出格式 -> 内部存储格式。前端用 excel，内部为 xlsx。
_FORMAT_ALIAS = {"pdf": "pdf", "csv": "csv", "excel": "xlsx", "xlsx": "xlsx"}
_TYPE_LABELS = {"daily": "日报", "weekly": "周报", "monthly": "月报"}


def _format_size(num_bytes: int) -> str:
    """字节数转友好字符串，如 245KB / 1.5MB。"""
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / 1024 / 1024:.1f}MB"
    if num_bytes >= 1024:
        return f"{round(num_bytes / 1024)}KB"
    return f"{num_bytes}B"


def _to_list_item(meta: ReportMetadata) -> dict:
    """ReportMetadata -> 前端报表列表项(camelCase)。"""
    created = meta.generated_at or meta.period_end
    label = _TYPE_LABELS.get(meta.report_type, meta.report_type)
    return {
        "id": meta.report_id,
        "title": f"{label} - {meta.period_end.strftime('%Y-%m-%d')}",
        "type": meta.report_type,
        "createdAt": created.strftime("%Y-%m-%d %H:%M:%S"),
        "fileSize": _format_size(meta.file_size),
        "status": meta.status,
    }


class GenerateReportRequest(BaseModel):

    report_type: str = Field(description="daily / weekly / monthly")
    market_id: int = Field(description="市场标识")
    account_id: str = Field(description="账户")
    strategy_id: str | None = Field(default=None, description="日报/周报所属策略")
    strategy_ids: list[str] = Field(default_factory=list, description="月报参与对比的策略列表")
    period_date: date = Field(description="日报取当天/周报取周一/月报取当月任意一天")
    file_format: str = Field(default="pdf", description="导出格式：pdf / xlsx / csv")


def get_report_service() -> ReportService:
    raise RuntimeError("ReportService 未注入")


def get_report_store() -> ReportFileStore:
    raise RuntimeError("ReportFileStore 未注入")


@router.get("", response_model=ApiResponse[list[dict]])
async def list_reports(
    report_type: str = Query(alias="type", description="报表类型：daily/weekly/monthly"),
    report_date: date | None = Query(default=None, alias="date", description="日期，如 2026-06-01"),
    market_id: int = Query(1, description="市场ID，选填"),
    account_id: str = Query("", description="账户ID，选填"),
    store: ReportFileStore = Depends(get_report_store),
) -> ApiResponse[list[dict]]:
    start_time: datetime | None = None
    end_time: datetime | None = None
    if report_date is not None:
        start_time = datetime(report_date.year, report_date.month, report_date.day)
        end_time = start_time + timedelta(days=1)
    reports = await store.list_reports(
        market_id, account_id, report_type, None, start_time, end_time
    )
    return ApiResponse(data=[_to_list_item(meta) for meta in reports])


@router.get("/{report_id}/export")
async def export_report(
    report_id: int,
    export_format: str = Query("pdf", alias="format", description="导出格式：pdf/excel/csv"),
    store: ReportFileStore = Depends(get_report_store),
) -> Response:
    metadata = await store.get_report(report_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="报表不存在")
    payload = await store.load_report_bytes(report_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="报表文件缺失")
    # 当前按报表已生成的格式返回文件；请求格式与已生成格式不一致时以已生成为准
    # (按需重渲染为后续增强，待与前端确认)。excel->xlsx 仅用于匹配/命名。
    _ = _FORMAT_ALIAS.get(export_format.lower(), metadata.file_format)
    stored = metadata.file_format
    media_type = _MEDIA_TYPES.get(stored, "application/octet-stream")
    filename = f"{metadata.report_type}_{report_id}.{stored}"
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{report_id}", response_model=ApiResponse[ReportMetadata])
async def get_report(
    report_id: int,
    store: ReportFileStore = Depends(get_report_store),
) -> ApiResponse[ReportMetadata]:
    metadata = await store.get_report(report_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="报表不存在")
    return ApiResponse(data=metadata)


@router.post("/generate", response_model=ApiResponse[ReportFileResult])
async def generate_report(
    request: GenerateReportRequest,
    service: ReportService = Depends(get_report_service),
) -> ApiResponse[ReportFileResult]:
    if request.report_type == "daily":
        if request.strategy_id is None:
            raise HTTPException(status_code=422, detail="日报需指定 strategy_id")
        result = await service.generate_daily_report(
            request.market_id, request.account_id, request.strategy_id,
            request.period_date, request.file_format,
        )
    elif request.report_type == "weekly":
        if request.strategy_id is None:
            raise HTTPException(status_code=422, detail="周报需指定 strategy_id")
        result = await service.generate_weekly_report(
            request.market_id, request.account_id, request.strategy_id,
            request.period_date, request.file_format,
        )
    elif request.report_type == "monthly":
        if not request.strategy_ids:
            raise HTTPException(status_code=422, detail="月报需指定 strategy_ids")
        result = await service.generate_monthly_report(
            request.market_id, request.account_id, request.strategy_ids,
            request.period_date, request.file_format,
        )
    else:
        raise HTTPException(status_code=422, detail=f"不支持的报表类型：{request.report_type}")
    return ApiResponse(data=result)
