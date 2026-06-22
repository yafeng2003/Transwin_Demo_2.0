
from fastapi import FastAPI

from common.interfaces.risk_interface import RiskEventHandler
from execution.services.order_executor import OrderExecutor
from risk_control.services.risk_service import RiskEventServiceImpl

from risk_control.api.risk_controller import router as risk_router

app = FastAPI(
    title="量化交易系统后端",
    version="1.0.0",
    description="支持策略生成、订单执行、风控监控、数据分析的量化交易平台",
)


risk_event_handler: RiskEventHandler = RiskEventServiceImpl()

order_executor = OrderExecutor(risk_handler=risk_event_handler)


print("[OK] 依赖注入组装完成")
print(f"  OrderExecutor.risk_handler = {type(order_executor._risk_handler).__name__}")


app.include_router(risk_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
