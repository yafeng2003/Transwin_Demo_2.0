from .memory_logger import InMemoryLogger, app_logger

__all__ = ["InMemoryLogger", "app_logger", "set_app_logger"]


def set_app_logger(logger):
    """替换全局 app_logger 实例（例如从内存日志切换为数据库日志）。"""
    global app_logger
    app_logger = logger
