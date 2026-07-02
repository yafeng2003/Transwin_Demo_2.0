"""内存日志服务。

在 Mock 模式下替代数据库日志表，支持系统日志和交易日志的记录与分页查询。
"""

from datetime import datetime

from common.models import PagedResult


class InMemoryLogger:
    """线程安全的内存日志记录器。"""

    def __init__(self):
        self._system_logs: list[dict] = []
        self._trading_logs: list[dict] = []
        self._next_id = 1

    def log_system(self, level: str, module: str, message: str, detail: str = "") -> None:
        self._system_logs.insert(0, {
            "id": self._next_id,
            "level": level,
            "module": module,
            "message": message,
            "detail": detail,
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        self._next_id += 1

    def log_trading(self, log_type: str, symbol_code: str, symbol_name: str,
                    message: str, status: str = "success") -> None:
        type_labels = {"order": "下单", "cancel": "撤单", "deal": "成交"}
        self._trading_logs.insert(0, {
            "id": self._next_id,
            "type": log_type,
            "typeLabel": type_labels.get(log_type, log_type),
            "symbolCode": symbol_code,
            "symbolName": symbol_name,
            "message": message,
            "status": status,
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        self._next_id += 1

    def list_system_logs(self, level: str | None = None, module: str | None = None,
                         page: int = 1, size: int = 20) -> PagedResult[dict]:
        rows = [
            row for row in self._system_logs
            if (level is None or row["level"] == level)
            and (module is None or row["module"] == module)
        ]
        start = (page - 1) * size
        return PagedResult(list=rows[start:start + size], total=len(rows), page=page, size=size)

    def list_trading_logs(self, log_type: str | None = None,
                          page: int = 1, size: int = 20) -> PagedResult[dict]:
        rows = [
            row for row in self._trading_logs
            if (log_type is None or row["type"] == log_type)
        ]
        start = (page - 1) * size
        return PagedResult(list=rows[start:start + size], total=len(rows), page=page, size=size)


# 全局单例
app_logger = InMemoryLogger()
