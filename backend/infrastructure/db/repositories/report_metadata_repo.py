"""
report_metadata 表（报表文件元数据与内容）的读写操作。

报表文件以 MEDIUMBLOB 存入 MySQL，元数据与内容同表。
file_uri 为可下载路径（指向本服务 ``GET /reports/{report_id}/download``）。

接口文档对应：
  - :class:`common.interfaces.analysis_interface.ReportFileStore`
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from common.interfaces.analysis_interface import (
    ReportFileStore as ReportFileStoreInterface,
)
from common.models.analytics import ReportFile, ReportFileResult, ReportMetadata
from infrastructure.db.repositories.base_repo import BaseRepository


class ReportFileStoreImpl(BaseRepository, ReportFileStoreInterface):
    """报表文件存储与检索实现。

    元数据与文件二进制同表存储，按 ``{account}_report`` 分表（不按 strategy 分表）。
    strategy_id 作为普通列过滤，不参与表名拼接，方便跨策略查询。
    """

    TABLE_SUFFIX = "report"

    _DOWNLOAD_URI = "/api/v1/reports/{report_id}/download"

    # ── 写入 ──────────────────────────────────────────────────────

    async def save_report_file(self, report: ReportFile) -> ReportFileResult:
        return await asyncio.to_thread(self._save_report_file_sync, report)

    def _save_report_file_sync(self, report: ReportFile) -> ReportFileResult:
        # 始终使用 account 级表名，strategy_id 作为列存储而非分表依据。
        table = self._table_name(report.account_id, strategy_id=None)
        file_size = len(report.content)
        sql = (
            f"INSERT INTO {table} "
            f"(report_type, market_id, account_id, strategy_id, "
            f"period_start, period_end, file_format, content, "
            f"file_size, status, generated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            report.report_type,
            report.market_id,
            report.account_id,
            report.strategy_id,
            report.period_start,
            report.period_end,
            report.file_format,
            report.content,
            file_size,
            "saved",
            report.generated_at,
        )

        try:
            with self._db.cnx.cursor() as cursor:
                cursor.execute(sql, params)
                report_id = cursor.lastrowid
            self._db.commit()
        except Exception:
            self._db.cnx.rollback()
            raise

        return ReportFileResult(
            report_id=report_id,
            file_uri=self._DOWNLOAD_URI.format(report_id=report_id),
            status="saved",
        )

    # ── 查询 ──────────────────────────────────────────────────────

    async def list_reports(
        self,
        market_id: int,
        account_id: str,
        report_type: str | None = None,
        strategy_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[ReportMetadata]:
        return await asyncio.to_thread(
            self._list_reports_sync,
            market_id,
            account_id,
            report_type,
            strategy_id,
            start_time,
            end_time,
        )

    def _list_reports_sync(
        self,
        market_id: int,
        account_id: str,
        report_type: str | None,
        strategy_id: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
    ) -> list[ReportMetadata]:
        # 使用 account 级表名，strategy_id 仅作为过滤列。
        table = self._table_name(account_id, strategy_id=None)
        conditions = ["market_id = %s", "account_id = %s"]
        params: list = [market_id, account_id]

        if report_type is not None:
            conditions.append("report_type = %s")
            params.append(report_type)

        if strategy_id is not None:
            conditions.append("strategy_id = %s")
            params.append(strategy_id)
        # strategy_id 为 None 时不加过滤条件，返回 account 下所有报表

        if start_time is not None:
            conditions.append("period_start >= %s")
            params.append(start_time)

        if end_time is not None:
            conditions.append("period_end <= %s")
            params.append(end_time)

        sql = (
            f"SELECT report_id, report_type, market_id, account_id, "
            f"strategy_id, period_start, period_end, file_format, "
            f"file_size, status, generated_at "
            f"FROM {table} "
            f"WHERE {' AND '.join(conditions)} "
            f"ORDER BY generated_at DESC"
        )

        rows = self._db.fetch_all(sql, tuple(params))
        return [self._row_to_metadata(row) for row in rows]

    async def get_report(self, report_id: int) -> ReportMetadata | None:
        return await asyncio.to_thread(self._get_report_sync, report_id)

    def _get_report_sync(self, report_id: int) -> ReportMetadata | None:
        table = self._table_name_for_id(report_id)
        if table is None:
            return None

        sql = (
            f"SELECT report_id, report_type, market_id, account_id, "
            f"strategy_id, period_start, period_end, file_format, "
            f"file_size, status, generated_at "
            f"FROM {table} WHERE report_id = %s"
        )
        row = self._db.fetch_one(sql, (report_id,))
        if row is None:
            return None
        return self._row_to_metadata(row)

    async def load_report_bytes(self, report_id: int) -> bytes | None:
        return await asyncio.to_thread(self._load_report_bytes_sync, report_id)

    def _load_report_bytes_sync(self, report_id: int) -> bytes | None:
        table = self._table_name_for_id(report_id)
        if table is None:
            return None

        sql = f"SELECT content FROM {table} WHERE report_id = %s"
        row = self._db.fetch_one(sql, (report_id,))
        if row is None:
            return None
        return row["content"]

    # ── 辅助 ──────────────────────────────────────────────────────

    def _row_to_metadata(self, row: dict) -> ReportMetadata:
        return ReportMetadata(
            report_id=row["report_id"],
            report_type=row["report_type"],
            market_id=row["market_id"],
            account_id=row["account_id"],
            strategy_id=row["strategy_id"],
            period_start=row["period_start"],
            period_end=row["period_end"],
            file_format=row["file_format"],
            file_uri=self._DOWNLOAD_URI.format(report_id=row["report_id"]),
            file_size=row["file_size"],
            status=row["status"],
            generated_at=row["generated_at"],
        )

    def _table_name_for_id(self, report_id: int) -> str | None:
        """通过 report_id 反向查找表名。

        报表按 account 分表（{account}_report），仅凭 report_id 无法确定表名。
        遍历匹配的物理表查找，适于低频的管理端查询。
        """
        tables = self._db.fetch_all(
            "SELECT TABLE_NAME FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() "
            "AND TABLE_NAME LIKE '%%$_report' ESCAPE '$'"
        )
        for t in tables:
            name = t["TABLE_NAME"]
            row = self._db.fetch_one(
                f"SELECT 1 FROM `{name}` WHERE report_id = %s LIMIT 1",
                (report_id,),
            )
            if row is not None:
                return f"`{name}`"
        return None
