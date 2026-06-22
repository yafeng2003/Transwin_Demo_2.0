"""多市场行业映射扩展示例 / 模板。

运行：
    PYTHONPATH=. python -m data_analysis.scripts.extend_sector_maps

它把港股（内置全量）、A 股（申万样例）、美股（GICS 样例）三份映射合并成一张
SectorMap，并打印每个来源的载入摘要与若干查询示例。拿到各市场的全量清单后，
把下面 SPECS 里的 .sample.csv 换成你们的正式 .csv（或新增一条 SectorSourceSpec）即可，
**调用方代码无需改动**。

要点（多市场的真实差异，已在加载器内按市场处理）：
- 港股：去 .HK 后缀 + 去前导零（00700 / 0700.HK / 700 视为同一支）。
- A 股：保留前导零（000001 ≠ 1），去 .SH/.SZ 后缀，分类用申万/中信。
- 美股：保留类别点（BRK.B 原样），仅去已知交易所后缀，表头常为英文 code/name/sector。
"""

from pathlib import Path

from data_analysis.services.sector_map import (
    SectorSourceSpec,
    build_sector_map,
)

_RES = Path(__file__).resolve().parent.parent / "resources"

# —— 扩展点：每个市场一条来源。把 .sample.csv 换成正式清单即可 ——
SPECS: list[SectorSourceSpec] = [
    SectorSourceSpec(
        market_id=2, standard="恒生",
        path=str(_RES / "stock_sector_dict.csv"),      # 港股：内置全量
    ),
    SectorSourceSpec(
        market_id=1, standard="申万",
        path=str(_RES / "cn_a_sector_dict.sample.csv"),  # A 股：中文表头
    ),
    SectorSourceSpec(
        market_id=3, standard="GICS",
        path=str(_RES / "us_sector_dict.sample.csv"),    # 美股：英文表头，演示列映射
        code_col="code", name_col="name", sector_col="sector",
    ),
]

# 验证各市场归一化的查询示例：(market_id, 输入代码, 说明)
_DEMO_LOOKUPS = [
    (2, "00700", "港股 腾讯（带前导零，应命中）"),
    (2, "0700.HK", "港股 腾讯（带 .HK 后缀，应命中）"),
    (1, "000001", "A 股 平安银行（前导零有意义，应命中）"),
    (1, "1", "A 股 输入 1（不等于 000001，应未命中）"),
    (3, "AAPL", "美股 苹果（应命中）"),
    (3, "BRK.B", "美股 伯克希尔 B 类（类别点保留，应命中）"),
    (3, "AAPL.O", "美股 苹果（带 .O 后缀，应命中）"),
]


def main() -> None:
    sector_map = build_sector_map(SPECS)

    print("=" * 64)
    print("各来源载入摘要")
    print("=" * 64)
    for meta in sector_map.sources:
        print(
            f"  market_id={meta.market_id:<2} 标准={meta.standard or '-':<6} "
            f"载入 {meta.loaded:>4} / 共 {meta.total_rows:>4} 行 "
            f"(跳过 {meta.skipped}) 冲突 {len(meta.conflicts)} "
            f"来源={Path(meta.source).name}"
        )
    print(f"\n  合计 {len(sector_map)} 条，覆盖市场 "
          f"{[m.market_id for m in sector_map.sources]}")

    print("\n" + "=" * 64)
    print("查询示例（验证按市场的代码归一化）")
    print("=" * 64)
    for market_id, code, note in _DEMO_LOOKUPS:
        hit = sector_map.lookup(market_id, code)
        print(f"  [{market_id}] {code:<10} -> {hit or '未匹配':<14} {note}")

    print("\n" + "=" * 64)
    print("注入应用（装配阶段）")
    print("=" * 64)
    print(
        "  from data_analysis.scripts.extend_sector_maps import SPECS\n"
        "  from data_analysis.services.sector_map import build_sector_map\n"
        "  from data_analysis.app import build_app\n\n"
        "  app = build_app(\n"
        "      asset_repository, trade_repository, deal_repository, operation_repository,\n"
        "      report_store, sector_map=build_sector_map(SPECS),\n"
        "  )\n"
    )


if __name__ == "__main__":
    main()
