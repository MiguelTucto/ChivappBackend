import os

import httpx
import pytest

SMOKE_BASE_URL = os.environ.get("SMOKE_BASE_URL")

pytestmark = pytest.mark.skipif(
    not SMOKE_BASE_URL,
    reason="define SMOKE_BASE_URL para correr smoke tests contra un ambiente real (staging/producción)",
)


def test_health_endpoint_is_up():
    response = httpx.get(f"{SMOKE_BASE_URL}/health", timeout=10)
    assert response.status_code == 200
    assert response.json().get("status") == "ok"


def test_public_musicians_listing_is_reachable():
    response = httpx.get(f"{SMOKE_BASE_URL}/api/v1/profiles/musicians", timeout=10)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
