"""风控事件服务。

负责接收执行层推送的风险事件，调用评估器更新状态，并按需保存/发送通知。
"""

from common.interfaces import RiskEventHandler, RiskNotificationSender, RiskRepository
from common.models import PagedResult, RiskEvent, RiskEventResponse
from risk_control.services.risk_evaluator import RiskEvaluator
from risk_control.services.risk_repository import InMemoryRiskRepository


class RiskEventService(RiskEventHandler):
    """风控层业务编排入口，依赖抽象仓储和通知发送接口。"""

    def __init__(
        self,
        repository: RiskRepository | None = None,
        evaluator: RiskEvaluator | None = None,
        notification_sender: RiskNotificationSender | None = None,
    ):
        self._repository = repository or InMemoryRiskRepository()
        self._evaluator = evaluator or RiskEvaluator()
        self._notification_sender = notification_sender

    async def handle_risk_event(self, event: RiskEvent) -> RiskEventResponse:
        """处理单个风险事件，并在需要时触发通知。"""
        event.status = self._evaluator.evaluate_status(event)
        event_id = await self._repository.save_event(event)

        notification = self._evaluator.build_notification(event_id, event)
        if notification is not None:
            await self._repository.save_notification(notification)
            if self._notification_sender is not None:
                await self._notification_sender.send_risk_notification(notification)

        return RiskEventResponse(risk_event_id=event_id, status=event.status)

    async def list_events(
        self,
        event_type: str | None = None,
        level: int | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
        market_id: int | None = None,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> PagedResult[dict]:
        """分页查询风险事件列表。"""
        return await self._repository.list_events(
            event_type=event_type,
            level=level,
            status=status,
            page=page,
            size=size,
            market_id=market_id,
            account_id=account_id,
            strategy_id=strategy_id,
        )

    async def get_event(
        self, event_id: int, account_id: str | None = None, strategy_id: str | None = None
    ) -> dict | None:
        """查询单条风险事件。"""
        return await self._repository.get_event(event_id, account_id, strategy_id)

    async def resolve_event(
        self,
        event_id: int,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> dict | None:
        """将风险事件标记为已处理，并返回更新后的事件。"""
        updated = await self._repository.update_event_status(
            event_id,
            "resolved",
            account_id,
            strategy_id,
        )
        if not updated:
            return None
        return await self._repository.get_event(event_id, account_id, strategy_id)

    async def list_notifications(
        self,
        notification_type: str | None = None,
        page: int = 1,
        size: int = 20,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> PagedResult[dict]:
        """分页查询风险通知列表。"""
        return await self._repository.list_notifications(
            notification_type=notification_type,
            page=page,
            size=size,
            account_id=account_id,
            strategy_id=strategy_id,
        )

    async def get_overview(
        self, account_id: str | None = None, strategy_id: str | None = None,
        trend_days: int = 30,
    ) -> dict:
        """计算风控概览指标，供看板 API 使用。"""
        summary = await self._repository.summarize_events(account_id, strategy_id)
        risk_score = min(100, summary["highRiskEvents"] * 25 + summary["unresolvedEvents"] * 10)
        risk_level = 3 if risk_score >= 70 else 2 if risk_score >= 35 else 1
        trend = await self._repository.compute_trend(account_id, strategy_id, trend_days)
        return {
            "riskLevel": risk_level,
            "riskScore": risk_score,
            "todayEvents": summary["todayEvents"],
            "unresolvedEvents": summary["unresolvedEvents"],
            "weekEvents": summary["weekEvents"],
            "maxDrawdown": 0,
            "dailyVar": 0,
            "trend": trend,
        }

    async def get_account_metrics(self) -> dict:
        """返回账户风险指标占位数据，后续可接入真实资产/成交统计。"""
        return {
            "dailyLoss": {"current": 0, "threshold": 500000, "breached": False},
            "maxDrawdown": {"current": 0, "threshold": 20.0, "breached": False},
            "consecutiveLosses": {"current": 0, "threshold": 5, "breached": False},
            "thresholds": [
                {
                    "name": "单日亏损超限",
                    "threshold": "¥500,000",
                    "action": "暂停交易+通知",
                    "breached": False,
                    "description": "当日亏损超过阈值时触发",
                },
                {
                    "name": "最大回撤超限",
                    "threshold": "20%",
                    "action": "熔断+通知",
                    "breached": False,
                    "description": "账户最大回撤超过阈值时触发",
                },
                {
                    "name": "连续亏损次数",
                    "threshold": "5次",
                    "action": "暂停策略+通知",
                    "breached": False,
                    "description": "连续亏损次数超过阈值时触发",
                },
            ],
        }
