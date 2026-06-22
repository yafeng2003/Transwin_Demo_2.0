"""naming.py 单元测试。

纯函数，无需 mock，覆盖各种边界情况。
"""

from __future__ import annotations

from infrastructure.db.naming import (
    SUFFIX_ASSET,
    SUFFIX_DEAL,
    SUFFIX_NOTIFICATION,
    SUFFIX_OPERATION,
    SUFFIX_RISK_EVENT,
    SUFFIX_TRADE,
    asset_table_name,
    table_name,
)


class TestSuffixConstants:
    """表后缀常量是否与预期一致。"""

    def test_values(self) -> None:
        assert SUFFIX_OPERATION == "operation"
        assert SUFFIX_DEAL == "deal"
        assert SUFFIX_TRADE == "trade"
        assert SUFFIX_ASSET == "asset"
        assert SUFFIX_RISK_EVENT == "risk_event"
        assert SUFFIX_NOTIFICATION == "notification"


class TestTableName:
    """table_name 核心函数。"""

    # ── 含 strategy_id ─────────────────────────────────────────

    def test_with_strategy_quoted(self) -> None:
        assert table_name("ly", SUFFIX_OPERATION, "maop") == "`ly_maop_operation`"

    def test_with_strategy_unquoted(self) -> None:
        assert (
            table_name("ly", SUFFIX_DEAL, "maop", quoted=False)
            == "ly_maop_deal"
        )

    # ── 不含 strategy_id（如 asset 表）──────────────────────────

    def test_without_strategy_quoted(self) -> None:
        assert table_name("ly", SUFFIX_ASSET) == "`ly_asset`"

    def test_without_strategy_unquoted(self) -> None:
        assert (
            table_name("ly", SUFFIX_ASSET, quoted=False)
            == "ly_asset"
        )

    def test_with_strategy_none_equals_no_strategy(self) -> None:
        """显式传入 strategy_id=None 等同于不传。"""
        assert table_name("ly", SUFFIX_ASSET, None) == "`ly_asset`"

    # ── 边界情况 ───────────────────────────────────────────────

    def test_account_id_contains_underscore(self) -> None:
        """账户编码本身就含下划线时，表名不应再额外处理。"""
        result = table_name("my_account", SUFFIX_TRADE, "strat")
        assert result == "`my_account_strat_trade`"

    def test_suffix_other_value(self) -> None:
        """suffix 可以是任意字符串，不限于预定义常量。"""
        result = table_name("ly", "custom_suffix", "s1", quoted=False)
        assert result == "ly_s1_custom_suffix"


class TestAssetTableName:
    """asset_table_name 快捷方法。"""

    def test_quoted_default(self) -> None:
        assert asset_table_name("ly") == "`ly_asset`"

    def test_unquoted(self) -> None:
        assert asset_table_name("test", quoted=False) == "test_asset"

    def test_invokes_table_name(self) -> None:
        """确保快捷方法使用了正确的参数委托给 table_name。"""
        expected = table_name("x", SUFFIX_ASSET, None, quoted=True)
        assert asset_table_name("x") == expected
