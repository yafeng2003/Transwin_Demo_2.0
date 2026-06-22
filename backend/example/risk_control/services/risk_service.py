
from datetime import datetime

from common.interfaces.risk_interface import RiskEventHandler
from common.models.risk_event import RiskEvent, RiskEventResponse, RiskNotification


class RiskEventServiceImpl(RiskEventHandler):

    _ALERT_THRESHOLD = 3
    _BREAKER_THRESHOLD = 4
    _ESCALATION_THRESHOLD = 5

    def __init__(
        self,
        db_session=None,
        notification_service=None,
    ):
        self._db = db_session
        self._notifier = notification_service

    async def handle_risk_event(self, event: RiskEvent) -> RiskEventResponse:
        risk_event_id = await self._save_event(event)

        status = self._evaluate_risk_level(event)

        if event.event_level >= self._ALERT_THRESHOLD:
            await self._dispatch_notification(event)

        return RiskEventResponse(risk_event_id=risk_event_id, status=status)

    async def _save_event(self, event: RiskEvent) -> int:
        if self._db is None:
            return id(event) & 0xFFFF_FFFF

        try:
            async with self._db.begin() as tx:
                result = await tx.execute(
                    "INSERT INTO risk_event (..."
                    "event_type, account_id, strategy_id, symbol_code, "
                    "event_level, event_message, occur_time"
                    ") VALUES (...) RETURNING id"
                )
                row = result.fetchone()
                return row["id"]
        except Exception:
            return id(event) & 0xFFFF_FFFF

    def _evaluate_risk_level(self, event: RiskEvent) -> str:
        if event.event_level >= self._ESCALATION_THRESHOLD:
            return "escalated"
        if event.event_level >= self._BREAKER_THRESHOLD:
            return "received"
        return "received"

    async def _dispatch_notification(self, event: RiskEvent) -> None:
        if self._notifier is None:
            return

        if event.event_level >= self._BREAKER_THRESHOLD:
            ntype = "circuit_breaker"
        elif event.event_level >= self._ALERT_THRESHOLD:
            ntype = "alert"
        else:
            return

        notification = RiskNotification(
            notification_type=ntype,
            risk_level=event.event_level,
            title=f"[风控] {event.event_type} — {event.account_id}",
            content=self._build_notification_content(event),
            created_at=datetime.now(),
        )
        await self._notifier.send_risk_notification(notification)

    def _build_notification_content(self, event: RiskEvent) -> str:
        symbol = event.symbol_code or "全局"
        return (
            f"账户: {event.account_id}\n"
            f"策略: {event.strategy_id}\n"
            f"标的: {symbol}\n"
            f"事件: {event.event_type}\n"
            f"详情: {event.event_message}\n"
            f"时间: {event.occur_time.isoformat()}"
        )
