"""
从 ggt_marsi_deal 表读取成交记录，配对开平仓生成 trade 记录并写入 ggt_marsi_trade。

如果 deal 表为空，先自动从项目根目录的 ggt_marsi_deal.csv 导入数据。

用法：
  cd backend
  python -m infrastructure.scripts.generate_trades_from_deals
"""

from __future__ import annotations

import csv
import os
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PACKAGE_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)

from infrastructure.db.connection import Database, DatabaseConfig
from infrastructure.db.schema_manager import SchemaManager

# ── 配置 ──────────────────────────────────────────────────────────────
ACCOUNT_ID = "ggt"
STRATEGY_ID = "marsi"
MARKET_ID = 2

DEAL_CSV = os.path.join(
    os.path.abspath(os.path.join(_PACKAGE_ROOT, "..")),  # → Transwin_0625/
    "ggt_marsi_deal.csv",
)

DB_CONFIG = DatabaseConfig(
    host="192.16.1.112",
    port=3306,
    user="root",
    password="",
    database="strategy_system",
)

ZERO = Decimal("0")


# ── CSV 导入 ──────────────────────────────────────────────────────────

def load_deal_csv(path: str) -> list[dict]:
    """读取 deal CSV，返回按 deal_time 排序的行列表。"""
    rows: list[dict] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append({
                "deal_id": int(row["deal_id"]),
                "operation_id": int(row["operation_id"]),
                "market_id": int(row["market_id"]),
                "account_id": row["account_id"].strip(),
                "strategy_id": row["strategy_id"].strip(),
                "symbol_code": row["symbol_code"].strip(),
                "symbol_name": row.get("symbol_name", "").strip(),
                "asset_type": int(row["asset_type"]),
                "deal_type": int(row["deal_type"]),
                "direction": int(row["direction"]),
                "deal_price": Decimal(row["deal_price"].strip()),
                "deal_quantity": Decimal(row["deal_quantity"].strip()),
                "deal_amount": Decimal(row["deal_amount"].strip()),
                "commission": Decimal(row["commission"].strip()),
                "position_after": Decimal(row["position_after"].strip()),
                "is_manual": int(row["is_manual"]),
                "deal_time": datetime.strptime(row["deal_time"].strip(), "%Y-%m-%d"),
            })
    rows.sort(key=lambda r: (r["symbol_code"], r["deal_time"], r["deal_id"]))
    return rows


def import_deal_csv(db: Database, rows: list[dict]) -> int:
    """将 CSV 数据写入 deal 表，返回写入行数。"""
    table = f"`{ACCOUNT_ID}_{STRATEGY_ID}_deal`"
    sql = (
        f"INSERT INTO {table} "
        f"(operation_id, market_id, account_id, strategy_id, "
        f"symbol_code, symbol_name, asset_type, deal_type, direction, "
        f"deal_price, deal_quantity, deal_amount, commission, "
        f"position_after, is_manual, deal_time) "
        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, "
        f"%s, %s, %s, %s, %s, %s, %s)"
    )
    count = 0
    for r in rows:
        db.execute(sql, (
            r["operation_id"],
            r["market_id"],
            r["account_id"],
            r["strategy_id"],
            r["symbol_code"],
            r["symbol_name"],
            r["asset_type"],
            r["deal_type"],
            r["direction"],
            r["deal_price"],
            r["deal_quantity"],
            r["deal_amount"],
            r["commission"],
            r["position_after"],
            r["is_manual"],
            r["deal_time"],
        ))
        count += 1
        if count % 50 == 0:
            db.commit()
    db.commit()
    return count


# ── Deal → Trade 生成 ──────────────────────────────────────────────

def fetch_deals(db: Database) -> list[dict]:
    """读取 deal 表全部记录，按 symbol_code + deal_time 排序。"""
    table = f"`{ACCOUNT_ID}_{STRATEGY_ID}_deal`"
    rows = db.fetch_all(
        f"SELECT * FROM {table} ORDER BY symbol_code, deal_time, deal_id",
        (),
    )
    return rows


def build_trades(deals: list[dict]) -> list[dict]:
    """将成交配对为完整交易记录。

    每个 symbol_code 的成交按时间排序，依次匹配 open(1) → close(2)。
    """
    by_symbol: dict[str, list[dict]] = defaultdict(list)
    for d in deals:
        by_symbol[d["symbol_code"]].append(d)

    trades: list[dict] = []
    for symbol, rows in by_symbol.items():
        open_deal = None
        for d in rows:
            if d["deal_type"] == 1:   # 开仓
                open_deal = d
            elif d["deal_type"] == 2 and open_deal is not None:  # 平仓
                trades.append(_make_trade(open_deal, d))
                open_deal = None  # 等下一轮开仓

    return trades


def _make_trade(open_: dict, close: dict) -> dict:
    """根据一对开仓/平仓成交计算 trade 全部字段。"""
    open_qty = Decimal(str(open_["deal_quantity"]))
    open_price = Decimal(str(open_["deal_price"]))
    close_price = Decimal(str(close["deal_price"]))
    open_amount = Decimal(str(open_["deal_amount"]))
    close_amount = Decimal(str(close["deal_amount"]))

    realized_pnl = close_amount - open_amount  # 做多：平仓额 - 开仓额
    return_rate = (close_price - open_price) / open_price if open_price > ZERO else ZERO
    commission = Decimal(str(open_["commission"])) + Decimal(str(close["commission"]))

    return {
        "market_id": open_["market_id"],
        "account_id": open_["account_id"],
        "strategy_id": open_["strategy_id"],
        "symbol_code": open_["symbol_code"],
        "symbol_name": open_["symbol_name"] or "",
        "asset_type": open_["asset_type"],
        "direction": open_["direction"],
        "open_time": open_["deal_time"],
        "close_time": close["deal_time"],
        "open_price": open_price,
        "close_price": close_price,
        "open_quantity": open_qty,
        "open_amount": open_amount,
        "realized_pnl": realized_pnl,
        "return_rate": return_rate,
        "commission": commission,
    }


def insert_trades(db: Database, trades: list[dict]) -> int:
    """批量写入 trade 表，返回写入行数。"""
    if not trades:
        return 0

    table = f"`{ACCOUNT_ID}_{STRATEGY_ID}_trade`"
    sql = (
        f"INSERT INTO {table} "
        f"(market_id, account_id, strategy_id, symbol_code, symbol_name, "
        f"asset_type, direction, open_time, close_time, "
        f"open_price, close_price, open_quantity, open_amount, "
        f"realized_pnl, return_rate, commission) "
        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, "
        f"%s, %s, %s, %s, %s, %s, %s)"
    )

    count = 0
    for t in trades:
        db.execute(sql, (
            t["market_id"], t["account_id"], t["strategy_id"],
            t["symbol_code"], t["symbol_name"], t["asset_type"],
            t["direction"],
            t["open_time"], t["close_time"],
            t["open_price"], t["close_price"],
            t["open_quantity"], t["open_amount"],
            t["realized_pnl"], t["return_rate"], t["commission"],
        ))
        count += 1
        if count % 20 == 0:
            db.commit()
    db.commit()
    return count


# ── 主流程 ──────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Deal → Trade 生成工具")
    print(f"  account_id  = {ACCOUNT_ID}")
    print(f"  strategy_id = {STRATEGY_ID}")
    print()

    print("1️⃣  连接数据库...")
    db = Database(DB_CONFIG)
    db.connect()
    print("    ✅ 已连接")

    try:
        # 2. 确保 deal 和 trade 表存在
        print("2️⃣  确保表结构存在...")
        sm = SchemaManager(db)
        sm.create_tables(ACCOUNT_ID, STRATEGY_ID)
        print("    ✅ operation / deal / trade 表已就绪")

        # 3. 检查 deal 表是否有数据，为空则从 CSV 导入
        deal_table = f"`{ACCOUNT_ID}_{STRATEGY_ID}_deal`"
        row = db.fetch_one(f"SELECT COUNT(*) AS cnt FROM {deal_table}", ())
        deal_count = row["cnt"] if row else 0

        if deal_count == 0:
            print("3️⃣  deal 表为空，从 CSV 导入...")
            if not os.path.exists(DEAL_CSV):
                print(f"    ❌ 找不到 {DEAL_CSV}，中止")
                return
            deal_rows = load_deal_csv(DEAL_CSV)
            print(f"    读取 {len(deal_rows)} 条成交记录")
            imported = import_deal_csv(db, deal_rows)
            print(f"    ✅ 导入 {imported} 行到 {deal_table}")
        else:
            print(f"3️⃣  deal 表已有 {deal_count} 条记录，跳过 CSV 导入")

        # 4. 读取 deal 数据
        print("4️⃣  读取成交记录...")
        deals = fetch_deals(db)
        print(f"    ✅ {len(deals)} 条")

        # 5. 配对生成 trade
        print("5️⃣  配对生成完整交易...")
        trades = build_trades(deals)
        print(f"    ✅ {len(trades)} 笔")

        if not trades:
            print("\n⚠️  无交易可生成，请检查 deal 数据")
            return

        # 6. 写入 trade 表（先清空旧数据防重复）
        trade_table = f"`{ACCOUNT_ID}_{STRATEGY_ID}_trade`"
        print("6️⃣  写入 trade 表...")
        db.execute(f"DELETE FROM {trade_table}", ())
        print("    已清空旧 trade 记录")
        inserted = insert_trades(db, trades)
        print(f"    ✅ 写入 {inserted} 行到 {trade_table}")

        # 7. 验证
        row = db.fetch_one(
            f"SELECT COUNT(*) AS cnt FROM {trade_table}", ()
        )
        total = row["cnt"] if row else 0
        print(f"\n{'='*60}")
        print(f"  ✅ 完成！ggt_marsi_trade 表现有 {total} 条记录")
        print(f"  📊 涉及 {len(set(t['symbol_code'] for t in trades))} 只标的")
        print(f"  📅 时间范围: {trades[0]['open_time']} ~ {trades[-1]['close_time']}")

    except Exception:
        print("\n❌ 发生错误，回滚中...")
        db.cnx.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
