"""
将 CSV 历史数据导入数据库表。

- id_fortuna_history_profit1.csv  →  {account}_asset
- site_id_marsi_predict_ope2.csv   →  {account}_{strategy}_operation

用法：
  python -m infrastructure.scripts.import_csv_data
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime
from decimal import Decimal, ROUND_DOWN

# ── 路径处理 ────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PACKAGE_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))  # → backend/
_PROJECT_ROOT = os.path.abspath(os.path.join(_PACKAGE_ROOT, ".."))     # → Transwin_0625/

if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)

from infrastructure.db.connection import Database, DatabaseConfig
from infrastructure.db.schema_manager import SchemaManager

# ── 配置 ────────────────────────────────────────────────────────────
ACCOUNT_ID = "ggt"
STRATEGY_ID = "marsi"
MARKET_ID = 2
MAX_HOLDINGS = 15

# CSV 文件路径（位于项目根目录 Transwin_0625/）
PROFIT_CSV = os.path.join(_PROJECT_ROOT, "id_fortuna_history_profit1.csv")
OPERATION_CSV = os.path.join(_PROJECT_ROOT, "site_id_marsi_predict_ope2.csv")

# 数据库配置
DB_CONFIG = DatabaseConfig(
    host="192.16.1.112",
    port=3306,
    user="root",
    password="",
    database="strategy_system",
)


# ── CSV 读取 ────────────────────────────────────────────────────────

def _parse_date(s: str) -> datetime:
    return datetime.strptime(s.strip(), "%Y-%m-%d")


def load_profit_csv(path: str) -> list[dict]:
    """读取 profit CSV，返回按 date 排序的行列表。"""
    rows: list[dict] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            date_str = row["date"].strip()
            if not date_str:
                continue
            rows.append({
                "date": _parse_date(date_str),
                "total_money": Decimal(row["total_money"].strip()),
                "hold_stock_money": Decimal(row["hold_stock_money"].strip()),
                "cash_money": Decimal(row["cash_money"].strip()),
            })
    rows.sort(key=lambda r: r["date"])
    return rows


def load_operation_csv(path: str) -> list[dict]:
    """读取 operation CSV，只保留 buyorsell=1 或 -1，按 ope_date 排序。"""
    rows: list[dict] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            buyorsell = row["buyorsell"].strip()
            if buyorsell not in ("1", "-1"):
                continue
            ope_date = row["ope_date"].strip()
            if not ope_date:
                continue
            # 跳过无法获取成交价的记录
            op_succ_raw = row["operation_succ"].strip()
            if op_succ_raw == "no_price":
                continue
            rows.append({
                "id": int(row["id"].strip()),
                "buyorsell": int(buyorsell),
                "ope_date": _parse_date(ope_date),
                "stockno": row["stockno"].strip(),
                "price": Decimal(row["price"].strip()) if row["price"].strip() else Decimal("0"),
                "operation_succ": int(op_succ_raw) if op_succ_raw else 0,
            })
    rows.sort(key=lambda r: r["ope_date"])
    return rows


# ── 数据转换 ────────────────────────────────────────────────────────

def compute_asset_rows(profit_rows: list[dict]) -> list[dict]:
    """将 profit 数据转换为 asset 表行，net_value 从 1.0 开始按总资产变化率累乘。"""
    asset_rows: list[dict] = []
    prev_net_value = Decimal("1.0")

    for i, row in enumerate(profit_rows):
        if i == 0:
            net_value = Decimal("1.0")
        else:
            ratio = row["total_money"] / profit_rows[i - 1]["total_money"]
            net_value = prev_net_value * ratio

        asset_rows.append({
            "created_at": row["date"],
            "market_id": MARKET_ID,
            "account_id": ACCOUNT_ID,
            "total_asset": row["total_money"],
            "net_value": net_value,
            "market_value": row["hold_stock_money"],
            "cash_balance": row["cash_money"],
        })
        prev_net_value = net_value

    return asset_rows


def build_asset_date_index(asset_rows: list[dict]) -> dict[str, Decimal]:
    """按日期（yyyy-mm-dd）索引 total_asset，供 operation 查询。"""
    return {r["created_at"].strftime("%Y-%m-%d"): r["total_asset"] for r in asset_rows}


def compute_operation_rows(
    op_rows: list[dict],
    asset_by_date: dict[str, Decimal],
) -> list[dict]:
    """将 operation 数据转换为 DB 行，quantity 按 (total_asset/15)/price 计算。"""
    db_rows: list[dict] = []
    buy_quantity: dict[str, Decimal] = {}  # stockno → 上次买入的 quantity
    skip_buy = 0
    skip_sell = 0

    for op in op_rows:
        date_key = op["ope_date"].strftime("%Y-%m-%d")
        total_asset = asset_by_date.get(date_key)
        if total_asset is None:
            print(f"  ⚠️  {date_key} {op['stockno']}: 找不到对应日期的 total_asset，跳过")
            continue

        stockno = op["stockno"]

        if op["buyorsell"] == 1:  # 买入
            if op["price"] == 0:
                skip_buy += 1
                continue
            quantity = (
                (total_asset / Decimal(str(MAX_HOLDINGS)) / op["price"])
                .to_integral_value(rounding=ROUND_DOWN)
            )
            buy_quantity[stockno] = quantity
        else:  # 卖出
            quantity = buy_quantity.pop(stockno, None)
            if quantity is None:
                skip_sell += 1
                continue

        db_rows.append({
            "market_id": MARKET_ID,
            "account_id": ACCOUNT_ID,
            "strategy_id": STRATEGY_ID,
            "symbol_code": stockno,
            "symbol_name": "",
            "asset_type": 1,
            "operation_type": 1 if op["buyorsell"] == 1 else 2,
            "direction": 1,
            "order_type": 1,
            "price": op["price"],
            "quantity": quantity,
            "created_at": op["ope_date"],
            "status": 1 if op["operation_succ"] == 1 else 0,
        })

    if skip_buy:
        print(f"  ⚠️  跳过了 {skip_buy} 条买入（price 为 0）")
    if skip_sell:
        print(f"  ⚠️  跳过了 {skip_sell} 条卖出（找不到对应的买入记录）")

    return db_rows


# ── 数据库写入 ──────────────────────────────────────────────────────

def insert_assets(db: Database, rows: list[dict]) -> None:
    """批量写入 asset 表。"""
    table = f"`{ACCOUNT_ID}_asset`"
    sql = (
        f"INSERT INTO {table} "
        f"(created_at, market_id, account_id, total_asset, net_value, "
        f"market_value, cash_balance) "
        f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    count = 0
    for r in rows:
        db.execute(sql, (
            r["created_at"],
            r["market_id"],
            r["account_id"],
            r["total_asset"],
            r["net_value"],
            r["market_value"],
            r["cash_balance"],
        ))
        count += 1
        if count % 50 == 0:
            db.commit()
    db.commit()
    print(f"  ✅ 写入 {count} 行到 {table}")


def insert_operations(db: Database, rows: list[dict]) -> None:
    """批量写入 operation 表。"""
    table = f"`{ACCOUNT_ID}_{STRATEGY_ID}_operation`"
    sql = (
        f"INSERT INTO {table} "
        f"(market_id, account_id, strategy_id, symbol_code, symbol_name, "
        f"asset_type, operation_type, direction, order_type, price, quantity, "
        f"created_at, status) "
        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    count = 0
    for r in rows:
        db.execute(sql, (
            r["market_id"],
            r["account_id"],
            r["strategy_id"],
            r["symbol_code"],
            r["symbol_name"],
            r["asset_type"],
            r["operation_type"],
            r["direction"],
            r["order_type"],
            r["price"],
            r["quantity"],
            r["created_at"],
            r["status"],
        ))
        count += 1
        if count % 50 == 0:
            db.commit()
    db.commit()
    print(f"  ✅ 写入 {count} 行到 {table}")


# ── 建表 ────────────────────────────────────────────────────────────

def ensure_tables(db: Database) -> None:
    """如不存在则创建 7 张表。"""
    sm = SchemaManager(db)
    sm.create_all(ACCOUNT_ID, STRATEGY_ID)
    sm.create_asset_table(ACCOUNT_ID)
    sm.create_report_table(ACCOUNT_ID)
    print("  ✅ 表已就绪")


# ── 主入口 ──────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  CSV 历史数据导入")
    print(f"  account_id  = {ACCOUNT_ID}")
    print(f"  strategy_id = {STRATEGY_ID}")
    print(f"  CSV 目录     = {_PROJECT_ROOT}")
    print()

    # 1. 读取 CSV
    print("1️⃣  读取 profit CSV...")
    profit_rows = load_profit_csv(PROFIT_CSV)
    date_range = (
        f"{profit_rows[0]['date'].strftime('%Y-%m-%d')}"
        f" ~ {profit_rows[-1]['date'].strftime('%Y-%m-%d')}"
    )
    print(f"    {len(profit_rows)} 行 ({date_range})")

    print("2️⃣  读取 operation CSV...")
    op_rows = load_operation_csv(OPERATION_CSV)
    op_date_range = (
        f"{op_rows[0]['ope_date'].strftime('%Y-%m-%d')}"
        f" ~ {op_rows[-1]['ope_date'].strftime('%Y-%m-%d')}"
    )
    print(f"    {len(op_rows)} 条有效操作 ({op_date_range})")

    # 2. 转换
    print("3️⃣  转换 asset 数据...")
    asset_rows = compute_asset_rows(profit_rows)
    asset_by_date = build_asset_date_index(asset_rows)
    print(f"    {len(asset_rows)} 行")

    print("4️⃣  转换 operation 数据...")
    op_db_rows = compute_operation_rows(op_rows, asset_by_date)
    print(f"    {len(op_db_rows)} 行")

    # 3. 连接数据库
    print("5️⃣  连接数据库...")
    db = Database(DB_CONFIG)
    db.connect()
    print("    已连接")

    try:
        # 4. 建表
        print("6️⃣  检查/创建表...")
        ensure_tables(db)

        # 5. 写入
        print("7️⃣  写入 asset 表...")
        insert_assets(db, asset_rows)

        print("8️⃣  写入 operation 表...")
        insert_operations(db, op_db_rows)

    except Exception:
        print("❌ 发生错误，回滚中...")
        db.cnx.rollback()
        raise
    finally:
        db.close()

    print()
    print("✅ 全部导入完成！")
    print(f"   {ACCOUNT_ID}_asset         : {len(asset_rows)} 行")
    print(f"   {ACCOUNT_ID}_{STRATEGY_ID}_operation : {len(op_db_rows)} 行")


if __name__ == "__main__":
    main()
