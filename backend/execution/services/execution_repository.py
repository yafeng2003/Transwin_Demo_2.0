"""执行层内存仓储。

用于本地开发、单元测试和默认组装场景；真实数据库接入时通过 common/interfaces 中的仓储接口替换。
"""

from datetime import datetime
from decimal import Decimal

from common.interfaces import AssetRepository, DealRepository, OperationRepository, TradeRepository
from common.models import ActivePosition, Asset, Deal, Operation, OrderResult, PagedResult, Trade


def build_deal_from_order(result: OrderResult, operation: Operation | None = None) -> Deal | None:
    """将券商下单结果转换为成交记录，失败订单不生成 Deal。"""
    if not result.success:
        return None

    price = result.price or Decimal("0")
    return Deal(
        deal_id=0,
        operation_id=operation.operation_id if operation else None,
        market_id=operation.market_id if operation else 1,
        account_id=operation.account_id if operation else "",
        strategy_id=operation.strategy_id if operation else "manual",
        symbol_code=result.symbol_code,
        symbol_name=operation.symbol_name if operation else "",
        asset_type=operation.asset_type if operation else 1,
        deal_type=operation.operation_type if operation else 1,
        direction=operation.direction if operation else 1,
        deal_price=price,
        deal_quantity=result.quantity,
        deal_amount=price * result.quantity,
        commission=Decimal("0"),
        position_after=Decimal("0"),
        deal_time=result.created_at,
        is_manual=1 if operation is None else 0,
    )


class InMemoryExecutionRepository(OperationRepository, DealRepository, AssetRepository, TradeRepository):
    """执行层的内存版 Operation / Deal / Asset 仓储实现。"""

    def __init__(self):
        self._operations: list[Operation] = []
        self._order_results: list[OrderResult] = []
        self._deals: list[Deal] = []
        self._trades: list[Trade] = []
        self._assets: list[Asset] = []
        self._positions: list[ActivePosition] = []

    async def add_operation(self, operation: Operation) -> None:
        """添加一条待执行操作，供测试和本地流程使用。"""
        self._operations.append(operation)

    # ── 操作读写 ─────────────────────────────────────────────────

    async def insert_operations(
        self, account_id: str, strategy_id: str, operations: list[Operation]
    ) -> int:
        self._operations.extend(operations)
        return len(operations)

    async def get_pending_operations(
        self,
        account_id: str | None = None,
        strategy_id: str | None = None,
        market_id: int | None = None,
    ) -> list[Operation]:
        return [
            op
            for op in self._operations
            if op.status == 0
            and (market_id is None or op.market_id == market_id)
            and (account_id is None or op.account_id == account_id)
            and (strategy_id is None or op.strategy_id == strategy_id)
        ]

    async def get_operations_by_range(
        self,
        account_id: str,
        strategy_id: str,
        market_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Operation]:
        """按时间范围查询操作记录。"""
        return [
            op
            for op in self._operations
            if op.account_id == account_id
            and op.strategy_id == strategy_id
            and op.market_id == market_id
            and start_time <= op.created_at <= end_time
        ]

    async def update_status(
        self, operation_id: int, account_id: str, strategy_id: str, new_status: int
    ) -> bool:
        for operation in self._operations:
            if (
                operation.operation_id == operation_id
                and operation.account_id == account_id
                and operation.strategy_id == strategy_id
            ):
                operation.status = new_status
                return True
        return False

    async def save_order_result(self, result: OrderResult) -> None:
        """记录一次券商下单结果。"""
        self._order_results.append(result)

    async def save_deal_from_order(self, result: OrderResult, operation: Operation | None = None) -> None:
        """根据下单结果生成并保存成交记录。"""
        deal = build_deal_from_order(result, operation)
        if deal is not None:
            await self.insert_deal(deal.account_id, deal.strategy_id, deal)

    async def insert_deal(self, account_id: str, strategy_id: str, deal: Deal) -> int:
        """写入成交记录，并生成内存自增 ID。"""
        deal_id = len(self._deals) + 1
        deal.deal_id = deal_id
        self._deals.append(deal)
        return deal_id

    async def get_deals_before(
        self, account_id: str, strategy_id: str, market_id: int, current_time: datetime
    ) -> list[Deal]:
        """查询指定时间点之前的成交记录。"""
        return [
            deal
            for deal in self._deals
            if deal.account_id == account_id
            and deal.strategy_id == strategy_id
            and deal.market_id == market_id
            and deal.deal_time <= current_time
        ]

    async def get_deals_by_range(
        self,
        account_id: str,
        strategy_id: str,
        market_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Deal]:
        """按时间范围查询成交记录。"""
        return [
            deal
            for deal in self._deals
            if deal.account_id == account_id
            and deal.strategy_id == strategy_id
            and deal.market_id == market_id
            and start_time <= deal.deal_time <= end_time
        ]

    async def insert_trade(self, account_id: str, strategy_id: str, trade: Trade) -> int:
        """写入完整交易记录，并生成内存自增 ID。"""
        trade_id = len(self._trades) + 1
        trade.trade_id = trade_id
        self._trades.append(trade)
        return trade_id

    async def get_trades_by_range(
        self,
        account_id: str,
        strategy_id: str,
        market_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Trade]:
        """按时间范围查询完整交易记录。"""
        return [
            trade
            for trade in self._trades
            if trade.account_id == account_id
            and trade.strategy_id == strategy_id
            and trade.market_id == market_id
            and trade.close_time is not None
            and start_time <= trade.close_time <= end_time
        ]

    async def save_asset(self, asset: Asset) -> None:
        """兼容旧调用方式，将资产快照保存到账户级资产仓储。"""
        await self.sync_asset(asset.account_id, asset)

    async def sync_asset(self, account_id: str, asset: Asset) -> int:
        """写入资产快照，并生成内存自增 ID。"""
        asset_id = len(self._assets) + 1
        asset.asset_id = asset_id
        self._assets.append(asset)
        return asset_id

    async def get_assets_by_range(
        self, account_id: str, market_id: int, start_time: datetime, end_time: datetime
    ) -> list[Asset]:
        """按时间范围查询账户资产快照。"""
        return [
            asset
            for asset in self._assets
            if asset.account_id == account_id
            and asset.market_id == market_id
            and start_time <= asset.created_at <= end_time
        ]

    async def save_positions(self, positions: list[ActivePosition]) -> None:
        """覆盖保存当前持仓快照。"""
        self._positions = positions

    # ── 前端列表接口 ───────────────────────────────────────────────

    async def list_orders(
        self,
        page: int = 1,
        size: int = 20,
        market_id: int | None = None,
        account_id: str | None = None,
        strategy_id: str | None = None,
        status: int | None = None,
        symbol: str | None = None,
    ) -> PagedResult[dict]:
        """分页返回订单列表视图。"""
        rows = [
            {
                "id": index,
                "marketId": (result.raw or {}).get("marketId", 1),
                "accountId": (result.raw or {}).get("accountId", ""),
                "strategyId": (result.raw or {}).get("strategyId", "manual"),
                "symbolCode": result.symbol_code,
                "symbolName": (result.raw or {}).get("symbolName", ""),
                "operationType": (result.raw or {}).get("operationType", 1),
                "direction": 1 if result.side == "BUY" else 2,
                "orderType": 1 if result.order_type == "MARKET" else 2,
                "price": float(result.price or 0),
                "quantity": float(result.quantity),
                "status": 1 if result.success else 2,
                "statusLabel": "已提交" if result.success else "失败",
                "createdAt": result.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for index, result in enumerate(self._order_results, 1)
        ]
        rows = [
            row
            for row in rows
            if (market_id is None or row["marketId"] == market_id)
            and (account_id is None or row["accountId"] == account_id)
            and (strategy_id is None or row["strategyId"] == strategy_id)
            and (status is None or row["status"] == status)
            and self._matches_symbol(row, symbol)
        ]
        start = (page - 1) * size
        end = start + size
        return PagedResult(list=rows[start:end], total=len(rows), page=page, size=size)

    async def list_deals(
        self,
        page: int = 1,
        size: int = 20,
        market_id: int | None = None,
        account_id: str | None = None,
        strategy_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        symbol: str | None = None,
    ) -> PagedResult[dict]:
        """分页返回成交列表视图。"""
        deals = [
            deal
            for deal in self._deals
            if (market_id is None or deal.market_id == market_id)
            and (account_id is None or deal.account_id == account_id)
            and (strategy_id is None or deal.strategy_id == strategy_id)
            and (start_time is None or deal.deal_time >= start_time)
            and (end_time is None or deal.deal_time <= end_time)
        ]
        rows = [
            {
                "id": deal.deal_id,
                "operationId": deal.operation_id,
                "marketId": deal.market_id,
                "accountId": deal.account_id,
                "strategyId": deal.strategy_id,
                "symbolCode": deal.symbol_code,
                "symbolName": deal.symbol_name,
                "dealType": deal.deal_type,
                "direction": deal.direction,
                "dealPrice": float(deal.deal_price),
                "dealQuantity": float(deal.deal_quantity),
                "dealAmount": float(deal.deal_amount),
                "commission": float(deal.commission),
                "positionAfter": float(deal.position_after),
                "isManual": deal.is_manual,
                "dealTime": deal.deal_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for deal in deals
        ]
        rows = [row for row in rows if self._matches_symbol(row, symbol)]
        start = (page - 1) * size
        end = start + size
        return PagedResult(list=rows[start:end], total=len(rows), page=page, size=size)

    async def get_deal_stats(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict:
        """汇总成交统计指标。"""
        deals = [
            deal
            for deal in self._deals
            if (start_time is None or deal.deal_time >= start_time)
            and (end_time is None or deal.deal_time <= end_time)
        ]
        today_amount = sum(deal.deal_amount for deal in deals)
        today_commission = sum(deal.commission for deal in deals)
        return {
            "todayCount": len(deals),
            "todayAmount": float(today_amount),
            "todayCommission": float(today_commission),
            "weekCount": len(deals),
            "monthCount": len(deals),
        }

    async def list_positions(self) -> list[dict]:
        """返回当前持仓列表视图。"""
        return [
            {
                "symbolCode": position.symbol_code,
                "symbolName": position.symbol_name,
                "direction": position.direction,
                "openPrice": float(position.open_price),
                "currentPrice": float(position.current_price or 0),
                "holdingQuantity": float(position.holding_quantity),
                "holdingAmount": float(position.holding_amount),
                "unrealizedPnl": float(position.unrealized_pnl),
                "unrealizedPnlRate": 0,
                "openTime": position.open_time.strftime("%Y-%m-%d") if position.open_time else "",
                "strategyId": position.strategy_id,
            }
            for position in self._positions
        ]

    async def get_account_assets(
        self,
        account_id: str | None = None,
        market_id: int | None = None,
        days: int | None = None,
    ) -> dict:
        """返回账户资产当前值与历史序列。"""
        assets = [
            asset
            for asset in self._assets
            if (account_id is None or asset.account_id == account_id)
            and (market_id is None or asset.market_id == market_id)
        ]
        if days is not None and days > 0:
            assets = assets[-days:]
        current = assets[-1] if assets else Asset(
            created_at=datetime.now(),
            market_id=market_id or 1,
            account_id=account_id or "ggt",
            total_asset=Decimal("0"),
            net_value=Decimal("1"),
            market_value=Decimal("0"),
            cash_balance=Decimal("0"),
        )
        return {
            "current": {
                "totalAsset": float(current.total_asset),
                "netValue": float(current.net_value),
                "marketValue": float(current.market_value),
                "cashBalance": float(current.cash_balance),
            },
            "history": [
                {
                    "date": asset.created_at.strftime("%Y-%m-%d"),
                    "totalAsset": float(asset.total_asset),
                    "netValue": float(asset.net_value),
                    "marketValue": float(asset.market_value),
                    "cashBalance": float(asset.cash_balance),
                }
                for asset in assets
            ],
        }

    async def get_asset_summary(self, market_id: int, account_id: str) -> dict:
        """返回 Dashboard 资产概览。"""
        assets = [
            asset
            for asset in self._assets
            if asset.market_id == market_id and asset.account_id == account_id
        ]
        current = assets[-1] if assets else Asset(
            created_at=datetime.now(),
            market_id=market_id,
            account_id=account_id,
            total_asset=Decimal("0"),
            net_value=Decimal("1"),
            market_value=Decimal("0"),
            cash_balance=Decimal("0"),
        )
        previous = assets[-2] if len(assets) >= 2 else None
        first = assets[0] if assets else None

        today_pnl = current.total_asset - previous.total_asset if previous else Decimal("0")
        total_pnl = current.total_asset - first.total_asset if first else Decimal("0")
        today_return_rate = (
            today_pnl / previous.total_asset * Decimal("100")
            if previous and previous.total_asset != Decimal("0")
            else Decimal("0")
        )
        total_return_rate = (
            total_pnl / first.total_asset * Decimal("100")
            if first and first.total_asset != Decimal("0")
            else Decimal("0")
        )

        return {
            "totalAsset": float(current.total_asset),
            "netValue": float(current.net_value),
            "todayPnl": float(today_pnl),
            "totalPnl": float(total_pnl),
            "marketValue": float(current.market_value),
            "cashBalance": float(current.cash_balance),
            "todayReturnRate": float(today_return_rate),
            "totalReturnRate": float(total_return_rate),
        }

    def _matches_symbol(self, row: dict, symbol: str | None) -> bool:
        if not symbol:
            return True
        keyword = symbol.lower()
        return keyword in str(row.get("symbolCode", "")).lower() or keyword in str(row.get("symbolName", "")).lower()
