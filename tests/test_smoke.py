"""Integration smoke tests (requires: pip install -r requirements-dev.txt)."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_rbac_viewer_can_list_records() -> None:
    t = client.post(
        "/api/auth/token",
        data={"username": "viewer@example.com", "password": "viewer12345"},
    ).json()["access_token"]
    r = client.get("/api/records", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 200


def test_viewer_cannot_dashboard() -> None:
    t = client.post(
        "/api/auth/token",
        data={"username": "viewer@example.com", "password": "viewer12345"},
    ).json()["access_token"]
    r = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 403
