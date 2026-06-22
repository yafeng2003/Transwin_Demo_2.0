"""
Repository 公共基类。

表名拼接逻辑委托给 ``infrastructure.db.naming``，各业务 repo 只需声明 TABLE_SUFFIX。
"""

from __future__ import annotations

from infrastructure.db.connection import Database
from infrastructure.db.naming import table_name as _build_table_name


class BaseRepository:
    """Repository 基类。

    子类通过覆盖 TABLE_SUFFIX 声明对应的表后缀，
    表名实际由 ``infrastructure.db.naming.table_name`` 拼接。
    """

    TABLE_SUFFIX: str = ""

    def __init__(self, db: Database):
        self._db = db

    def _table_name(self, account_id: str, strategy_id: str | None = None) -> str:
        """拼出物理表名（含反引号），委托给 naming.table_name。"""
        return _build_table_name(account_id, self.TABLE_SUFFIX, strategy_id)
