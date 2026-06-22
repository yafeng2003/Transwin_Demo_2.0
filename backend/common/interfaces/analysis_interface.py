from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal

from common.models.analytics import (
    DailyMetric,
    ReportFile,
    ReportFileResult,
    ReportMetadata,
)


class PriceProvider(ABC):
    """现价来源，由执行层实现（执行层连交易所、持有实时价）。

    数据分析层不接第三方行情，浮动盈亏的现价应来自系统内部。
    历史时点的盯市为尽力而为，无法提供时实现方返回缺失标的为空。
    """

    @abstractmethod
    async def get_prices(
        self,
        market_id: int,
        symbol_codes: list[str],
        as_of: datetime,
    ) -> dict[str, Decimal]:
        ...


class ReportFileStore(ABC):
    """报表文件存储与检索，由基础服务实现。

    save 负责落对象存储并写报表元数据表；list/get/load 供报表中心读取。
    """

    @abstractmethod
    async def save_report_file(self, report: ReportFile) -> ReportFileResult:
        ...

    @abstractmethod
    async def list_reports(
        self,
        market_id: int,
        account_id: str,
        report_type: str | None = None,
        strategy_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[ReportMetadata]:
        ...

    @abstractmethod
    async def get_report(self, report_id: int) -> ReportMetadata | None:
        ...

    @abstractmethod
    async def load_report_bytes(self, report_id: int) -> bytes | None:
        ...


class DailyMetricsStore(ABC):
    """每日预聚合指标的存取，由基础服务实现。

    看板与报表读预聚合结果，避免每次扫原始明细。
    """

    @abstractmethod
    async def upsert_daily_metrics(self, metrics: list[DailyMetric]) -> int:
        ...

    @abstractmethod
    async def query_daily_metrics(
        self,
        market_id: int,
        account_id: str,
        strategy_id: str | None,
        start_date: date,
        end_date: date,
    ) -> list[DailyMetric]:
        ...
