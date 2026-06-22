"""风险事件评估器。

负责把风险事件等级转换为处理状态，并按规则生成需要发送的风险通知。
"""

from common.models import RiskEvent, RiskNotification


class RiskEvaluator:
    """纯业务规则组件，不直接依赖仓储或通知实现。"""

    def evaluate_status(self, event: RiskEvent) -> str:
        """根据风险等级决定事件初始处理状态。"""
        if event.event_level >= 5:
            return "processing"
        return "pending"

    def build_notification(self, event_id: int, event: RiskEvent) -> RiskNotification | None:
        """高于阈值的风险事件生成通知，低风险事件不通知。"""
        if event.event_level < 3:
            return None

        if event.event_level >= 5:
            notification_type = "strategy_pause"
            title = f"紧急风险 - {event.event_type}"
        elif event.event_level >= 4:
            notification_type = "circuit_breaker"
            title = f"熔断风险 - {event.event_type}"
        else:
            notification_type = "risk_alert"
            title = f"风险报警 - {event.event_type}"

        symbol = event.symbol_code or "全局"
        content = (
            f"账户: {event.account_id}\n"
            f"策略: {event.strategy_id}\n"
            f"标的: {symbol}\n"
            f"等级: {event.event_level}\n"
            f"详情: {event.event_message}\n"
            f"时间: {event.occur_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return RiskNotification(
            notification_type=notification_type,
            account_id=event.account_id,
            strategy_id=event.strategy_id,
            risk_level=event.event_level,
            title=title,
            content=content,
            risk_event_id=event_id,
        )
