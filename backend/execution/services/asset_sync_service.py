"""资产同步服务。

执行层通过 BrokerAdapter 拉取账户资产与持仓快照，并通过仓储接口写入当前运行所需的存储实现。
"""

from common.interfaces import AssetRepository, BrokerAdapter
from execution.services.execution_repository import InMemoryExecutionRepository


class AssetSyncService:
    """账户资产与持仓同步的业务编排器。"""

    def __init__(
        self,
        adapter: BrokerAdapter,
        repository: InMemoryExecutionRepository,
        asset_repository: AssetRepository | None = None,
    ):
        self._adapter = adapter
        self._repository = repository
        self._asset_repository = asset_repository or repository

    async def sync_asset(
        self,
        account_id: str,
        market_id: int,
        sync_positions: bool = True,
    ) -> dict:
        """同步账户资产，按需同步当前持仓，并返回前端展示用结果。"""
        asset = await self._adapter.get_account_assets(account_id, market_id)
        await self._asset_repository.sync_asset(account_id, asset)

        position_count = 0
        if sync_positions:
            positions = await self._adapter.get_positions(account_id, market_id)
            await self._repository.save_positions(positions)
            position_count = len(positions)

        return {
            "status": "success",
            "accountId": account_id,
            "marketId": market_id,
            "assetSynced": True,
            "positionsSynced": sync_positions,
            "positionCount": position_count,
            "syncedAt": asset.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
