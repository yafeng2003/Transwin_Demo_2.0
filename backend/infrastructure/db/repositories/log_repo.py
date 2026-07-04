"""数据库日志仓储。

替代 InMemoryLogger，将系统日志和交易日志持久化到 MySQL。
"""

from datetime import datetime

from common.models import PagedResult
from infrastructure.db.connection import Database


class DbLogger:
    """数据库版日志记录器。"""

    def __init__(self, db: Database):
        self._db = db
        self._next_id = 1

    # ── 系统日志 ─────────────────────────────────────────────────────

    def log_system(self, level: str, module: str, message: str, detail: str = "") -> None:
        self._db.execute(
            "INSERT INTO system_logs (level, module, message, detail, created_at) "
            "VALUES (%s, %s, %s, %s, %s)",
            (level, module, message, detail, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        self._db.commit()

    def list_system_logs(
        self, level: str | None = None, module: str | None = None,
        page: int = 1, size: int = 20,
    ) -> PagedResult[dict]:
        where = []
        params: list = []
        if level:
            where.append("level = %s")
            params.append(level)
        if module:
            where.append("module = %s")
            params.append(module)

        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        cnt_row = self._db.fetch_one(f"SELECT COUNT(*) AS cnt FROM system_logs{where_sql}", tuple(params))
        total = cnt_row["cnt"] if cnt_row else 0

        offset = (page - 1) * size
        rows = self._db.fetch_all(
            f"SELECT id, level, module, message, detail, created_at "
            f"FROM system_logs{where_sql} ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
            tuple(params + [size, offset]),
        )
        return PagedResult(
            list=[{
                "id": r["id"],
                "level": r["level"],
                "module": r["module"],
                "message": r["message"],
                "detail": r["detail"] or "",
                "createdAt": r["created_at"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r["created_at"], "strftime") else str(r["created_at"]),
            } for r in rows],
            total=total, page=page, size=size,
        )

    # ── 交易日志 ─────────────────────────────────────────────────────

    def log_trading(self, log_type: str, symbol_code: str, symbol_name: str,
                    message: str, status: str = "success") -> None:
        type_labels = {"order": "下单", "cancel": "撤单", "deal": "成交"}
        self._db.execute(
            "INSERT INTO ggt_marsi_trading_log (log_type, type_label, symbol_code, symbol_name, message, status, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (log_type, type_labels.get(log_type, log_type), symbol_code, symbol_name, message, status,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        self._db.commit()

    def list_trading_logs(
        self, log_type: str | None = None,
        page: int = 1, size: int = 20,
    ) -> PagedResult[dict]:
        where = []
        params: list = []
        if log_type:
            where.append("log_type = %s")
            params.append(log_type)

        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        cnt_row = self._db.fetch_one(
            f"SELECT COUNT(*) AS cnt FROM ggt_marsi_trading_log{where_sql}", tuple(params)
        )
        total = cnt_row["cnt"] if cnt_row else 0

        offset = (page - 1) * size
        rows = self._db.fetch_all(
            f"SELECT id, log_type, type_label, symbol_code, symbol_name, message, status, created_at "
            f"FROM ggt_marsi_trading_log{where_sql} ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
            tuple(params + [size, offset]),
        )
        return PagedResult(
            list=[{
                "id": r["id"],
                "type": r["log_type"],
                "typeLabel": r["type_label"],
                "symbolCode": r["symbol_code"],
                "symbolName": r["symbol_name"],
                "message": r["message"],
                "status": r["status"],
                "createdAt": r["created_at"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r["created_at"], "strftime") else str(r["created_at"]),
            } for r in rows],
            total=total, page=page, size=size,
        )
