from pathlib import Path
from datetime import datetime
from decimal import Decimal

from common.models.trading import ActivePosition, ActivePositions
from data_analysis.services.sector_map import (
    SectorMap,
    SectorSourceSpec,
    build_sector_map,
    default_sector_map,
    load_sector_map_from_csv,
    sector_distribution,
)

_RES = Path(__file__).resolve().parent.parent / "resources"

_CSV = (
    "代码,名称,一级行业分类,分类依据简述\n"
    "700,腾讯控股,资讯科技业,社交与游戏\n"
    "00005,汇丰控股,金融业,银行\n"        # 带前导零，应与 5 归一为同一支
    "0700.HK,腾讯重复,资讯科技业,后缀写法\n"  # 与 700 同代码（归一化后），且行业一致
    "398,无此数据,-,-\n"                  # 无此数据 + 占位行业，应跳过
    "1024,某游戏股,-,无行业\n"            # 行业为占位 -，应跳过
    "9988,阿里巴巴,金融业,误标行业\n"       # 与下一行同代码不同行业 -> 冲突，取后者
    "9988,阿里巴巴,资讯科技业,修正\n"
)


def _write(tmp_path, text=_CSV):
    p = tmp_path / "sector.csv"
    p.write_text(text, encoding="utf-8-sig")
    return p


def _pos(market_id, items):
    # items: list of (symbol_code, amount)
    aps = [
        ActivePosition(
            symbol_code=code, position_type=1, direction=1, open_price=Decimal("1"),
            holding_quantity=Decimal("1"), holding_amount=Decimal(str(amt)),
            open_time=datetime(2024, 1, 1), unrealized_pnl=Decimal("0"),
        )
        for code, amt in items
    ]
    return ActivePositions(
        market_id=market_id, account_id="a", strategy_id="s",
        current_time=datetime(2024, 1, 2), active_positions=aps,
    )


class TestLoader:
    def test_counts_skip_and_conflict(self, tmp_path):
        m = load_sector_map_from_csv(_write(tmp_path), market_id=2)
        # 7 行数据：跳过 398、1024 两行无效；700 与 0700.HK 归一为同一键；9988 出现两次
        assert m.meta.total_rows == 7
        assert m.meta.skipped == 2
        # 唯一键：700、5、9988 -> 3 条
        assert len(m) == 3
        assert "9988:金融业→资讯科技业" in m.meta.conflicts

    def test_hk_normalization_variants(self, tmp_path):
        m = load_sector_map_from_csv(_write(tmp_path), market_id=2)
        # 前导零 / 交易所后缀 / 裸代码 三种写法都应命中同一支
        assert m.lookup(2, "700") == "资讯科技业"
        assert m.lookup(2, "00700") == "资讯科技业"
        assert m.lookup(2, "0700.HK") == "资讯科技业"
        assert m.lookup(2, "5") == "金融业"
        assert m.lookup(2, "00005") == "金融业"
        # 冲突行取后者
        assert m.lookup(2, "9988") == "资讯科技业"

    def test_unmatched_and_wrong_market(self, tmp_path):
        m = load_sector_map_from_csv(_write(tmp_path), market_id=2)
        assert m.lookup(2, "9999") is None          # 不存在
        assert m.lookup(1, "700") is None            # 同代码不同市场不应命中（这是港股映射）

    def test_non_hk_leading_zero_is_significant(self, tmp_path):
        # A股(market_id=1)前导零有意义：000001 与 1 不应被视为同一支
        text = "代码,名称,一级行业分类,分类依据简述\n000001,平安银行,金融业,银行\n"
        m = load_sector_map_from_csv(_write(tmp_path, text), market_id=1)
        assert m.lookup(1, "000001") == "金融业"
        assert m.lookup(1, "1") is None


class TestBundledDefault:
    def test_default_map_loads_real_csv(self):
        m = default_sector_map()
        assert len(m) > 500                          # 真实港股清单约 525 支
        assert m.lookup(2, "700") == "资讯科技业"     # 腾讯
        assert m.lookup(2, "00700") == "资讯科技业"   # 归一化后同样命中
        assert m.lookup(2, "5") == "金融业"           # 汇丰
        assert m.lookup(2, "939") == "金融业"          # 建行
        # “无此数据”占位行不应进表
        assert m.lookup(2, "398") is None


class TestDistribution:
    def test_weights_and_full_coverage(self):
        m = default_sector_map()
        # 腾讯(资讯科技业) 600 + 汇丰(金融业) 400 -> 60% / 40%
        dist = sector_distribution(_pos(2, [("700", 600), ("5", 400)]), m)
        assert dist.total_amount == Decimal("1000")
        assert abs(dist.coverage_ratio - 1.0) < 1e-9
        top = dist.sectors[0]
        assert top.sector == "资讯科技业" and abs(top.weight - 0.6) < 1e-9
        assert dist.unmatched_symbols == []

    def test_unmatched_goes_to_bucket(self):
        m = default_sector_map()
        dist = sector_distribution(_pos(2, [("700", 500), ("ZZZ999", 500)]), m)
        assert "ZZZ999" in dist.unmatched_symbols
        assert abs(dist.coverage_ratio - 0.5) < 1e-9
        sectors = {w.sector for w in dist.sectors}
        assert "未分类" in sectors and "资讯科技业" in sectors

    def test_empty_positions(self):
        dist = sector_distribution(_pos(2, []), default_sector_map())
        assert dist.total_amount == Decimal("0")
        assert dist.coverage_ratio == 0.0
        assert dist.sectors == []

    def test_none_map_all_unclassified(self):
        # 未注入映射（None）时不应崩溃，全部归未分类
        dist = sector_distribution(_pos(2, [("700", 100)]), None)
        assert dist.sectors[0].sector == "未分类"
        assert dist.coverage_ratio == 0.0


_US_CSV = (
    "code,name,sector\n"
    "AAPL,Apple,Information Technology\n"
    "BRK.B,Berkshire B,Financials\n"      # 类别点不可当后缀切
    "JPM,JPMorgan,Financials\n"
)


class TestUSNormalization:
    def test_class_dot_preserved_and_suffix_stripped(self, tmp_path):
        p = tmp_path / "us.csv"
        p.write_text(_US_CSV, encoding="utf-8-sig")
        m = load_sector_map_from_csv(
            p, market_id=3, standard="GICS",
            code_col="code", name_col="name", sector_col="sector",
        )
        assert m.lookup(3, "AAPL") == "Information Technology"
        assert m.lookup(3, "AAPL.O") == "Information Technology"   # 去已知后缀
        assert m.lookup(3, "aapl") == "Information Technology"     # 大小写不敏感
        assert m.lookup(3, "BRK.B") == "Financials"               # 类别点保留
        assert m.lookup(3, "BRK.B.US") == "Financials"            # 去 .US，保留 .B
        assert m.lookup(3, "BRK") is None                         # 不应被误并到 BRK


class TestBuildSectorMap:
    def test_merge_skip_missing_and_no_cross_market_collision(self, tmp_path):
        hk = tmp_path / "hk.csv"
        hk.write_text("代码,名称,一级行业分类,分类依据简述\n5,汇丰,金融业,银行\n", encoding="utf-8-sig")
        cn = tmp_path / "cn.csv"
        cn.write_text("代码,名称,一级行业分类,分类依据简述\n5,浦发银行,银行,银行\n", encoding="utf-8-sig")
        specs = [
            SectorSourceSpec(market_id=2, path=str(hk), standard="恒生"),
            SectorSourceSpec(market_id=1, path=str(cn), standard="申万"),
            SectorSourceSpec(market_id=3, path=str(tmp_path / "does_not_exist.csv")),  # 跳过
        ]
        m = build_sector_map(specs)
        assert len(m.sources) == 2                 # 缺失来源被跳过
        assert len(m) == 2
        # 同代码 "5" 在不同市场互不覆盖
        assert m.lookup(2, "5") == "金融业"
        assert m.lookup(1, "5") == "银行"
        assert m.meta.market_id == -1              # 合并视图
        assert m.meta.loaded == 2

    def test_shipped_sample_files_load(self):
        # 守护随包样例文件可被正确解析（含英文列映射与 A 股前导零、美股类别点）
        specs = [
            SectorSourceSpec(market_id=1, path=str(_RES / "cn_a_sector_dict.sample.csv"), standard="申万"),
            SectorSourceSpec(
                market_id=3, path=str(_RES / "us_sector_dict.sample.csv"), standard="GICS",
                code_col="code", name_col="name", sector_col="sector",
            ),
        ]
        m = build_sector_map(specs)
        assert m.lookup(1, "000001") == "银行"
        assert m.lookup(1, "600519") == "食品饮料"
        assert m.lookup(3, "AAPL") == "Information Technology"
        assert m.lookup(3, "BRK.B") == "Financials"

    def test_register_normalizer_extension_point(self):
        from data_analysis.services import sector_map as sm
        # 自定义市场 9 的归一化：去 "X" 前缀
        sm.register_normalizer(9, lambda c: c[1:] if c.startswith("X") else c)
        try:
            entries = {(9, "ABC"): "测试行业"}
            mp = SectorMap(entries)
            assert mp.lookup(9, "XABC") == "测试行业"
        finally:
            sm._NORMALIZERS.pop(9, None)  # 复原，避免污染其他用例
