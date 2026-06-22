
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from main import app

    return TestClient(app)


class TestRiskAPI:

    def test_list_risk_events(self, client):
        resp = client.get("/api/v1/risk/events")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_risk_events_with_filters(self, client):
        resp = client.get(
            "/api/v1/risk/events",
            params={"account_id": "acc_001", "min_level": 3},
        )
        assert resp.status_code == 200

    def test_risk_summary(self, client):
        resp = client.get("/api/v1/risk/events/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_events" in data
        assert "alert_count" in data
        assert "critical_count" in data

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
