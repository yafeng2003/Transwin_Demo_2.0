"""Table naming helpers shared by repositories and schema management."""

from __future__ import annotations

SUFFIX_OPERATION = "operation"
SUFFIX_DEAL = "deal"
SUFFIX_TRADE = "trade"
SUFFIX_ASSET = "asset"
SUFFIX_RISK_EVENT = "risk_event"
SUFFIX_NOTIFICATION = "notification"
SUFFIX_REPORT = "report"


def table_name(
    account_id: str,
    suffix: str,
    strategy_id: str | None = None,
    *,
    quoted: bool = True,
) -> str:
    """Build a physical table name in {account}[_{strategy}]_{suffix} form."""
    parts = [account_id]
    if strategy_id is not None:
        parts.append(strategy_id)
    parts.append(suffix)
    name = "_".join(parts)
    return f"`{name}`" if quoted else name


def asset_table_name(account_id: str, *, quoted: bool = True) -> str:
    """Asset tables are account-scoped and do not include strategy_id."""
    return table_name(account_id, SUFFIX_ASSET, strategy_id=None, quoted=quoted)
