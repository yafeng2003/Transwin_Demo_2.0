"""Main app report endpoint smoke tests."""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from main import app


def test_main_reports_route_is_mounted():
    client = TestClient(app)

    response = client.get("/api/v1/reports", params={"type": "daily"})

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert isinstance(body["data"], list)
