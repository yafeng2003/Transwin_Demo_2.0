from datetime import datetime

import pytest

from common.models.analytics import ReportContent, ReportSection
from data_analysis.services.report import report_renderer as rr


def _content() -> ReportContent:
    return ReportContent(
        report_type="daily",
        title="日报 2024-01-01",
        market_id=1,
        account_id="acc_001",
        strategy_id="s1",
        period_start=datetime(2024, 1, 1),
        period_end=datetime(2024, 1, 1, 23, 59),
        summary=[("累计收益率", "21.00%"), ("夏普比率", "1.2000")],
        sections=[
            ReportSection(title="当日成交记录", headers=["时间", "标的"], rows=[["09:30", "测试标的"]]),
            ReportSection(title="空小节", headers=["列一", "列二"], rows=[]),
        ],
        generated_at=datetime(2024, 1, 2),
    )


class TestRenderers:

    def test_csv_has_bom_and_chinese(self):
        data = rr.render("csv", _content())
        assert data.startswith(b"\xef\xbb\xbf")
        assert "累计收益率".encode("utf-8") in data

    def test_xlsx_is_zip(self):
        data = rr.render("xlsx", _content())
        assert data[:2] == b"PK"

    def test_pdf_has_magic_header(self):
        data = rr.render("pdf", _content())
        assert data[:4] == b"%PDF"
        assert len(data) > 1000

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError):
            rr.render("doc", _content())
