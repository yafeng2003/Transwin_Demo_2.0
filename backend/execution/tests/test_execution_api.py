"""执行层 API 测试。

验证 FastAPI 端点响应结构，确保前端依赖的基础字段稳定。
"""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from main import app


def test_health_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "running"


def test_manual_buy_response_shape():
    client = TestClient(app)

    response = client.post(
        "/api/v1/manual/buy",
        json={
            "marketId": 2,
            "accountId": "acc_main",
            "symbolCode": "HK.00700",
            "orderType": 1,
            "quantity": 100,
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "submitted"


def test_orders_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/orders")

    assert response.status_code == 200
    assert "list" in response.json()["data"]


def test_dashboard_asset_summary_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/dashboard/asset-summary", params={"market_id": 1, "account_id": "acc_main"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert "totalAsset" in data
    assert "todayPnl" in data


def test_dashboard_position_overview_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/dashboard/position-overview", params={"market_id": 1, "account_id": "acc_main"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert "positions" in data
    assert "totalMarketValue" in data


def test_orders_accept_frontend_filters():
    client = TestClient(app)

    response = client.get(
        "/api/v1/orders",
        params={
            "market_id": 2,
            "account_id": "acc_main",
            "strategy_id": "manual",
            "status": 1,
            "symbol": "HK.00700",
        },
    )

    assert response.status_code == 200
    assert "list" in response.json()["data"]


def test_deals_accept_frontend_filters():
    client = TestClient(app)

    response = client.get(
        "/api/v1/deals",
        params={
            "market_id": 2,
            "account_id": "acc_main",
            "strategy_id": "manual",
            "date_range": "2026-06-01,2026-06-30",
        },
    )

    assert response.status_code == 200
    assert "list" in response.json()["data"]


def test_system_logs_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/logs/system", params={"level": "ERROR", "page": 1, "size": 20})

    assert response.status_code == 200
    assert "list" in response.json()["data"]


def test_manual_modify_order_uses_account_id():
    client = TestClient(app)

    response = client.post(
        "/api/v1/manual/modify-order",
        json={"orderId": "MOCK-1", "accountId": "acc_main", "price": 46},
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "modified"
