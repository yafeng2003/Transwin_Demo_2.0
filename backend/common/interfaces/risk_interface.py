"""风险事件处理抽象接口。

执行层通过该接口向风控层推送风险事件，避免直接依赖风控服务具体实现。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from common.models import RiskEvent, RiskEventResponse


class RiskEventHandler(ABC):
    """风险事件处理接口。"""

    @abstractmethod
    async def handle_risk_event(self, event: RiskEvent) -> RiskEventResponse:
        """处理单个风险事件并返回处理结果。"""
        ...
