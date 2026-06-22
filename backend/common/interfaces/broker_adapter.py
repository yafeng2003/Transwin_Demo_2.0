"""BrokerAdapter 抽象接口。

执行层通过该接口访问券商能力，避免业务逻辑直接依赖 futu、mock 或其他具体券商实现。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from common.models import (
    ActivePosition,
    Asset,
    CancelOrderRequest,
    ModifyOrderRequest,
    OrderRequest,
    OrderResult,
)


class BrokerAdapter(ABC):
    """券商适配器接口，定义连接、行情、资产、持仓和订单操作契约。"""

    @abstractmethod
    async def connect(self) -> None:
        """建立券商连接或初始化所需上下文。"""
        ...

    @abstractmethod
    async def close(self) -> None:
        """关闭券商连接并释放上下文资源。"""
        ...

    @abstractmethod
    async def unlock(self) -> bool:
        """解锁交易权限，返回是否解锁成功。"""
        ...

    @abstractmethod
    async def get_account_assets(self, account_id: str, market_id: int) -> Asset:
        """查询账户资产快照。"""
        ...

    @abstractmethod
    async def get_positions(self, account_id: str, market_id: int) -> list[ActivePosition]:
        """查询账户当前持仓。"""
        ...

    @abstractmethod
    async def get_market_price(self, symbol_code: str) -> Decimal | None:
        """查询标的最新价格，无法获取时返回 None。"""
        ...

    @abstractmethod
    async def get_lot_size(self, symbol_code: str) -> int:
        """查询标的最小交易单位。"""
        ...

    @abstractmethod
    async def get_max_buy_quantity(self, symbol_code: str, price: Decimal) -> Decimal | None:
        """按指定价格查询最大可买数量，无法获取时返回 None。"""
        ...

    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResult:
        """提交订单并返回统一下单结果。"""
        ...

    @abstractmethod
    async def cancel_order(self, request: CancelOrderRequest) -> OrderResult:
        """撤销订单并返回统一结果。"""
        ...

    @abstractmethod
    async def modify_order(self, request: ModifyOrderRequest) -> OrderResult:
        """修改订单价格或数量。"""
        ...

    @abstractmethod
    async def query_order(self, order_id: str) -> OrderResult | None:
        """查询单个订单状态，查不到时返回 None。"""
        ...
