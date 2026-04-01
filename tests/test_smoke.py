"""Integration smoke tests (requires: pip install -r requirements-dev.txt)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_rbac_viewer_cannot_list_records() -> None:
    t = client.post(
        "/api/auth/token",
        data={"username": "viewer@example.com", "password": "viewer12345"},
    ).json()["access_token"]
    r = client.get("/api/records", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 403


def test_viewer_can_dashboard() -> None:
    t = client.post(
        "/api/auth/token",
        data={"username": "viewer@example.com", "password": "viewer12345"},
    ).json()["access_token"]
    r = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 200
    body = r.json()
    assert "total_income" in body
    assert "weekly_trends" in body
