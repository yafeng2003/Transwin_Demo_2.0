
from abc import ABC, abstractmethod

from common.models.risk_event import RiskEvent, RiskEventResponse


class RiskEventHandler(ABC):

    @abstractmethod
    async def handle_risk_event(self, event: RiskEvent) -> RiskEventResponse:
        ...
