
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class RiskEvent(BaseModel):

    event_type: str = Field(description="事件类型标识，如 order_failure, api_abnormal, drawdown_exceeded")
    account_id: str = Field(description="关联账户")
    strategy_id: str = Field(description="关联策略")
    symbol_code: str | None = Field(default=None, description="关联标的代码，非标的维度风控事件可为 None")
    event_level: int = Field(ge=1, le=5, description="事件等级：1-提示 / 2-注意 / 3-警告 / 4-严重 / 5-紧急")
    event_message: str = Field(description="事件描述信息")
    occur_time: datetime = Field(description="事件发生时间")


class RiskNotification(BaseModel):

    notification_type: str = Field(description="通知类型：alert / circuit_breaker / abnormal / manual_intervention")
    risk_level: int = Field(ge=1, le=5, description="风险等级，含义同 RiskEvent.event_level")
    title: str = Field(description="通知标题")
    content: str = Field(description="通知正文")
    created_at: datetime = Field(description="通知生成时间")


class RiskEventResponse(BaseModel):

    risk_event_id: int = Field(description="风控事件记录 ID")
    status: str = Field(description="处理状态：received / rejected / escalated")
