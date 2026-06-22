"""模拟通知发送器。

用于测试通知调用链，可配置发送失败以验证异常路径。
"""

from common.interfaces import RiskNotificationSender
from common.models import RiskNotification


class MockNotificationSender(RiskNotificationSender):
    """RiskNotificationSender 的内存模拟实现。"""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.sent: list[RiskNotification] = []

    async def send_risk_notification(self, notification: RiskNotification) -> int:
        """记录通知；should_fail=True 时模拟发送失败。"""
        if self.should_fail:
            raise RuntimeError("mock notification failure")
        self.sent.append(notification)
        return len(self.sent)
