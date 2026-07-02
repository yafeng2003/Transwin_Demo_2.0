"""手动生成日报，可在服务器上直接执行。

用法：
  cd backend
  python -m data_analysis.scripts.generate_report

生成后可通过 GET /api/v1/reports/{report_id}/export?format=pdf 下载。
"""

from __future__ import annotations

import asyncio
import sys
import os
from datetime import date, timedelta

# 把 backend/ 加入 sys.path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PACKAGE_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)

from infrastructure.db.connection import Database, DatabaseConfig
from infrastructure.db.repositories.execution_db_repository import ExecutionDbRepository
from infrastructure.db.repositories.report_metadata_repo import ReportFileStoreImpl
from data_analysis.config import AnalysisConfig
from data_analysis.services.report.report_service import ReportService

# ── 参数配置（按需修改） ──────────────────────────────────────────────
MARKET_ID = 2        # 港股
ACCOUNT_ID = "ggt"
STRATEGY_ID = "marsi"
DAYS_BACK = 30       # 往前生成多少天
FILE_FORMATS = ["pdf", "xlsx", "csv"]  # 同时生成三种格式

# 数据库配置（与 main.py 一致）
DB_CONFIG = DatabaseConfig(
    host="192.16.1.112",
    port=3306,
    user="root",
    password="",
    database="strategy_system",
)


async def main() -> None:
    print("=" * 60)
    print("  批量生成日报")
    print(f"  account  = {ACCOUNT_ID}")
    print(f"  strategy = {STRATEGY_ID}")
    print(f"  天数     = 最近 {DAYS_BACK} 天")
    print(f"  formats  = {FILE_FORMATS}")
    print()

    print("1️⃣  连接数据库...")
    db = Database(DB_CONFIG)
    db.connect()
    print("    ✅ 已连接")

    try:
        print("2️⃣  装配依赖...")
        repo = ExecutionDbRepository(db)
        store = ReportFileStoreImpl(db)
        config = AnalysisConfig()
        service = ReportService(
            asset_repository=repo,
            trade_repository=repo,
            deal_repository=repo,
            report_store=store,
            config=config,
        )
        print("    ✅ ReportService 已就绪")
        print()

        today = date.today()
        total_ok = 0
        total_fail = 0

        for i in range(DAYS_BACK):
            day = today - timedelta(days=i)
            for fmt in FILE_FORMATS:
                try:
                    result = await service.generate_daily_report(
                        market_id=MARKET_ID,
                        account_id=ACCOUNT_ID,
                        strategy_id=STRATEGY_ID,
                        day=day,
                        file_format=fmt,
                    )
                    print(f"  ✅ {day}  ({fmt}) → report_id={result.report_id}")
                    total_ok += 1
                except Exception as e:
                    print(f"  ❌ {day}  ({fmt}) → {e}")
                    total_fail += 1

        print(f"\n{'='*60}")
        print(f"  批量生成完成！成功 {total_ok} 条，失败 {total_fail} 条")
        print(f"  可到前端报表中心查看，或通过")
        print(f"  GET /api/v1/reports?type=daily&account_id={ACCOUNT_ID}  查询")

    except Exception as e:
        print(f"\n❌ 初始化失败：{e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
