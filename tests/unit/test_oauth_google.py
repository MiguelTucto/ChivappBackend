from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.services.oauth import (
    OAuthProfile,
    build_authorize_url,
    verify_google_id_token,
)


client = TestClient(app)


def test_oauth_start_google_not_configured_redirects():
    with patch.object(settings, "GOOGLE_CLIENT_ID", None), patch.object(
        settings, "GOOGLE_CLIENT_SECRET", None
    ):
        response = client.get(
            "/api/v1/auth/oauth/google/start",
            follow_redirects=False,
        )
        assert response.status_code == 307 or response.status_code == 302
        location = response.headers.get("location", "")
        assert "oauth_error=google_not_configured" in location


def test_oauth_start_google_configured_redirects_to_accounts_google():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-google-client-id"), patch.object(
        settings, "GOOGLE_CLIENT_SECRET", "mock-secret"
    ):
        response = client.get(
            "/api/v1/auth/oauth/google/start",
            follow_redirects=False,
        )
        assert response.status_code == 302
        location = response.headers.get("location", "")
        assert location.startswith("https://accounts.google.com/o/oauth2/v2/auth")
        assert "client_id=mock-google-client-id" in location
        assert "scope=" in location


def test_verify_google_id_token_parses_profile():
    import asyncio

    mock_token_info = {
        "aud": "mock-client-id",
        "sub": "1234567890",
        "email": "mariachi.user@example.com",
        "name": "Mariachi User",
        "picture": "https://lh3.googleusercontent.com/photo.jpg",
    }

    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-client-id"), patch(
        "httpx.AsyncClient.get"
    ) as mock_get:
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_token_info
        mock_get.return_value = mock_response

        profile = asyncio.run(verify_google_id_token("mock-token"))

        assert isinstance(profile, OAuthProfile)
        assert profile.provider_user_id == "1234567890"
        assert profile.email == "mariachi.user@example.com"
        assert profile.fullname == "Mariachi User"
        assert profile.picture_url == "https://lh3.googleusercontent.com/photo.jpg"
