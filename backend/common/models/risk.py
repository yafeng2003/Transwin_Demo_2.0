from datetime import datetime

from pydantic import BaseModel, Field


class RiskEvent(BaseModel):
    event_type: str = Field(description="order_failed / api_error / timeout / drawdown etc.")
    account_id: str
    strategy_id: str
    symbol_code: str | None = None
    event_level: int = Field(ge=1, le=5)
    event_message: str
    occur_time: datetime = Field(default_factory=datetime.now)
    status: str = "pending"


class RiskEventResponse(BaseModel):
    risk_event_id: int
    status: str


class RiskNotification(BaseModel):
    notification_type: str
    account_id: str = ""
    strategy_id: str = ""
    risk_level: int = Field(ge=1, le=5)
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_read: bool = False
    risk_event_id: int | None = None


class RiskMetric(BaseModel):
    current: float
    threshold: float
    breached: bool
