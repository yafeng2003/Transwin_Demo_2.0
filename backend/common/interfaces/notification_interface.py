"""通知发送抽象接口。

风控层只依赖该接口发送通知，具体发送方式可由邮件、mock 或其他通知渠道实现。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from common.models import RiskNotification


class RiskNotificationSender(ABC):
    """风险通知发送接口。"""

    @abstractmethod
    async def send_risk_notification(self, notification: RiskNotification) -> int:
        """发送一条风险通知，返回发送方生成的记录 ID 或发送数量。"""
        ...
