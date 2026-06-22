"""策略订单执行服务。

从 OperationRepository 拉取待执行操作，经过 OrderPreparer 转换为券商订单请求，并将成交和风险事件推送给对应接口。
"""

from common.interfaces import (
    AssetRepository,
    BrokerAdapter,
    DealRepository,
    OperationRepository,
    RiskEventHandler,
)
from common.models import ExecutionStatus, Operation, OrderResult, RiskEvent
from execution.services.asset_sync_service import AssetSyncService
from execution.services.execution_repository import InMemoryExecutionRepository, build_deal_from_order
from execution.services.order_preparer import OrderPreparer


class OrderExecutor:
    """执行层主编排器，负责策略操作到真实/模拟券商下单的完整链路。"""

    def __init__(
        self,
        adapter: BrokerAdapter,
        repository: InMemoryExecutionRepository | None = None,
        operation_repository: OperationRepository | None = None,
        deal_repository: DealRepository | None = None,
        asset_repository: AssetRepository | None = None,
        risk_handler: RiskEventHandler | None = None,
        preparer: OrderPreparer | None = None,
        asset_sync_service: AssetSyncService | None = None,
    ):
        self._adapter = adapter
        self._repository = repository or InMemoryExecutionRepository()
        self._operation_repository = operation_repository or self._repository
        self._deal_repository = deal_repository or self._repository
        self._asset_repository = asset_repository or self._repository
        self._risk_handler = risk_handler
        self._preparer = preparer or OrderPreparer(adapter)
        self._asset_sync_service = asset_sync_service or AssetSyncService(
            adapter,
            self._repository,
            asset_repository=self._asset_repository,
        )

    async def execute_pending_operations(
        self,
        market_id: int | None = None,
        account_id: str | None = None,
        strategy_id: str | None = None,
    ) -> dict:
        """执行符合条件的待处理操作，并返回批次执行统计。"""
        operations = await self._operation_repository.get_pending_operations(account_id, strategy_id, market_id)
        results: list[OrderResult] = []

        await self._adapter.connect()
        try:
            unlocked = await self._adapter.unlock()
            if not unlocked:
                await self._report_risk(None, "api_error", 5, "交易解锁失败")
                return {"status": ExecutionStatus.FAILED, "total": len(operations), "success": 0, "failed": len(operations)}

            for operation in operations:
                requests, reason = await self._preparer.prepare(operation)
                if not requests:
                    await self._report_risk(operation, "order_failed", 2, reason)
                    continue

                for request in requests:
                    result = await self._adapter.place_order(request)
                    await self._repository.save_order_result(result)
                    deal = build_deal_from_order(result, operation)
                    if deal is not None:
                        await self._deal_repository.insert_deal(deal.account_id, deal.strategy_id, deal)
                        await self._operation_repository.update_status(
                            operation.operation_id,
                            operation.account_id,
                            operation.strategy_id,
                            1,
                        )
                    results.append(result)
                    if not result.success:
                        await self._operation_repository.update_status(
                            operation.operation_id,
                            operation.account_id,
                            operation.strategy_id,
                            2,
                        )
                        await self._report_risk(operation, "order_failed", 3, result.message)

            if account_id is not None and market_id is not None:
                await self._asset_sync_service.sync_asset(account_id, market_id)
        finally:
            await self._adapter.close()

        success_count = sum(1 for result in results if result.success)
        failed_count = sum(1 for result in results if not result.success)
        if not results:
            status = ExecutionStatus.PENDING
        elif failed_count == 0:
            status = ExecutionStatus.SUCCESS
        elif success_count == 0:
            status = ExecutionStatus.FAILED
        else:
            status = ExecutionStatus.PARTIAL_SUCCESS

        return {
            "status": status,
            "total": len(results),
            "success": success_count,
            "failed": failed_count,
        }

    async def _report_risk(
        self,
        operation: Operation | None,
        event_type: str,
        event_level: int,
        message: str,
    ) -> None:
        """将执行异常转为风险事件并推送给风控层。"""
        if self._risk_handler is None:
            return
        await self._risk_handler.handle_risk_event(
            RiskEvent(
                event_type=event_type,
                account_id=operation.account_id if operation else "",
                strategy_id=operation.strategy_id if operation else "",
                symbol_code=operation.symbol_code if operation else None,
                event_level=event_level,
                event_message=message,
            )
        )
