"""TradeRepository 测试。

- mock 模式（默认）：验证参数传递与调用逻辑。
- ``--real-db`` 模式：验证真实 SQL 执行与数据读写。
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from common.models.trade import Trade
from infrastructure.db.repositories.trade_repo import TradeRepository


@pytest.mark.anyio
class TestInsertTrade:
    """写入完整交易记录。"""

    async def test_insert(self, db, sample_trade: Trade) -> None:
        repo = TradeRepository(db)

        trade_id = await repo.insert_trade("ly", "maop", sample_trade)

        assert trade_id > 0

    @pytest.mark.mock_only
    async def test_rollback_on_failure(
        self, mock_db: MagicMock, sample_trade: Trade
    ) -> None:
        mock_db.cnx.cursor.return_value.__enter__.return_value.execute.side_effect = (
            RuntimeError("insert error")
        )
        repo = TradeRepository(mock_db)

        with pytest.raises(RuntimeError):
            await repo.insert_trade("ly", "maop", sample_trade)

        mock_db.cnx.rollback.assert_called_once()

    @pytest.mark.mock_only
    async def test_sql_contains_trade_fields(
        self, mock_db: MagicMock, sample_trade: Trade
    ) -> None:
        repo = TradeRepository(mock_db)

        await repo.insert_trade("ly", "maop", sample_trade)

        sql = mock_db.cnx.cursor.return_value.__enter__.return_value.execute.call_args[0][0]
        assert "INSERT INTO" in sql
        assert "ly_maop_trade" in sql or "`ly_maop_trade`" in sql
        assert "realized_pnl" in sql
        assert "return_rate" in sql


@pytest.mark.anyio
class TestGetTradesByRange:
    """按时间范围查询完整交易记录。"""

    async def test_returns_trades(
        self, db, sample_trade: Trade, using_real_db: bool
    ) -> None:
        start = datetime(2026, 1, 1)
        end = datetime(2026, 12, 31)
        repo = TradeRepository(db)

        if using_real_db:
            await repo.insert_trade("ly", "maop", sample_trade)
        else:
            db.fetch_all.return_value = [
                {
                    "trade_id": 1,
                    "market_id": 1,
                    "account_id": "ly",
                    "strategy_id": "maop",
                    "symbol_code": "000001",
                    "symbol_name": "Ping An Bank",
                    "asset_type": 1,
                    "direction": 1,
                    "open_time": "2026-06-01 09:30:00",
                    "close_time": "2026-06-10 14:00:00",
                    "open_price": 12.50,
                    "close_price": 13.20,
                    "open_quantity": 1000,
                    "open_amount": 12500.00,
                    "realized_pnl": 700.00,
                    "return_rate": 0.056,
                    "commission": 5.00,
                }
            ]

        trades = await repo.get_trades_by_range("ly", "maop", 1, start, end)

        assert len(trades) == 1
        assert isinstance(trades[0], Trade)
        assert trades[0].realized_pnl is not None
        assert trades[0].return_rate is not None

    async def test_empty(self, db) -> None:
        repo = TradeRepository(db)

        trades = await repo.get_trades_by_range(
            "ly", "maop", 1, datetime(2020, 1, 1), datetime(2020, 1, 2)
        )

        assert trades == []
