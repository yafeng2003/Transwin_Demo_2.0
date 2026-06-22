import os
from dataclasses import dataclass


@dataclass(frozen=True)
class FutuSettings:
    host: str = "127.0.0.1"
    port: int = 11111
    trading_env: str = "SIMULATE"
    trading_market: str = "HK"
    trading_pwd: str = ""
    security_firm: str = "FUTUSECURITIES"


@dataclass(frozen=True)
class ExecutionSettings:
    split_base_size: int = 1000
    split_min_count: int = 3
    split_max_count: int = 5
    split_interval_seconds: float = 2.0


def load_futu_settings() -> FutuSettings:
    return FutuSettings(
        host=os.getenv("FUTUOPEND_ADDRESS", "127.0.0.1"),
        port=int(os.getenv("FUTUOPEND_PORT", "11111")),
        trading_env=os.getenv("FUTU_TRADING_ENV", "SIMULATE"),
        trading_market=os.getenv("FUTU_TRADING_MARKET", "HK"),
        trading_pwd=os.getenv("FUTU_TRADING_PWD", ""),
        security_firm=os.getenv("FUTU_SECURITY_FIRM", "FUTUSECURITIES"),
    )


def load_execution_settings() -> ExecutionSettings:
    return ExecutionSettings(
        split_base_size=int(os.getenv("ORDER_SPLIT_BASE_SIZE", "1000")),
        split_min_count=int(os.getenv("ORDER_SPLIT_MIN_COUNT", "3")),
        split_max_count=int(os.getenv("ORDER_SPLIT_MAX_COUNT", "5")),
        split_interval_seconds=float(os.getenv("ORDER_SPLIT_INTERVAL", "2.0")),
    )
