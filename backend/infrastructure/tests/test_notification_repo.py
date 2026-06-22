"""NotificationRepository dual-mode tests."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from common.models import RiskNotification
from infrastructure.db.repositories.notification_repo import NotificationRepository


@pytest.mark.anyio
class TestSaveNotification:
    async def test_save_notification(
        self, db, sample_risk_notification: RiskNotification
    ) -> None:
        repo = NotificationRepository(db)

        notification_id = await repo.save_notification(
            sample_risk_notification, send_status="success"
        )

        assert notification_id > 0

    @pytest.mark.mock_only
    async def test_uses_sharded_table(
        self, mock_db: MagicMock, sample_risk_notification: RiskNotification
    ) -> None:
        repo = NotificationRepository(mock_db)

        await repo.save_notification(sample_risk_notification, send_status="success")

        sql = mock_db.cnx.cursor.return_value.__enter__.return_value.execute.call_args[0][0]
        assert "ly_maop_notification" in sql
        assert "INSERT INTO" in sql

    @pytest.mark.mock_only
    async def test_rollback_on_failure(
        self, mock_db: MagicMock, sample_risk_notification: RiskNotification
    ) -> None:
        mock_db.cnx.cursor.return_value.__enter__.return_value.execute.side_effect = (
            RuntimeError("insert failed")
        )
        repo = NotificationRepository(mock_db)

        with pytest.raises(RuntimeError):
            await repo.save_notification(sample_risk_notification, send_status="failed")

        mock_db.cnx.rollback.assert_called_once()

    async def test_scope_required(self, db) -> None:
        repo = NotificationRepository(db)
        notification = RiskNotification(
            notification_type="risk_alert",
            risk_level=4,
            title="Risk alert",
            content="Missing scope",
        )

        with pytest.raises(ValueError):
            await repo.save_notification(notification, send_status="skipped")


@pytest.mark.anyio
class TestListNotifications:
    async def test_list_notifications(
        self,
        db,
        sample_risk_notification: RiskNotification,
        using_real_db: bool,
    ) -> None:
        repo = NotificationRepository(db)

        if using_real_db:
            await repo.save_notification(sample_risk_notification, send_status="success")
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
                    "send_status": "success",
                }
            ]

        result = await repo.list_notifications(
            notification_type="risk_alert",
            account_id="ly",
            strategy_id="maop",
        )

        assert result.total == 1
        assert result.list[0]["type"] == "risk_alert"
        assert result.list[0]["sendStatus"] == "success"

    async def test_list_scope_required(self, db) -> None:
        repo = NotificationRepository(db)

        with pytest.raises(ValueError):
            await repo.list_notifications()
