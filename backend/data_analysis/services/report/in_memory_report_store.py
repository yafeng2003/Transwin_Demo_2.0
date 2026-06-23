"""In-memory report file store for the integrated demo app."""

from datetime import datetime

from common.interfaces.analysis_interface import ReportFileStore
from common.models.analytics import ReportFile, ReportFileResult, ReportMetadata


class InMemoryReportFileStore(ReportFileStore):
    """Store report metadata and bytes in process memory."""

    def __init__(self) -> None:
        self._reports: dict[int, tuple[ReportMetadata, bytes]] = {}
        self._next_id = 1

    async def save_report_file(self, report: ReportFile) -> ReportFileResult:
        report_id = self._next_id
        self._next_id += 1
        metadata = ReportMetadata(
            report_id=report_id,
            report_type=report.report_type,
            market_id=report.market_id,
            account_id=report.account_id,
            strategy_id=report.strategy_id,
            period_start=report.period_start,
            period_end=report.period_end,
            file_format=report.file_format,
            file_uri=f"/api/v1/reports/{report_id}/export",
            file_size=len(report.content),
            status="generated",
            generated_at=report.generated_at,
        )
        self._reports[report_id] = (metadata, report.content)
        return ReportFileResult(report_id=report_id, file_uri=metadata.file_uri, status="saved")

    async def list_reports(
        self,
        market_id: int,
        account_id: str,
        report_type: str | None = None,
        strategy_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[ReportMetadata]:
        reports = [
            metadata
            for metadata, _ in self._reports.values()
            if metadata.market_id == market_id
            and (not account_id or metadata.account_id == account_id)
            and (report_type is None or metadata.report_type == report_type)
            and (strategy_id is None or metadata.strategy_id == strategy_id)
            and (start_time is None or metadata.period_start >= start_time)
            and (end_time is None or metadata.period_end <= end_time)
        ]
        return sorted(reports, key=lambda item: item.generated_at, reverse=True)

    async def get_report(self, report_id: int) -> ReportMetadata | None:
        stored = self._reports.get(report_id)
        return stored[0] if stored else None

    async def load_report_bytes(self, report_id: int) -> bytes | None:
        stored = self._reports.get(report_id)
        return stored[1] if stored else None
