from __future__ import annotations

import email.utils
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    pass


def parse_sender_info(raw_sender: str) -> tuple[str, str]:
    """Extrae el nombre y correo del remitente configurado."""
    name, addr = email.utils.parseaddr(raw_sender)
    clean_name = name.strip() or "ChivApp"
    clean_addr = addr.strip() or "notificaciones@chiv.app"
    return clean_name, clean_addr


def send_via_brevo(
    *,
    to: str,
    subject: str,
    html: str,
    text: str,
    recipient_name: str | None = None,
) -> str | None:
    """Envía un correo transaccional utilizando la API v3 de Brevo."""
    if not settings.EMAIL_ENABLED:
        logger.info("Envío de correos deshabilitado; omitiendo a %s — asunto: %s", to, subject)
        return None

    if not settings.BREVO_API_KEY:
        logger.warning(
            "BREVO_API_KEY no configurada; omitiendo envío a %s — asunto: %s", to, subject
        )
        return None

    sender_name, sender_email = parse_sender_info(settings.EMAIL_FROM)

    recipient_payload: dict[str, str] = {"email": to}
    if recipient_name and recipient_name.strip():
        recipient_payload["name"] = recipient_name.strip()

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [recipient_payload],
        "subject": subject,
        "htmlContent": html,
        "textContent": text,
    }

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": settings.BREVO_API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise EmailDeliveryError(f"No se pudo contactar a Brevo: {exc}") from exc

    if response.status_code not in (200, 201):
        detail = response.text[:500]
        raise EmailDeliveryError(f"Brevo respondió con error {response.status_code}: {detail}")

    data = response.json()
    return data.get("messageId")
