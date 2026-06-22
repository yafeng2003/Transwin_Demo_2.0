"""风控 API 测试。

验证风险事件和风险概览端点的响应结构。
"""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from main import app


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
