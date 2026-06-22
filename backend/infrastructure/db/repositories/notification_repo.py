from __future__ import annotations

import asyncio
from datetime import datetime

from common.interfaces.notification_repository import (
    NotificationRepository as NotificationRepositoryInterface,
)
from common.models import PagedResult, RiskNotification
from infrastructure.db.naming import SUFFIX_NOTIFICATION
from infrastructure.db.repositories.base_repo import BaseRepository


class NotificationRepository(BaseRepository, NotificationRepositoryInterface):
    TABLE_SUFFIX = SUFFIX_NOTIFICATION

    async def save_notification(self, notification: RiskNotification, send_status: str) -> int:
        return await asyncio.to_thread(
            self._save_notification_sync, notification, send_status
        )

    def _save_notification_sync(
        self, notification: RiskNotification, send_status: str
    ) -> int:
        table = self._table_name_for_notification(notification)
        sql = (
            f"INSERT INTO {table} "
            f"(notification_type, risk_level, title, content, created_at, "
            f"is_read, risk_event_id, send_status) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            notification.notification_type,
            notification.risk_level,
            notification.title,
            notification.content,
            notification.created_at,
            int(notification.is_read),
            notification.risk_event_id,
            send_status,
        )
        try:
            with self._db.cnx.cursor() as cursor:
                cursor.execute(sql, params)
                notification_id = cursor.lastrowid
            self._db.commit()
        except Exception:
            self._db.cnx.rollback()
            raise
        return notification_id

    async def list_notifications(
        self,
        notification_type: str | None = None,
        page: int = 1,
        size: int = 20,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> PagedResult[dict]:
        account_id, strategy_id = self._require_scope(account_id, strategy_id)
        return await asyncio.to_thread(
            self._list_notifications_sync,
            notification_type,
            page,
            size,
            account_id,
            strategy_id,
        )

    def _list_notifications_sync(
        self,
        notification_type: str | None,
        page: int,
        size: int,
        account_id: str,
        strategy_id: str,
    ) -> PagedResult[dict]:
        table = self._table_name(account_id, strategy_id)
        where_sql = "WHERE notification_type = %s" if notification_type is not None else ""
        params: list[object] = [notification_type] if notification_type is not None else []
        count_row = self._db.fetch_one(
            f"SELECT COUNT(*) AS cnt FROM {table} {where_sql}",
            tuple(params),
        )
        offset = (page - 1) * size
        rows = self._db.fetch_all(
            f"SELECT notification_id, notification_type, risk_level, title, content, "
            f"created_at, is_read, send_status "
            f"FROM {table} {where_sql} "
            f"ORDER BY created_at DESC, notification_id DESC LIMIT %s OFFSET %s",
            tuple(params + [size, offset]),
        )
        return PagedResult(
            list=[self._row(row) for row in rows],
            total=count_row["cnt"] if count_row is not None else 0,
            page=page,
            size=size,
        )

    def _table_name_for_notification(self, notification: RiskNotification) -> str:
        account_id, strategy_id = self._require_scope(
            notification.account_id, notification.strategy_id
        )
        return self._table_name(account_id, strategy_id)

    def _require_scope(
        self, account_id: str | None, strategy_id: str | None
    ) -> tuple[str, str]:
        if not account_id or not strategy_id:
            raise ValueError("account_id and strategy_id are required for sharded tables")
        return account_id, strategy_id

    def _row(self, row: dict) -> dict:
        created_at = row["created_at"]
        if isinstance(created_at, str):
            formatted_time = created_at
        elif isinstance(created_at, datetime):
            formatted_time = created_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            formatted_time = str(created_at)
        return {
            "id": row["notification_id"],
            "type": row["notification_type"],
            "typeLabel": self._type_label(row["notification_type"]),
            "level": row["risk_level"],
            "title": row["title"],
            "content": row["content"],
            "isRead": bool(row["is_read"]),
            "sendStatus": row["send_status"],
            "createdAt": formatted_time,
        }

    def _type_label(self, notification_type: str) -> str:
        labels = {
            "risk_alert": "风险报警",
            "circuit_breaker": "熔断",
            "anomaly": "异常",
            "strategy_pause": "策略暂停",
            "manual_intervention": "人工干预",
            "email": "邮件",
            "system": "系统通知",
        }
        return labels.get(notification_type, notification_type)
