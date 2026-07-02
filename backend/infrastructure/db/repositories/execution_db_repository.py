"""
执行层数据库仓储。

替换 InMemoryExecutionRepository，所有数据读写基于 MySQL。
核心接口方法委托给 operation / deal / asset / trade 四个单一职责仓储，
前端列表方法直接查询数据库表并格式化返回。
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from decimal import Decimal

from common.interfaces import AssetRepository, DealRepository, OperationRepository, TradeRepository
from common.models import ActivePosition, Asset, Deal, Operation, OrderResult, PagedResult, Trade
from infrastructure.db.connection import Database
from infrastructure.db.repositories.operation_repo import OperationRepository as DbOpRepo
from infrastructure.db.repositories.deal_repo import DealRepository as DbDealRepo
from infrastructure.db.repositories.asset_repo import AssetRepository as DbAssetRepo
from infrastructure.db.repositories.trade_repo import TradeRepository as DbTradeRepo

logger = logging.getLogger(__name__)


class ExecutionDbRepository(OperationRepository, DealRepository, AssetRepository, TradeRepository):
    """数据库版执行层仓储，行为与 InMemoryExecutionRepository 兼容。"""

    def __init__(self, db: Database):
        self._op_repo = DbOpRepo(db)
        self._deal_repo = DbDealRepo(db)
        self._asset_repo = DbAssetRepo(db)
        self._trade_repo = DbTradeRepo(db)
        self._db = db
        # save_order_result 暂存在内存中（订单列表从 operation 表读取）
        self._order_results: list[OrderResult] = []
        # save_positions 暂存在内存中（持仓来自 broker 适配器）
        self._positions: list[ActivePosition] = []

    # ── 操作读写 ─────────────────────────────────────────────────────

    async def add_operation(self, operation: Operation) -> None:
        """添加一条待执行操作（单条便捷方法）。"""
        await self._op_repo.insert_operations(
            operation.account_id, operation.strategy_id, [operation]
        )

    async def insert_operations(
        self, account_id: str, strategy_id: str, operations: list[Operation]
    ) -> int:
        return await self._op_repo.insert_operations(account_id, strategy_id, operations)

    async def get_pending_operations(
        self,
        account_id: str,
        strategy_id: str,
        market_id: int,
    ) -> list[Operation]:
        return await self._op_repo.get_pending_operations(
            account_id, strategy_id, market_id,
        )

    async def get_operations_by_range(
        self,
        account_id: str,
        strategy_id: str,
        market_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Operation]:
        return await self._op_repo.get_operations_by_range(
            account_id, strategy_id, market_id, start_time, end_time
        )

    async def update_status(
        self, operation_id: int, account_id: str, strategy_id: str, new_status: int
    ) -> bool:
        return await self._op_repo.update_status(operation_id, account_id, strategy_id, new_status)

    # ── 下单结果 ─────────────────────────────────────────────────────

    async def save_order_result(self, result: OrderResult) -> None:
        """记录下单结果（内存暂存，重启丢失；订单列表从 operation 表读取）。"""
        self._order_results.append(result)

    async def save_deal_from_order(
        self, result: OrderResult, operation: Operation | None = None
    ) -> None:
        """根据下单结果生成并保存成交记录。"""
        from execution.services.execution_repository import build_deal_from_order

        deal = build_deal_from_order(result, operation)
        if deal is not None:
            await self.insert_deal(deal.account_id, deal.strategy_id, deal)

    # ── 成交读写 ─────────────────────────────────────────────────────

    async def insert_deal(self, account_id: str, strategy_id: str, deal: Deal) -> int:
        return await self._deal_repo.insert_deal(account_id, strategy_id, deal)

    async def get_deals_before(
        self, account_id: str, strategy_id: str, market_id: int, current_time: datetime
    ) -> list[Deal]:
        return await self._deal_repo.get_deals_before(account_id, strategy_id, market_id, current_time)

    async def get_deals_by_range(
        self,
        account_id: str,
        strategy_id: str,
        market_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Deal]:
        return await self._deal_repo.get_deals_by_range(
            account_id, strategy_id, market_id, start_time, end_time
        )

    # ── 交易读写 ─────────────────────────────────────────────────────

    async def insert_trade(self, account_id: str, strategy_id: str, trade: Trade) -> int:
        return await self._trade_repo.insert_trade(account_id, strategy_id, trade)

    async def get_trades_by_range(
        self,
        account_id: str,
        strategy_id: str,
        market_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Trade]:
        return await self._trade_repo.get_trades_by_range(
            account_id, strategy_id, market_id, start_time, end_time
        )

    # ── 资产读写 ─────────────────────────────────────────────────────

    async def save_asset(self, asset: Asset) -> None:
        """兼容旧调用方式，将资产快照保存到账户级资产仓储。"""
        await self.sync_asset(asset.account_id, asset)

    async def sync_asset(self, account_id: str, asset: Asset) -> int:
        return await self._asset_repo.sync_asset(account_id, asset)

    async def get_assets_by_range(
        self, account_id: str, market_id: int, start_time: datetime, end_time: datetime
    ) -> list[Asset]:
        return await self._asset_repo.get_assets_by_range(
            account_id, market_id, start_time, end_time
        )

    # ── 持仓（暂存内存） ──────────────────────────────────────────────

    async def save_positions(self, positions: list[ActivePosition]) -> None:
        """覆盖保存当前持仓快照。"""
        self._positions = positions

    # ══════════════════════════════════════════════════════════════════
    #  前端列表接口（直接查询数据库）
    # ══════════════════════════════════════════════════════════════════

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
        """从 operation 表分页返回订单列表。"""
        if not all([account_id, strategy_id, market_id]):
            raise ValueError("account_id, strategy_id and market_id are required")
        acct = account_id
        strat = strategy_id
        mkt = market_id
        table = f"`{acct}_{strat}_operation`"

        where = ["market_id = %s", "account_id = %s", "strategy_id = %s"]
        params: list = [mkt, acct, strat]

        if status is not None:
            where.append("status = %s")
            params.append(status)

        where_sql = " AND ".join(where)

        # 总数
        cnt_row = self._db.fetch_one(
            f"SELECT COUNT(*) AS cnt FROM {table} WHERE {where_sql}", tuple(params)
        )
        total = cnt_row["cnt"] if cnt_row else 0

        # 分页数据
        offset = (page - 1) * size
        rows = self._db.fetch_all(
            f"SELECT operation_id, symbol_code, symbol_name, operation_type, direction, "
            f"order_type, price, quantity, created_at, status "
            f"FROM {table} WHERE {where_sql} "
            f"ORDER BY created_at DESC, operation_id DESC LIMIT %s OFFSET %s",
            tuple(params + [size, offset]),
        )

        result_rows = []
        for r in rows:
            op_type = r["operation_type"]
            direction = r["direction"]
            s = r["status"]
            result_rows.append({
                "id": r["operation_id"],
                "marketId": mkt,
                "accountId": acct,
                "strategyId": strat,
                "symbolCode": r["symbol_code"],
                "symbolName": r["symbol_name"] or "",
                "operationType": op_type,
                "direction": direction,
                "orderType": r["order_type"],
                "price": float(r["price"] or 0),
                "quantity": float(r["quantity"] or 0),
                "status": s,
                "statusLabel": self._order_status_label(s),
                "createdAt": r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(r["created_at"], datetime)
                else str(r["created_at"]),
            })

        # 可选按 symbol 过滤
        if symbol:
            kw = symbol.lower()
            result_rows = [
                row for row in result_rows
                if kw in row["symbolCode"].lower() or kw in row["symbolName"].lower()
            ]

        return PagedResult(list=result_rows, total=total, page=page, size=size)

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
        """从 deal 表分页返回成交列表。"""
        if not all([account_id, strategy_id, market_id]):
            raise ValueError("account_id, strategy_id and market_id are required")
        acct = account_id
        strat = strategy_id
        mkt = market_id
        table = f"`{acct}_{strat}_deal`"

        where = ["market_id = %s", "account_id = %s", "strategy_id = %s"]
        params: list = [mkt, acct, strat]

        if start_time is not None:
            where.append("deal_time >= %s")
            params.append(start_time)
        if end_time is not None:
            where.append("deal_time <= %s")
            params.append(end_time)

        where_sql = " AND ".join(where)

        cnt_row = self._db.fetch_one(
            f"SELECT COUNT(*) AS cnt FROM {table} WHERE {where_sql}", tuple(params)
        )
        total = cnt_row["cnt"] if cnt_row else 0

        offset = (page - 1) * size
        rows = self._db.fetch_all(
            f"SELECT * FROM {table} WHERE {where_sql} "
            f"ORDER BY deal_time DESC, deal_id DESC LIMIT %s OFFSET %s",
            tuple(params + [size, offset]),
        )

        result_rows = []
        for r in rows:
            deal_time = r["deal_time"]
            result_rows.append({
                "id": r["deal_id"],
                "operationId": r["operation_id"],
                "marketId": r["market_id"],
                "accountId": r["account_id"],
                "strategyId": r["strategy_id"],
                "symbolCode": r["symbol_code"],
                "symbolName": r["symbol_name"] or "",
                "dealType": r["deal_type"],
                "direction": r["direction"],
                "dealPrice": float(r["deal_price"] or 0),
                "dealQuantity": float(r["deal_quantity"] or 0),
                "dealAmount": float(r["deal_amount"] or 0),
                "commission": float(r["commission"] or 0),
                "positionAfter": float(r["position_after"] or 0),
                "isManual": r["is_manual"],
                "dealTime": deal_time.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(deal_time, datetime)
                else str(deal_time),
            })

        if symbol:
            kw = symbol.lower()
            result_rows = [
                row for row in result_rows
                if kw in row["symbolCode"].lower() or kw in row["symbolName"].lower()
            ]

        return PagedResult(list=result_rows, total=total, page=page, size=size)

    async def get_deal_stats(
        self,
        account_id: str,
        strategy_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict:
        """汇总成交统计指标（按今日/本周/本月分别统计）。"""
        table = f"`{account_id}_{strategy_id}_deal`"
        now = datetime.now()

        # 今日
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59)
        today = self._query_deal_stats(table, today_start, today_end)

        # 本周（周一 ~ 周日）
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        week = self._query_deal_stats(table, week_start, week_end)

        # 本月
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        month = self._query_deal_stats(table, month_start, month_end)

        return {
            "todayCount": today["cnt"],
            "todayAmount": round(today["amount"], 2),
            "todayCommission": round(today["commission"], 2),
            "weekCount": week["cnt"],
            "monthCount": month["cnt"],
        }

    def _query_deal_stats(self, table: str, start: datetime, end: datetime) -> dict:
        """查询指定时间范围内的成交汇总。"""
        row = self._db.fetch_one(
            f"SELECT COUNT(*) AS cnt, "
            f"COALESCE(SUM(deal_amount), 0) AS amount, "
            f"COALESCE(SUM(commission), 0) AS commission "
            f"FROM {table} WHERE deal_time >= %s AND deal_time <= %s",
            (start, end),
        )
        if row is None:
            return {"cnt": 0, "amount": 0.0, "commission": 0.0}
        return {
            "cnt": row["cnt"],
            "amount": float(row["amount"]),
            "commission": float(row["commission"]),
        }

    async def list_positions(self) -> list[dict]:
        """返回当前持仓列表视图（来自内存快照）。"""
        return [
            {
                "symbolCode": p.symbol_code,
                "symbolName": p.symbol_name,
                "direction": p.direction,
                "openPrice": float(p.open_price),
                "currentPrice": float(p.current_price or 0),
                "holdingQuantity": float(p.holding_quantity),
                "holdingAmount": float(p.holding_amount),
                "unrealizedPnl": float(p.unrealized_pnl),
                "unrealizedPnlRate": 0,
                "openTime": p.open_time.strftime("%Y-%m-%d") if p.open_time else "",
                "strategyId": p.strategy_id,
            }
            for p in self._positions
        ]

    async def get_account_assets(
        self,
        account_id: str,
        market_id: int,
        days: int | None = None,
    ) -> dict:
        """从 asset 表返回账户资产当前值与历史序列。"""
        acct = account_id
        mkt = market_id
        table = f"`{acct}_asset`"

        rows = self._db.fetch_all(
            f"SELECT created_at, total_asset, net_value, market_value, cash_balance "
            f"FROM {table} WHERE account_id = %s AND market_id = %s "
            f"ORDER BY created_at ASC",
            (acct, mkt),
        )
        if days is not None and days > 0 and len(rows) > days:
            rows = rows[-days:]

        if not rows:
            return {
                "current": {
                    "totalAsset": 0.0, "netValue": 1.0,
                    "marketValue": 0.0, "cashBalance": 0.0,
                },
                "history": [],
            }

        current = rows[-1]
        history = [
            {
                "date": r["created_at"].strftime("%Y-%m-%d")
                if isinstance(r["created_at"], datetime) else str(r["created_at"]),
                "totalAsset": float(r["total_asset"] or 0),
                "netValue": float(r["net_value"] or 0),
                "marketValue": float(r["market_value"] or 0),
                "cashBalance": float(r["cash_balance"] or 0),
            }
            for r in rows
        ]
        return {
            "current": {
                "totalAsset": float(current["total_asset"] or 0),
                "netValue": float(current["net_value"] or 0),
                "marketValue": float(current["market_value"] or 0),
                "cashBalance": float(current["cash_balance"] or 0),
            },
            "history": history,
        }

    async def get_asset_summary(self, market_id: int, account_id: str) -> dict:
        """返回 Dashboard 资产概览（当日/累计盈亏）。"""
        table = f"`{account_id}_asset`"
        rows = self._db.fetch_all(
            f"SELECT created_at, total_asset, net_value, market_value, cash_balance "
            f"FROM {table} WHERE account_id = %s AND market_id = %s "
            f"ORDER BY created_at ASC",
            (account_id, market_id),
        )

        if not rows:
            return {
                "totalAsset": 0.0, "netValue": 1.0,
                "todayPnl": 0.0, "totalPnl": 0.0,
                "marketValue": 0.0, "cashBalance": 0.0,
                "todayReturnRate": 0.0, "totalReturnRate": 0.0,
            }

        current = rows[-1]
        previous = rows[-2] if len(rows) >= 2 else None
        first = rows[0]

        cur_total = Decimal(str(current["total_asset"]))
        pre_total = Decimal(str(previous["total_asset"])) if previous else Decimal("0")
        first_total = Decimal(str(first["total_asset"]))

        today_pnl = cur_total - pre_total if previous else Decimal("0")
        total_pnl = cur_total - first_total
        today_rate = (
            today_pnl / pre_total * Decimal("100")
            if previous and pre_total != Decimal("0")
            else Decimal("0")
        )
        total_rate = (
            total_pnl / first_total * Decimal("100")
            if first_total != Decimal("0")
            else Decimal("0")
        )

        return {
            "totalAsset": float(cur_total),
            "netValue": float(current["net_value"] or 0),
            "todayPnl": float(today_pnl),
            "totalPnl": float(total_pnl),
            "marketValue": float(current["market_value"] or 0),
            "cashBalance": float(current["cash_balance"] or 0),
            "todayReturnRate": float(today_rate),
            "totalReturnRate": float(total_rate),
        }

    # ── 辅助 ─────────────────────────────────────────────────────────

    @staticmethod
    def _order_status_label(status: int) -> str:
        return {0: "待执行", 1: "已执行", 2: "失败", 3: "部分成交", 4: "已撤销"}.get(status, "未知")
