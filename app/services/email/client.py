from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    pass


def send_via_resend(
    *,
    to: str,
    subject: str,
    html: str,
    text: str,
) -> str | None:
    if not settings.EMAIL_ENABLED:
        logger.info("Email disabled; skipping send to %s — subject: %s", to, subject)
        return None

    if not settings.RESEND_API_KEY:
        logger.warning(
            "RESEND_API_KEY missing; skipping send to %s — subject: %s", to, subject
        )
        return None

    payload = {
        "from": settings.EMAIL_FROM,
        "to": [to],
        "subject": subject,
        "html": html,
        "text": text,
    }

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise EmailDeliveryError(f"No se pudo contactar a Resend: {exc}") from exc

    if response.status_code >= 400:
        detail = response.text[:500]
        raise EmailDeliveryError(f"Resend respondió {response.status_code}: {detail}")

    data = response.json()
    return data.get("id")
