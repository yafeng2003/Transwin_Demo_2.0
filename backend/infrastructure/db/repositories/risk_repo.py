from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from common.interfaces.risk_repository import RiskRepository as RiskRepositoryInterface
from common.models import PagedResult, RiskEvent, RiskNotification
from infrastructure.db.naming import SUFFIX_NOTIFICATION, SUFFIX_RISK_EVENT, table_name
from infrastructure.db.repositories.base_repo import BaseRepository


class RiskRepository(BaseRepository, RiskRepositoryInterface):
    TABLE_SUFFIX = SUFFIX_RISK_EVENT

    async def save_event(self, event: RiskEvent) -> int:
        return await asyncio.to_thread(self._save_event_sync, event)

    def _save_event_sync(self, event: RiskEvent) -> int:
        table = self._table_name(event.account_id, event.strategy_id)
        sql = (
            f"INSERT INTO {table} "
            f"(event_type, account_id, strategy_id, symbol_code, event_level, "
            f"event_message, occur_time, status) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            event.event_type,
            event.account_id,
            event.strategy_id,
            event.symbol_code,
            event.event_level,
            event.event_message,
            event.occur_time,
            event.status,
        )
        try:
            with self._db.cnx.cursor() as cursor:
                cursor.execute(sql, params)
                event_id = cursor.lastrowid
            self._db.commit()
        except Exception:
            self._db.cnx.rollback()
            raise
        return event_id

    async def get_event(
        self, event_id: int, account_id: str | None = None, strategy_id: str | None = None
    ) -> dict | None:
        account_id, strategy_id = self._require_scope(account_id, strategy_id)
        return await asyncio.to_thread(self._get_event_sync, event_id, account_id, strategy_id)

    def _get_event_sync(
        self, event_id: int, account_id: str, strategy_id: str
    ) -> dict | None:
        table = self._table_name(account_id, strategy_id)
        sql = (
            f"SELECT risk_event_id, event_type, account_id, strategy_id, "
            f"symbol_code, event_level, event_message, occur_time, status "
            f"FROM {table} WHERE risk_event_id = %s"
        )
        row = self._db.fetch_one(sql, (event_id,))
        return self._event_row(row) if row is not None else None

    async def update_event_status(
        self,
        event_id: int,
        status: str,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> bool:
        account_id, strategy_id = self._require_scope(account_id, strategy_id)
        return await asyncio.to_thread(
            self._update_event_status_sync,
            event_id,
            status,
            account_id,
            strategy_id,
        )

    def _update_event_status_sync(
        self,
        event_id: int,
        status: str,
        account_id: str,
        strategy_id: str,
    ) -> bool:
        table = self._table_name(account_id, strategy_id)
        sql = f"UPDATE {table} SET status = %s WHERE risk_event_id = %s"
        try:
            with self._db.cnx.cursor() as cursor:
                cursor.execute(sql, (status, event_id))
                updated = cursor.rowcount > 0
            self._db.commit()
        except Exception:
            self._db.cnx.rollback()
            raise
        return updated

    async def list_events(
        self,
        event_type: str | None = None,
        level: int | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> PagedResult[dict]:
        account_id, strategy_id = self._require_scope(account_id, strategy_id)
        return await asyncio.to_thread(
            self._list_events_sync,
            event_type,
            level,
            status,
            page,
            size,
            account_id,
            strategy_id,
        )

    def _list_events_sync(
        self,
        event_type: str | None,
        level: int | None,
        status: str | None,
        page: int,
        size: int,
        account_id: str,
        strategy_id: str,
    ) -> PagedResult[dict]:
        table = self._table_name(account_id, strategy_id)
        where: list[str] = []
        params: list[object] = []
        if event_type is not None:
            where.append("event_type = %s")
            params.append(event_type)
        if level is not None:
            min_level, max_level = self._storage_level_range(level)
            where.append("event_level BETWEEN %s AND %s")
            params.extend([min_level, max_level])
        if status is not None:
            where.append("status = %s")
            params.append(status)

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        count_row = self._db.fetch_one(
            f"SELECT COUNT(*) AS cnt FROM {table} {where_sql}",
            tuple(params),
        )
        offset = (page - 1) * size
        rows = self._db.fetch_all(
            f"SELECT risk_event_id, event_type, account_id, strategy_id, "
            f"symbol_code, event_level, event_message, occur_time, status "
            f"FROM {table} {where_sql} "
            f"ORDER BY occur_time DESC, risk_event_id DESC LIMIT %s OFFSET %s",
            tuple(params + [size, offset]),
        )
        return PagedResult(
            list=[self._event_row(row) for row in rows],
            total=count_row["cnt"] if count_row is not None else 0,
            page=page,
            size=size,
        )

    async def save_notification(self, notification: RiskNotification) -> int:
        return await asyncio.to_thread(self._save_notification_sync, notification)

    def _save_notification_sync(self, notification: RiskNotification) -> int:
        account_id, strategy_id = self._notification_scope(notification)
        table = table_name(account_id, SUFFIX_NOTIFICATION, strategy_id)
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
            "skipped",
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
        table = table_name(account_id, SUFFIX_NOTIFICATION, strategy_id)
        where_sql = "WHERE notification_type = %s" if notification_type is not None else ""
        params: list[object] = [notification_type] if notification_type is not None else []
        count_row = self._db.fetch_one(
            f"SELECT COUNT(*) AS cnt FROM {table} {where_sql}",
            tuple(params),
        )
        offset = (page - 1) * size
        rows = self._db.fetch_all(
            f"SELECT notification_id, notification_type, risk_level, title, content, "
            f"created_at, is_read, risk_event_id "
            f"FROM {table} {where_sql} "
            f"ORDER BY created_at DESC, notification_id DESC LIMIT %s OFFSET %s",
            tuple(params + [size, offset]),
        )
        return PagedResult(
            list=[self._notification_row(row) for row in rows],
            total=count_row["cnt"] if count_row is not None else 0,
            page=page,
            size=size,
        )

    async def summarize_events(
        self, account_id: str | None = None, strategy_id: str | None = None
    ) -> dict:
        account_id, strategy_id = self._require_scope(account_id, strategy_id)
        return await asyncio.to_thread(self._summarize_events_sync, account_id, strategy_id)

    def _summarize_events_sync(self, account_id: str, strategy_id: str) -> dict:
        table = self._table_name(account_id, strategy_id)
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59)
        week_start = today_start - timedelta(days=today_start.weekday())
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

        total = self._count(table)
        unresolved = self._count(table, "status <> %s", ("resolved",))
        high = self._count(table, "event_level >= %s", (4,))
        today = self._count(table, "occur_time >= %s AND occur_time <= %s",
                            (today_start, today_end))
        this_week = self._count(table, "occur_time >= %s AND occur_time <= %s",
                                (week_start, week_end))
        return {
            "totalEvents": total,
            "todayEvents": today,
            "weekEvents": this_week,
            "unresolvedEvents": unresolved,
            "highRiskEvents": high,
        }

    async def compute_trend(
        self, account_id: str | None = None, strategy_id: str | None = None,
        days: int = 30,
    ) -> list[dict]:
        account_id, strategy_id = self._require_scope(account_id, strategy_id)
        return await asyncio.to_thread(self._compute_trend_sync, account_id, strategy_id, days)

    def _compute_trend_sync(self, account_id: str, strategy_id: str, days: int) -> list[dict]:
        table = self._table_name(account_id, strategy_id)
        now = datetime.now()

        # 查出每天的高风险事件数(event_level>=4)和未解决事件数
        rows = self._db.fetch_all(
            f"SELECT DATE(occur_time) AS d, "
            f"event_level, status "
            f"FROM {table} "
            f"WHERE occur_time >= %s "
            f"ORDER BY occur_time ASC",
            (now - timedelta(days=days),),
        )

        # 按日期分组统计
        daily_high: dict[str, int] = {}
        daily_unresolved: dict[str, int] = {}
        for r in rows:
            day = r["d"].strftime("%Y-%m-%d") if hasattr(r["d"], "strftime") else str(r["d"])
            if r["event_level"] >= 4:
                daily_high[day] = daily_high.get(day, 0) + 1
            if r["status"] != "resolved":
                daily_unresolved[day] = daily_unresolved.get(day, 0) + 1

        # 逐日累加计算风险评分
        trend: list[dict] = []
        cum_high = 0
        cum_unresolved = 0
        for i in range(days):
            day = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            # 被覆盖到的事件计入累计
            if day in daily_high:
                cum_high += daily_high[day]
            if day in daily_unresolved:
                cum_unresolved += daily_unresolved[day]

            # 当天若有新事件才重新算分，否则延续前一天分数
            if day in daily_high or day in daily_unresolved:
                score = min(100, cum_high * 25 + cum_unresolved * 10)
            else:
                score = trend[-1]["riskScore"] if trend else 0

            trend.append({"date": day, "riskScore": score})

        return trend

    def _count(self, table: str, where_sql: str = "", params: tuple = ()) -> int:
        clause = f"WHERE {where_sql}" if where_sql else ""
        try:
            row = self._db.fetch_one(f"SELECT COUNT(*) AS cnt FROM {table} {clause}", params)
        except Exception:
            return 0
        if row is None:
            return 0
        # DictCursor 返回的 dict 键名可能因版本而异，取第一个值
        return int(list(row.values())[0]) if row else 0

    def _require_scope(
        self, account_id: str | None, strategy_id: str | None
    ) -> tuple[str, str]:
        if not account_id or not strategy_id:
            raise ValueError("account_id and strategy_id are required for sharded tables")
        return account_id, strategy_id

    def _notification_scope(self, notification: RiskNotification) -> tuple[str, str]:
        return self._require_scope(notification.account_id, notification.strategy_id)

    def _event_row(self, row: dict) -> dict:
        occur_time = row["occur_time"]
        if isinstance(occur_time, str):
            formatted_time = occur_time
        elif isinstance(occur_time, datetime):
            formatted_time = occur_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            formatted_time = str(occur_time)
        return {
            "id": row["risk_event_id"],
            "eventType": row["event_type"],
            "eventLabel": self._event_label(row["event_type"]),
            "level": self._frontend_level(row["event_level"]),
            "accountId": row["account_id"],
            "strategyId": row["strategy_id"],
            "symbolCode": row["symbol_code"],
            "message": row["event_message"],
            "status": row["status"],
            "occurTime": formatted_time,
        }

    def _notification_row(self, row: dict) -> dict:
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
            "typeLabel": self._notification_label(row["notification_type"]),
            "level": self._frontend_level(row["risk_level"]),
            "title": row["title"],
            "content": row["content"],
            "isRead": bool(row["is_read"]),
            "createdAt": formatted_time,
        }

    def _frontend_level(self, event_level: int) -> int:
        if event_level >= 4:
            return 3
        if event_level >= 2:
            return 2
        return 1

    def _storage_level_range(self, frontend_level: int) -> tuple[int, int]:
        if frontend_level == 3:
            return 4, 5
        if frontend_level == 2:
            return 2, 3
        return 1, 1

    def _event_label(self, event_type: str) -> str:
        labels = {
            "order_failed": "下单失败",
            "cancel_failed": "撤单失败",
            "modify_failed": "改单失败",
            "api_error": "API异常",
            "timeout": "超时",
            "daily_loss": "单日亏损",
            "drawdown": "最大回撤",
            "consecutive_loss": "连续亏损",
            "circuit_breaker": "熔断",
        }
        return labels.get(event_type, event_type)

    def _notification_label(self, notification_type: str) -> str:
        labels = {
            "risk_alert": "风险报警",
            "circuit_breaker": "熔断通知",
            "anomaly": "异常通知",
            "strategy_pause": "策略暂停",
            "manual_intervention": "人工干预",
        }
        return labels.get(notification_type, notification_type)
