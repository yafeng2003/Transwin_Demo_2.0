from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


class ActivePosition(BaseModel):
    symbol_code: str
    symbol_name: str = ""
    position_type: int = 1
    direction: int = 1
    open_price: Decimal
    current_price: Decimal | None = None
    holding_quantity: Decimal
    holding_amount: Decimal
    open_time: datetime | None = None
    unrealized_pnl: Decimal = Decimal("0")
    strategy_id: str = ""


class ActivePositions(BaseModel):
    market_id: int
    account_id: str
    strategy_id: str | None = None
    current_time: datetime
    active_positions: list[ActivePosition]


class OrderRequest(BaseModel):
    symbol_code: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal = Field(gt=0)
    price: Decimal | None = None
    market_id: int = 1
    account_id: str
    strategy_id: str = ""
    operation_id: int | None = None
    remark: str = ""
    is_manual: bool = False


class OrderResult(BaseModel):
    success: bool
    order_id: str | None = None
    symbol_code: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Decimal | None = None
    status: str
    message: str = ""
    raw: dict | None = None
    created_at: datetime = Field(default_factory=datetime.now)


class CancelOrderRequest(BaseModel):
    order_id: str
    account_id: str
    market_id: int = 1


class ModifyOrderRequest(BaseModel):
    order_id: str
    account_id: str
    market_id: int = 1
    price: Decimal | None = None
    quantity: Decimal | None = None
