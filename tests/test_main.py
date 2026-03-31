import os
import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MAINLAYER_API_KEY", "test-key")
os.environ.setdefault("MAINLAYER_RESOURCE_ID", "test-resource")


def _make_app():
    with patch("mainlayer.MainlayerClient"):
        from src.main import app
        return app


@pytest.fixture()
def authorized_client():
    app = _make_app()

    access_mock = MagicMock()
    access_mock.authorized = True

    with patch("src.main.ml") as ml_mock:
        ml_mock.resources.verify_access = AsyncMock(return_value=access_mock)
        with TestClient(app) as client:
            yield client, ml_mock


@pytest.fixture()
def unauthorized_client():
    app = _make_app()

    access_mock = MagicMock()
    access_mock.authorized = False

    with patch("src.main.ml") as ml_mock:
        ml_mock.resources.verify_access = AsyncMock(return_value=access_mock)
        with TestClient(app) as client:
            yield client, ml_mock


def test_health():
    app = _make_app()
    with TestClient(app) as client:
        resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_generate_authorized(authorized_client):
    client, _ = authorized_client
    resp = client.post(
        "/generate",
        json={"prompt": "A cat", "width": 64, "height": 64, "format": "png"},
        headers={"x-mainlayer-token": "valid-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "image_b64" in data
    assert data["credits_used"] == 1
    # Verify it is valid base64
    decoded = base64.b64decode(data["image_b64"])
    assert len(decoded) > 0


def test_generate_unauthorized(unauthorized_client):
    client, _ = unauthorized_client
    resp = client.post(
        "/generate",
        json={"prompt": "A cat", "width": 64, "height": 64, "format": "png"},
        headers={"x-mainlayer-token": "bad-token"},
    )
    assert resp.status_code == 402


def test_generate_missing_token():
    app = _make_app()
    with TestClient(app) as client:
        resp = client.post(
            "/generate",
            json={"prompt": "A cat"},
        )
    assert resp.status_code == 422


def test_generate_invalid_format(authorized_client):
    client, _ = authorized_client
    resp = client.post(
        "/generate",
        json={"prompt": "A cat", "format": "bmp"},
        headers={"x-mainlayer-token": "valid-token"},
    )
    assert resp.status_code == 400


def test_generate_invalid_dimensions(authorized_client):
    client, _ = authorized_client
    resp = client.post(
        "/generate",
        json={"prompt": "A cat", "width": 10, "height": 10},
        headers={"x-mainlayer-token": "valid-token"},
    )
    assert resp.status_code == 400
