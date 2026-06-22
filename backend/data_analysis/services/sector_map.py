import csv
import logging
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, Field

from common.models.analytics import SectorDistribution, SectorWeight
from common.models.trading import ActivePositions

logger = logging.getLogger(__name__)

_ZERO = Decimal("0")
_UNCLASSIFIED = "未分类"
_HK = 2  # 港股 market_id

# 源数据中的占位/无效行业值；命中即跳过该行，使其落入“未分类”。
_INVALID_SECTORS = {"", "-", "—", "未分类", "n/a", "na", "无"}
_INVALID_NAMES = {"无此数据"}

_DEFAULT_RESOURCE = (
    Path(__file__).resolve().parent.parent / "resources" / "stock_sector_dict.csv"
)

# 各市场的交易所后缀；归一化时仅剥离这些“已知后缀”，
# 因此美股类别点（BRK.B）不会被误当作后缀切掉。
_HK_SUFFIXES = {"HK"}
_CN_SUFFIXES = {"SH", "SZ", "SS", "BJ"}
_US_SUFFIXES = {"US", "O", "N", "OQ", "NYSE", "NASDAQ", "ARCA", "AMEX", "PK"}


def _strip_suffix(code: str, suffixes: set[str]) -> str:
    head, sep, tail = code.rpartition(".")
    return head if sep and tail in suffixes else code


def _norm_hk(code: str) -> str:
    # 港股：去 .HK + 去前导零（00700 / 0700.HK / 700 → 700）。
    c = _strip_suffix(code, _HK_SUFFIXES)
    return str(int(c)) if c.isdigit() else c


def _norm_cn_a(code: str) -> str:
    # A 股：去 .SH/.SZ 等后缀，保留前导零（000001 ≠ 1）。
    return _strip_suffix(code, _CN_SUFFIXES)


def _norm_us(code: str) -> str:
    # 美股：去已知交易所后缀，但保留类别点（BRK.B 原样、BRK.B.US → BRK.B）。
    return _strip_suffix(code, _US_SUFFIXES)


def _norm_default(code: str) -> str:
    # 未登记市场（如期货/加密）：仅做大写去空格，不臆测后缀/前导零规则。
    return code


# market_id → 代码归一化函数。新增市场时在此登记一条规则即可，调用方无需改动。
_NORMALIZERS = {1: _norm_cn_a, 2: _norm_hk, 3: _norm_us}


def register_normalizer(market_id: int, fn) -> None:
    """登记/覆盖某市场的代码归一化规则（产品化扩展点）。"""
    _NORMALIZERS[market_id] = fn


def _canonical_code(market_id: int, raw: str) -> str:
    code = (raw or "").strip().upper()
    return _NORMALIZERS.get(market_id, _norm_default)(code)


class SectorMapMeta(BaseModel):
    """加载结果元信息，便于启动时打印与排查覆盖率。"""

    source: str = Field(description="来源文件")
    market_id: int = Field(description="该映射归属的市场")
    standard: str = Field(default="", description="分类标准，如 恒生 / 申万 / 中信 / GICS")
    loaded: int = Field(description="成功载入的映射条数")
    skipped: int = Field(description="跳过的无效行数（无此数据 / 无行业）")
    total_rows: int = Field(description="源文件总行数")
    sectors: list[str] = Field(default_factory=list, description="覆盖到的行业列表")
    conflicts: list[str] = Field(
        default_factory=list, description="同代码不同行业的冲突，格式 代码:旧→新"
    )


class SectorMap:
    """标的→行业 映射表（分析层引用数据）。

    内部按 (market_id, 归一化代码) 索引，因此对前导零 / 交易所后缀的差异不敏感。
    查不到返回 None，由上层决定归入“未分类”。
    """

    def __init__(
        self,
        entries: dict[tuple[int, str], str],
        meta: SectorMapMeta | None = None,
        sources: list[SectorMapMeta] | None = None,
    ) -> None:
        self._entries = entries
        self.meta = meta
        # 单来源时 sources 即 [meta]；多来源合并时为各来源的元信息列表。
        self.sources = sources if sources is not None else ([meta] if meta else [])

    @classmethod
    def empty(cls) -> "SectorMap":
        return cls({}, None)

    def __len__(self) -> int:
        return len(self._entries)

    def lookup(self, market_id: int, symbol_code: str) -> str | None:
        return self._entries.get((market_id, _canonical_code(market_id, symbol_code)))


def load_sector_map_from_csv(
    path: str | Path,
    market_id: int = _HK,
    *,
    standard: str = "",
    code_col: str = "代码",
    name_col: str = "名称",
    sector_col: str = "一级行业分类",
) -> SectorMap:
    """从 CSV 载入单个市场的行业映射。

    默认列名匹配内置港股表（代码 / 名称 / 一级行业分类）；不同数据源可通过
    code_col / name_col / sector_col 覆盖（例如美股源常用英文表头 code / name / sector）。
    跳过“无此数据”及行业为空/占位的行；同代码不同行业记入 conflicts 并以后者为准。
    """
    p = Path(path)
    entries: dict[tuple[int, str], str] = {}
    conflicts: list[str] = []
    skipped = 0
    total = 0
    with p.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            code = (row.get(code_col) or "").strip()
            name = (row.get(name_col) or "").strip()
            sector = (row.get(sector_col) or "").strip()
            if not code or name in _INVALID_NAMES or sector.lower() in _INVALID_SECTORS:
                skipped += 1
                continue
            key = (market_id, _canonical_code(market_id, code))
            existing = entries.get(key)
            if existing is not None and existing != sector:
                conflicts.append(f"{code}:{existing}→{sector}")
            entries[key] = sector

    meta = SectorMapMeta(
        source=str(p),
        market_id=market_id,
        standard=standard,
        loaded=len(entries),
        skipped=skipped,
        total_rows=total,
        sectors=sorted(set(entries.values())),
        conflicts=conflicts,
    )
    logger.info(
        "行业映射载入：%d 条 / 共 %d 行（跳过 %d）/ %d 个行业 / 冲突 %d 处 / 市场=%d / 标准=%s / 来源=%s",
        meta.loaded, meta.total_rows, meta.skipped, len(meta.sectors),
        len(meta.conflicts), market_id, standard or "-", p.name,
    )
    if conflicts:
        logger.warning("行业映射存在同代码不同行业（取后者）：%s", "; ".join(conflicts[:10]))
    return SectorMap(entries, meta)


def default_sector_map() -> SectorMap:
    """载入随包内置的港股行业映射；资源缺失时降级为空表（全部记未分类）。"""
    if not _DEFAULT_RESOURCE.exists():
        logger.warning("未找到内置行业映射资源：%s，行业分布将全部记为未分类", _DEFAULT_RESOURCE)
        return SectorMap.empty()
    return load_sector_map_from_csv(_DEFAULT_RESOURCE, market_id=_HK, standard="恒生")


class SectorSourceSpec(BaseModel):
    """一个市场的行业映射来源描述（产品化扩展的配置单元）。"""

    market_id: int = Field(description="市场：1-沪深 2-港股 3-美股 4-期货 5-加密货币")
    path: str = Field(description="该市场行业映射 CSV 路径")
    standard: str = Field(default="", description="分类标准，如 申万 / 中信 / GICS / 恒生")
    code_col: str = Field(default="代码", description="代码列名")
    name_col: str = Field(default="名称", description="名称列名")
    sector_col: str = Field(default="一级行业分类", description="一级行业列名")


def build_sector_map(specs: list[SectorSourceSpec]) -> SectorMap:
    """按多个市场来源合并为一张映射表。

    键含 market_id，跨市场天然不冲突（港股 700 与某美股 ticker 互不干扰）；
    同一市场多文件时后载入覆盖先载入。不存在的来源会被跳过并记 warning，
    便于“先登记占位、拿到清单再补”的渐进扩展。
    """
    entries: dict[tuple[int, str], str] = {}
    sources: list[SectorMapMeta] = []
    for spec in specs:
        p = Path(spec.path)
        if not p.exists():
            logger.warning(
                "行业映射来源不存在，跳过：market_id=%d standard=%s path=%s",
                spec.market_id, spec.standard or "-", spec.path,
            )
            continue
        part = load_sector_map_from_csv(
            p, spec.market_id, standard=spec.standard,
            code_col=spec.code_col, name_col=spec.name_col, sector_col=spec.sector_col,
        )
        entries.update(part._entries)  # 同模块内访问内部索引，跨市场键不会相互覆盖
        sources.append(part.meta)

    aggregate = SectorMapMeta(
        source=" + ".join(s.source for s in sources) or "(无有效来源)",
        market_id=-1,  # -1 表示合并视图，非单一市场
        standard=" / ".join(sorted({s.standard for s in sources if s.standard})),
        loaded=len(entries),
        skipped=sum(s.skipped for s in sources),
        total_rows=sum(s.total_rows for s in sources),
        sectors=sorted({sec for s in sources for sec in s.sectors}),
        conflicts=[c for s in sources for c in s.conflicts],
    )
    logger.info(
        "合并行业映射：%d 条，覆盖市场 %s",
        len(entries), [s.market_id for s in sources],
    )
    return SectorMap(entries, meta=aggregate, sources=sources)


def sector_distribution(
    positions: ActivePositions, sector_map: SectorMap | None
) -> SectorDistribution:
    """按行业汇总持仓金额占比。

    未匹配到行业的标的归入“未分类”并在 unmatched_symbols 中列出；
    coverage_ratio = 已匹配行业的金额 / 总持仓金额，便于判断映射覆盖是否充分。
    """
    smap = sector_map or SectorMap.empty()
    total = sum((p.holding_amount for p in positions.active_positions), _ZERO)

    amount_by_sector: dict[str, Decimal] = {}
    matched_amount = _ZERO
    unmatched: list[str] = []
    seen: set[str] = set()
    for p in positions.active_positions:
        sector = smap.lookup(positions.market_id, p.symbol_code)
        if sector is None:
            sector = _UNCLASSIFIED
            if p.symbol_code not in seen:
                seen.add(p.symbol_code)
                unmatched.append(p.symbol_code)
        else:
            matched_amount += p.holding_amount
        amount_by_sector[sector] = amount_by_sector.get(sector, _ZERO) + p.holding_amount

    weights = [
        SectorWeight(
            sector=sector,
            holding_amount=amount,
            weight=float(amount / total) if total > _ZERO else 0.0,
        )
        for sector, amount in amount_by_sector.items()
    ]
    weights.sort(key=lambda w: w.weight, reverse=True)
    coverage = float(matched_amount / total) if total > _ZERO else 0.0
    return SectorDistribution(
        total_amount=total,
        coverage_ratio=coverage,
        sectors=weights,
        unmatched_symbols=unmatched,
    )
