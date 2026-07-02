"""为 ggt_marsi 生成模拟风险事件通知数据，写入 risk_event 和 notification 表。

数据基于成交和资产 CSV 的上下文（时间范围、标的代码），大部分为轻微事件。

用法：
  cd backend
  python -m infrastructure.scripts.seed_risk_data
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PACKAGE_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)

from infrastructure.db.connection import Database, DatabaseConfig
from infrastructure.db.schema_manager import SchemaManager
from infrastructure.db.naming import table_name, SUFFIX_NOTIFICATION, SUFFIX_RISK_EVENT

ACCOUNT_ID = "ggt"
STRATEGY_ID = "marsi"

DB_CONFIG = DatabaseConfig(
    host="192.16.1.112",
    port=3306,
    user="root",
    password="",
    database="strategy_system",
)

# 成交 CSV 中出现的真实标的
SYMBOLS = [
    "00005", "00027", "00285", "00288", "00358", "00688", "00763",
    "00836", "00857", "00902", "00914", "00939", "01060", "01177",
    "01276", "01299", "01339", "01378", "01766", "01776", "01788",
    "02020", "02050", "02097", "02313", "02331", "02498", "02628",
    "03330", "03988", "03993", "06613", "06690", "06862", "09868",
    "09973",
]


def ensure_tables(db: Database) -> None:
    """确保 risk_event 和 notification 表存在。"""
    sm = SchemaManager(db)
    sm.create_tables(ACCOUNT_ID, STRATEGY_ID)


def insert_risk_events(db: Database) -> int:
    """插入 10 条轻微风险事件。"""
    table = table_name(ACCOUNT_ID, SUFFIX_RISK_EVENT, STRATEGY_ID)

    events = [
        # event_type, event_level, symbol_code, message, occur_time, status
        ("api_timeout",        1, "00005", "Futu API 查询行情超时，自动重连成功，耗时 2.3s",                                       datetime(2026, 1, 28, 9, 45, 0),  "resolved"),
        ("order_delay",        1, "00027", "下单指令队列积压，延迟 1.8s 后提交至交易所，已正常成交",                                  datetime(2026, 2, 10, 10, 12, 0), "resolved"),
        ("slippage_warning",   2, "00285", "卖出滑点超过 15bps，委托价 29.80，成交价 29.72，偏差约 0.27%",                          datetime(2026, 3, 4, 14, 30, 0),  "resolved"),
        ("api_error",          1, None,    "Futu API 返回频率限制警告，调整请求间隔后恢复",                                          datetime(2026, 3, 15, 11, 0, 0),  "resolved"),
        ("drawdown",           2, None,    "策略 marsi 当日净值回撤 -2.1%，低于 -3.0% 预警线，当前处于正常范围",                      datetime(2026, 4, 10, 15, 30, 0), "resolved"),
        ("consecutive_loss",   1, "01060", "标的 01060 连续 2 笔亏损，累计 -¥98,430，建议关注持仓",                                 datetime(2026, 4, 25, 16, 0, 0),  "resolved"),
        ("daily_loss",         2, None,    "当日累计亏损 ¥87,220，占账户资产 0.6%，未触发阈值 ¥500,000",                          datetime(2026, 5, 6, 15, 45, 0),  "resolved"),
        ("modify_failed",      1, "00857", "改单请求因订单已部分成交被拒绝，不影响已有仓位",                                        datetime(2026, 5, 15, 10, 22, 0), "resolved"),
        ("timeout",            1, None,    "资产净值同步任务重试 1 次后成功，延后 5 分钟更新",                                      datetime(2026, 6, 1, 8, 30, 0),   "resolved"),
        ("api_error",          2, "00288", "Futu API 返回限价错误（错误码 30010），多账户并发冲突，自动修正参数后重新下单成功",      datetime(2026, 6, 12, 13, 15, 0), "resolved"),
    ]

    sql = (
        f"INSERT INTO {table} "
        f"(event_type, account_id, strategy_id, symbol_code, event_level, "
        f"event_message, occur_time, status) "
        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    count = 0
    for e_type, e_level, sym, msg, o_time, status in events:
        db.execute(sql, (e_type, ACCOUNT_ID, STRATEGY_ID, sym, e_level, msg, o_time, status))
        count += 1
    db.commit()
    return count


def insert_notifications(db: Database) -> int:
    """插入 10 条与风险事件对应的通知记录。"""
    table = table_name(ACCOUNT_ID, SUFFIX_NOTIFICATION, STRATEGY_ID)

    notifications = [
        # notification_type, risk_level, title, content, created_at, is_read, risk_event_id
        ("risk_alert",      1, "API 超时已恢复",                "Futu API 查询行情超时，自动重连成功，耗时 2.3s，交易未受影响",                                    datetime(2026, 1, 28, 9, 46, 0),  0, 1),
        ("risk_alert",      1, "下单延迟",                      "下单指令队列积压 1.8s，已正常提交至交易所，订单已全部成交",                                     datetime(2026, 2, 10, 10, 14, 0), 0, 2),
        ("risk_alert",      2, "卖出滑点偏高",                  "00285 卖出成交价 29.72，委托价 29.80，滑点 -0.27%（15.7bps），在可接受范围内",                 datetime(2026, 3, 4, 14, 32, 0),  0, 3),
        ("anomaly",         1, "API 频率限制",                  "Futu API 触发请求频率限制，系统自动调整间隔后恢复正常，不影响后续交易",                           datetime(2026, 3, 15, 11, 2, 0),  0, 4),
        ("risk_alert",      2, "净值回撤预警",                  "策略 marsi 当日净值回撤 -2.1%，距 -3.0% 预警线仍有安全空间，当前处于正常监控范围",                datetime(2026, 4, 10, 15, 35, 0), 0, 5),
        ("anomaly",         1, "连续亏损提醒",                  "标的 01060 连续 2 笔亏损，累计 -¥98,430。该标的持仓占比 3.2%，建议关注后续走势",                  datetime(2026, 4, 25, 16, 5, 0),  0, 6),
        ("risk_alert",      1, "当日亏损提醒",                  "当日累计亏损 ¥87,220（占比 0.6%），远低于 ¥500,000 阈值，无需处理",                              datetime(2026, 5, 6, 15, 50, 0),  0, 7),
        ("risk_alert",      1, "改单失败提示",                  "00857 改单请求因订单已部分成交被拒，原订单正常执行，无需补单",                                    datetime(2026, 5, 15, 10, 25, 0), 0, 8),
        ("anomaly",         1, "同步延迟通知",                  "资产净值同步任务重试 1 次后成功（延迟 5 分钟），数据已于 08:35 更新至最新",                      datetime(2026, 6, 1, 8, 35, 0),   0, 9),
        ("risk_alert",      2, "Futu API 参数错误",             "限价单参数错误（错误码 30010），系统已自动修正参数并重新下单，成交正常",                           datetime(2026, 6, 12, 13, 18, 0), 1, 10),
    ]

    sql = (
        f"INSERT INTO {table} "
        f"(notification_type, risk_level, title, content, created_at, "
        f"is_read, risk_event_id, send_status) "
        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    count = 0
    for n_type, r_level, title, content, created, is_read, event_id in notifications:
        db.execute(sql, (n_type, r_level, title, content, created, is_read, event_id, "sent"))
        count += 1
    db.commit()
    return count


def main() -> None:
    print("=" * 60)
    print("  生成模拟风控数据")
    print(f"  account  = {ACCOUNT_ID}")
    print(f"  strategy = {STRATEGY_ID}")
    print()

    print("1️⃣  连接数据库...")
    db = Database(DB_CONFIG)
    db.connect()
    print("    ✅ 已连接")

    try:
        print("2️⃣  确保表存在...")
        ensure_tables(db)
        print("    ✅ 表已就绪")

        print("3️⃣  清空旧数据...")
        risk_table = table_name(ACCOUNT_ID, SUFFIX_RISK_EVENT, STRATEGY_ID)
        notif_table = table_name(ACCOUNT_ID, SUFFIX_NOTIFICATION, STRATEGY_ID)
        db.execute(f"DELETE FROM {risk_table}", ())
        db.execute(f"DELETE FROM {notif_table}", ())
        db.commit()
        print("    ✅ 已清空")

        print("4️⃣  插入风险事件...")
        ec = insert_risk_events(db)
        print(f"    ✅ 写入 {ec} 条到 {risk_table}")

        print("5️⃣  插入通知...")
        nc = insert_notifications(db)
        print(f"    ✅ 写入 {nc} 条到 {notif_table}")

        print(f"\n{'='*60}")
        print(f"  ✅ 完成！")
        print(f"  ⚠️  risk_event     = {ec} 条")
        print(f"  🔔  notification   = {nc} 条")
        print()
        print("  风险事件类型分布：")
        for et in ["api_timeout", "order_delay", "slippage_warning", "api_error",
                    "drawdown", "consecutive_loss", "daily_loss", "modify_failed", "timeout"]:
            print(f"    - {et}")

    except Exception as e:
        print(f"\n❌ 错误：{e}")
        db.cnx.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
