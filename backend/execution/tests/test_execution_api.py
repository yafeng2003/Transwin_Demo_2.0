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
