from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field

from common.interfaces.analysis_interface import ReportFileStore
from common.models.analytics import ReportFileResult, ReportMetadata
from data_analysis.services.report.report_service import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["报表中心"])

_MEDIA_TYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
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


@router.get("", response_model=list[ReportMetadata])
async def list_reports(
    market_id: int = Query(description="市场标识"),
    account_id: str = Query(description="账户"),
    report_type: str | None = Query(default=None, description="按类型筛选"),
    strategy_id: str | None = Query(default=None, description="按策略筛选"),
    start_time: datetime | None = Query(default=None, description="生成时间下界"),
    end_time: datetime | None = Query(default=None, description="生成时间上界"),
    store: ReportFileStore = Depends(get_report_store),
) -> list[ReportMetadata]:
    return await store.list_reports(
        market_id, account_id, report_type, strategy_id, start_time, end_time
    )


@router.get("/{report_id}", response_model=ReportMetadata)
async def get_report(
    report_id: int,
    store: ReportFileStore = Depends(get_report_store),
) -> ReportMetadata:
    metadata = await store.get_report(report_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="报表不存在")
    return metadata


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    store: ReportFileStore = Depends(get_report_store),
) -> Response:
    metadata = await store.get_report(report_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="报表不存在")
    payload = await store.load_report_bytes(report_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="报表文件缺失")

    media_type = _MEDIA_TYPES.get(metadata.file_format, "application/octet-stream")
    filename = f"{metadata.report_type}_{report_id}.{metadata.file_format}"
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/generate", response_model=ReportFileResult)
async def generate_report(
    request: GenerateReportRequest,
    service: ReportService = Depends(get_report_service),
) -> ReportFileResult:
    if request.report_type == "daily":
        if request.strategy_id is None:
            raise HTTPException(status_code=422, detail="日报需指定 strategy_id")
        return await service.generate_daily_report(
            request.market_id, request.account_id, request.strategy_id,
            request.period_date, request.file_format,
        )
    if request.report_type == "weekly":
        if request.strategy_id is None:
            raise HTTPException(status_code=422, detail="周报需指定 strategy_id")
        return await service.generate_weekly_report(
            request.market_id, request.account_id, request.strategy_id,
            request.period_date, request.file_format,
        )
    if request.report_type == "monthly":
        if not request.strategy_ids:
            raise HTTPException(status_code=422, detail="月报需指定 strategy_ids")
        return await service.generate_monthly_report(
            request.market_id, request.account_id, request.strategy_ids,
            request.period_date, request.file_format,
        )
    raise HTTPException(status_code=422, detail=f"不支持的报表类型：{request.report_type}")
