import pytest

pytestmark = pytest.mark.db


def test_login_rate_limiting_blocks_after_threshold(client):
    """Verifica que tras exceder el límite de peticiones por minuto en /login, se devuelva 429."""
    for i in range(10):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": f"brute_{i}@test.com", "password": "wrong"},
        )
        assert res.status_code == 401

    blocked_res = client.post(
        "/api/v1/auth/login",
        json={"email": "brute_11@test.com", "password": "wrong"},
    )
    assert blocked_res.status_code == 429
    body = blocked_res.json()
    assert "Demasiadas peticiones" in body["detail"]
    assert "Retry-After" in blocked_res.headers
