"""Main app frontend analysis endpoint tests."""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from main import app


def test_frontend_analysis_returns_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/analysis/returns", params={"market_id": 1, "account_id": "acc_main"})

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert "summary" in body["data"]
    assert "dailyReturns" in body["data"]
    assert "navSeries" in body["data"]
    assert "drawdownSeries" in body["data"]
    assert "monthlyReturns" in body["data"]
    assert "dailyReturnDist" in body["data"]
    assert "annualReturns" in body["data"]
    assert "volatility" in body["data"]["summary"]


def test_frontend_analysis_risk_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/analysis/risk", params={"market_id": 1, "account_id": "acc_main"})

    assert response.status_code == 200
    assert "volatility" in response.json()["data"]


def test_frontend_analysis_trading_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/analysis/trading", params={"market_id": 1, "account_id": "acc_main"})

    assert response.status_code == 200
    assert "tradeCount" in response.json()["data"]


def test_frontend_analysis_strategy_response_shape():
    client = TestClient(app)

    response = client.get("/api/v1/analysis/strategy", params={"market_id": 1, "account_id": "acc_main"})

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
