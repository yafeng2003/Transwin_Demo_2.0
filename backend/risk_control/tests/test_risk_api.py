"""风控 API 测试。

验证风险事件和风险概览端点的响应结构。
"""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from common.models import RiskEvent
from main import app
from main import risk_service


def test_risk_events_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/risk/events")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert "list" in body["data"]


def test_risk_overview_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/risk/overview")

    assert response.status_code == 200
    assert "riskLevel" in response.json()["data"]


def test_resolve_risk_event_response_shape():
    client = TestClient(app)
    event_response = client.post(
        "/api/v1/manual/buy",
        json={
            "marketId": 1,
            "accountId": "acc_main",
            "symbolCode": "HK.00700",
            "orderType": 1,
            "quantity": 100,
        },
    )
    assert event_response.status_code == 200

    import anyio

    risk_event = anyio.run(
        risk_service.handle_risk_event,
        RiskEvent(
            event_type="order_failed",
            account_id="acc_main",
            strategy_id="manual",
            symbol_code="HK.00700",
            event_level=2,
            event_message="下单失败",
        ),
    )
    response = client.post("/api/v1/risk/events/resolve", json={"id": risk_event.risk_event_id})

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "resolved"
