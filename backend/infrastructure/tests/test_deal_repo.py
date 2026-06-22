"""DealRepository 测试。

- mock 模式（默认）：验证参数传递与调用逻辑。
- ``--real-db`` 模式：验证真实 SQL 执行与数据读写。
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from common.models.deal import Deal
from infrastructure.db.repositories.deal_repo import DealRepository


@pytest.mark.anyio
class TestInsertDeal:
    """写入成交记录。"""

    async def test_insert(self, db, sample_deal: Deal) -> None:
        repo = DealRepository(db)

        deal_id = await repo.insert_deal("ly", "maop", sample_deal)

        assert deal_id > 0

    @pytest.mark.mock_only
    async def test_rollback_on_failure(
        self, mock_db: MagicMock, sample_deal: Deal
    ) -> None:
        mock_db.cnx.cursor.return_value.__enter__.return_value.execute.side_effect = (
            RuntimeError("insert error")
        )
        repo = DealRepository(mock_db)

        with pytest.raises(RuntimeError):
            await repo.insert_deal("ly", "maop", sample_deal)

        mock_db.cnx.rollback.assert_called_once()

    @pytest.mark.mock_only
    async def test_sql_contains_all_fields(
        self, mock_db: MagicMock, sample_deal: Deal
    ) -> None:
        repo = DealRepository(mock_db)

        await repo.insert_deal("ly", "maop", sample_deal)

        sql = mock_db.cnx.cursor.return_value.__enter__.return_value.execute.call_args[0][0]
        assert "INSERT INTO" in sql
        assert "ly_maop_deal" in sql or "`ly_maop_deal`" in sql
        assert "deal_price" in sql
        assert "deal_amount" in sql


@pytest.mark.anyio
class TestGetDealsBefore:
    """按时间点查询成交记录。"""

    async def test_returns_deals(
        self, db, sample_deal: Deal, using_real_db: bool
    ) -> None:
        now = datetime(2026, 6, 10, 15, 0, 0)
        repo = DealRepository(db)

        if using_real_db:
            await repo.insert_deal("ly", "maop", sample_deal)
        else:
            db.fetch_all.return_value = [
                {
                    "deal_id": 1,
                    "operation_id": 1,
                    "market_id": 1,
                    "account_id": "ly",
                    "strategy_id": "maop",
                    "symbol_code": "000001",
                    "symbol_name": "Ping An Bank",
                    "asset_type": 1,
                    "deal_type": 1,
                    "direction": 1,
                    "deal_price": 12.50,
                    "deal_quantity": 1000,
                    "deal_amount": 12500.00,
                    "commission": 2.50,
                    "position_after": 1000,
                    "is_manual": 0,
                    "deal_time": "2026-06-01 09:30:05",
                }
            ]

        deals = await repo.get_deals_before("ly", "maop", 1, now)

        assert len(deals) == 1
        assert isinstance(deals[0], Deal)


@pytest.mark.anyio
class TestGetDealsByRange:
    """按时间范围查询成交记录。"""

    async def test_returns_deals(
        self, db, sample_deal: Deal, using_real_db: bool
    ) -> None:
        start = datetime(2026, 6, 1)
        end = datetime(2026, 6, 30)
        repo = DealRepository(db)

        if using_real_db:
            await repo.insert_deal("ly", "maop", sample_deal)
        else:
            db.fetch_all.return_value = [
                {
                    "deal_id": 2,
                    "operation_id": 1,
                    "market_id": 1,
                    "account_id": "ly",
                    "strategy_id": "maop",
                    "symbol_code": "000001",
                    "symbol_name": "Ping An Bank",
                    "asset_type": 1,
                    "deal_type": 1,
                    "direction": 1,
                    "deal_price": 13.00,
                    "deal_quantity": 500,
                    "deal_amount": 6500.00,
                    "commission": 1.50,
                    "position_after": 500,
                    "is_manual": 0,
                    "deal_time": "2026-06-15 10:00:00",
                }
            ]

        deals = await repo.get_deals_by_range("ly", "maop", 1, start, end)

        assert len(deals) == 1
        assert deals[0].deal_price is not None

    async def test_empty_range(self, db) -> None:
        repo = DealRepository(db)

        deals = await repo.get_deals_by_range(
            "ly", "maop", 1, datetime(2020, 1, 1), datetime(2020, 1, 2)
        )

        assert deals == []
