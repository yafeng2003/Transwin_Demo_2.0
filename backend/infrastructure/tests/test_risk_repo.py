"""RiskRepository dual-mode tests."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from common.models import RiskEvent, RiskNotification
from infrastructure.db.repositories.risk_repo import RiskRepository


@pytest.mark.anyio
class TestSaveRiskEvent:
    async def test_save_event(self, db, sample_risk_event: RiskEvent) -> None:
        repo = RiskRepository(db)

        event_id = await repo.save_event(sample_risk_event)

        assert event_id > 0

    @pytest.mark.mock_only
    async def test_save_event_uses_sharded_table(
        self, mock_db: MagicMock, sample_risk_event: RiskEvent
    ) -> None:
        repo = RiskRepository(mock_db)

        await repo.save_event(sample_risk_event)

        sql = mock_db.cnx.cursor.return_value.__enter__.return_value.execute.call_args[0][0]
        assert "ly_maop_risk_event" in sql
        assert "INSERT INTO" in sql

    @pytest.mark.mock_only
    async def test_save_event_rollback_on_error(
        self, mock_db: MagicMock, sample_risk_event: RiskEvent
    ) -> None:
        mock_db.cnx.cursor.return_value.__enter__.return_value.execute.side_effect = (
            RuntimeError("insert failed")
        )
        repo = RiskRepository(mock_db)

        with pytest.raises(RuntimeError):
            await repo.save_event(sample_risk_event)

        mock_db.cnx.rollback.assert_called_once()


@pytest.mark.anyio
class TestQueryRiskEvents:
    async def test_get_event(
        self, db, sample_risk_event: RiskEvent, using_real_db: bool
    ) -> None:
        repo = RiskRepository(db)

        if using_real_db:
            event_id = await repo.save_event(sample_risk_event)
        else:
            event_id = 1
            db.fetch_one.return_value = {
                "risk_event_id": event_id,
                "event_type": "api_error",
                "account_id": "ly",
                "strategy_id": "maop",
                "symbol_code": "000001",
                "event_level": 4,
                "event_message": "API connection error",
                "occur_time": datetime(2026, 6, 1, 10, 0, 0),
                "status": "pending",
            }

        row = await repo.get_event(event_id, "ly", "maop")

        assert row is not None
        assert row["eventType"] == "api_error"
        assert row["accountId"] == "ly"

    async def test_list_events(
        self, db, sample_risk_event: RiskEvent, using_real_db: bool
    ) -> None:
        repo = RiskRepository(db)

        if using_real_db:
            await repo.save_event(sample_risk_event)
        else:
            db.fetch_one.return_value = {"cnt": 1}
            db.fetch_all.return_value = [
                {
                    "risk_event_id": 1,
                    "event_type": "api_error",
                    "account_id": "ly",
                    "strategy_id": "maop",
                    "symbol_code": "000001",
                    "event_level": 4,
                    "event_message": "API connection error",
                    "occur_time": datetime(2026, 6, 1, 10, 0, 0),
                    "status": "pending",
                }
            ]

        result = await repo.list_events(
            event_type="api_error", account_id="ly", strategy_id="maop"
        )

        assert result.total == 1
        assert result.list[0]["eventType"] == "api_error"

    async def test_summarize_events(
        self, db, sample_risk_event: RiskEvent, using_real_db: bool
    ) -> None:
        repo = RiskRepository(db)

        if using_real_db:
            await repo.save_event(sample_risk_event)
        else:
            db.fetch_one.side_effect = [{"cnt": 1}, {"cnt": 1}, {"cnt": 1}]

        summary = await repo.summarize_events("ly", "maop")

        assert summary["totalEvents"] == 1
        assert summary["highRiskEvents"] == 1

    async def test_scope_required(self, db) -> None:
        repo = RiskRepository(db)

        with pytest.raises(ValueError):
            await repo.list_events()


@pytest.mark.anyio
class TestRiskNotifications:
    async def test_save_and_list_notification(
        self,
        db,
        sample_risk_event: RiskEvent,
        sample_risk_notification: RiskNotification,
        using_real_db: bool,
    ) -> None:
        repo = RiskRepository(db)

        if using_real_db:
            event_id = await repo.save_event(sample_risk_event)
            sample_risk_notification.risk_event_id = event_id
            await repo.save_notification(sample_risk_notification)
        else:
            db.fetch_one.return_value = {"cnt": 1}
            db.fetch_all.return_value = [
                {
                    "notification_id": 1,
                    "notification_type": "risk_alert",
                    "risk_level": 4,
                    "title": "Risk alert",
                    "content": "API connection error",
                    "created_at": datetime(2026, 6, 1, 10, 1, 0),
                    "is_read": 0,
                    "risk_event_id": 1,
                }
            ]

        result = await repo.list_notifications(
            notification_type="risk_alert", account_id="ly", strategy_id="maop"
        )

        assert result.total == 1
        assert result.list[0]["type"] == "risk_alert"

    @pytest.mark.mock_only
    async def test_save_notification_uses_sharded_table(
        self, mock_db: MagicMock, sample_risk_notification: RiskNotification
    ) -> None:
        repo = RiskRepository(mock_db)

        await repo.save_notification(sample_risk_notification)

        sql = mock_db.cnx.cursor.return_value.__enter__.return_value.execute.call_args[0][0]
        assert "ly_maop_notification" in sql

    async def test_notification_scope_required(self, db) -> None:
        repo = RiskRepository(db)
        notification = RiskNotification(
            notification_type="risk_alert",
            risk_level=4,
            title="Risk alert",
            content="Missing scope",
        )

        with pytest.raises(ValueError):
            await repo.save_notification(notification)
