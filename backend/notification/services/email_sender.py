"""邮件通知发送器。

实现 RiskNotificationSender 接口，将风险通知通过 SMTP SSL 发送到配置的告警收件人。
"""

import smtplib
import ssl
from email.message import EmailMessage

from common.interfaces import RiskNotificationSender
from common.models import RiskNotification


class EmailNotificationSender(RiskNotificationSender):
    """基于 SMTP 的风险通知发送实现。"""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_auth_code: str,
        alert_to: list[str],
    ):
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_auth_code = smtp_auth_code
        self._alert_to = [addr for addr in alert_to if addr]

    async def send_risk_notification(self, notification: RiskNotification) -> int:
        """发送单条风险通知邮件，返回发送条数。"""
        if not self._smtp_user or not self._smtp_auth_code or not self._alert_to:
            raise RuntimeError("email notification is not configured")

        message = EmailMessage()
        message["Subject"] = notification.title
        message["From"] = self._smtp_user
        message["To"] = ", ".join(self._alert_to)
        message.set_content(notification.content)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self._smtp_host, self._smtp_port, context=context) as server:
            server.login(self._smtp_user, self._smtp_auth_code)
            server.send_message(message)

        return 1
