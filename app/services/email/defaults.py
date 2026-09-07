"""Default email templates seeded on startup. Admin can edit via panel."""

from __future__ import annotations

EMAIL_TEMPLATE_DEFAULTS: list[dict] = [
    {
        "slug": "welcome",
        "name": "Bienvenida",
        "description": "Se envía al crear una cuenta con correo y contraseña.",
        "subject": "Bienvenido a ChivApp, {{user_name}}",
        "available_variables": [
            "user_name",
            "user_email",
            "app_name",
            "login_url",
        ],
        "html_body": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 560px; margin: 0 auto;">
  <h1 style="color: #111; font-size: 24px;">¡Bienvenido a {{app_name}}!</h1>
  <p>Hola {{user_name}},</p>
  <p>Tu cuenta quedó creada con el correo <strong>{{user_email}}</strong>.</p>
  <p>Desde ChivApp puedes descubrir músicos, gestionar reservas y coordinar eventos.</p>
  <p style="margin: 28px 0;">
    <a href="{{login_url}}" style="background:#111;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:600;">
      Ir a ChivApp
    </a>
  </p>
  <p style="color:#666;font-size:14px;">Si no creaste esta cuenta, puedes ignorar este mensaje.</p>
</div>
""".strip(),
        "text_body": """
Hola {{user_name}},

¡Bienvenido a {{app_name}}!

Tu cuenta quedó creada con el correo {{user_email}}.

Ingresa aquí: {{login_url}}

Si no creaste esta cuenta, ignora este mensaje.
""".strip(),
    },
    {
        "slug": "email_verification",
        "name": "Verificación de correo",
        "description": "Enlace para confirmar el correo electrónico de la cuenta.",
        "subject": "Confirma tu correo en {{app_name}}",
        "available_variables": [
            "user_name",
            "user_email",
            "app_name",
            "action_url",
            "expires_hours",
        ],
        "html_body": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 560px; margin: 0 auto;">
  <h1 style="color: #111; font-size: 24px;">Confirma tu correo</h1>
  <p>Hola {{user_name}},</p>
  <p>Para activar tu cuenta en {{app_name}}, confirma que este correo te pertenece:</p>
  <p style="margin: 28px 0;">
    <a href="{{action_url}}" style="background:#111;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:600;">
      Verificar correo
    </a>
  </p>
  <p style="color:#666;font-size:14px;">Este enlace expira en {{expires_hours}} horas.</p>
  <p style="color:#666;font-size:14px;">Si no creaste una cuenta, ignora este mensaje.</p>
</div>
""".strip(),
        "text_body": """
Hola {{user_name}},

Confirma tu correo en {{app_name}} visitando:
{{action_url}}

El enlace expira en {{expires_hours}} horas.
""".strip(),
    },
    {
        "slug": "password_reset",
        "name": "Restablecer contraseña",
        "description": "Enlace para crear una nueva contraseña.",
        "subject": "Restablece tu contraseña en {{app_name}}",
        "available_variables": [
            "user_name",
            "user_email",
            "app_name",
            "action_url",
            "expires_hours",
        ],
        "html_body": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 560px; margin: 0 auto;">
  <h1 style="color: #111; font-size: 24px;">Restablece tu contraseña</h1>
  <p>Hola {{user_name}},</p>
  <p>Recibimos una solicitud para restablecer la contraseña de {{user_email}}.</p>
  <p style="margin: 28px 0;">
    <a href="{{action_url}}" style="background:#111;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:600;">
      Crear nueva contraseña
    </a>
  </p>
  <p style="color:#666;font-size:14px;">El enlace expira en {{expires_hours}} horas.</p>
  <p style="color:#666;font-size:14px;">Si no solicitaste este cambio, ignora este mensaje.</p>
</div>
""".strip(),
        "text_body": """
Hola {{user_name}},

Restablece tu contraseña en {{app_name}}:
{{action_url}}

El enlace expira en {{expires_hours}} horas.

Si no solicitaste este cambio, ignora este mensaje.
""".strip(),
    },
    {
        "slug": "ensemble_invite",
        "name": "Invitación a integrante",
        "description": "Un líder invita a alguien a unirse a su agrupación.",
        "subject": "{{leader_name}} te invitó a {{app_name}}",
        "available_variables": [
            "member_name",
            "member_email",
            "leader_name",
            "app_name",
            "action_url",
            "expires_days",
            "specialties",
        ],
        "html_body": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 560px; margin: 0 auto;">
  <h1 style="color: #111; font-size: 24px;">Te invitaron a una agrupación</h1>
  <p>Hola {{member_name}},</p>
  <p><strong>{{leader_name}}</strong> te agregó como integrante en {{app_name}}.</p>
  <p>Especialidades: {{specialties}}</p>
  <p>Crea tu contraseña para activar tu cuenta y ver convocatorias de la agrupación.</p>
  <p style="margin: 28px 0;">
    <a href="{{action_url}}" style="background:#111;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:600;">
      Crear mi contraseña
    </a>
  </p>
  <p style="color:#666;font-size:14px;">El enlace expira en {{expires_days}} días.</p>
</div>
""".strip(),
        "text_body": """
Hola {{member_name}},

{{leader_name}} te invitó a unirte a su agrupación en {{app_name}}.
Especialidades: {{specialties}}

Crea tu contraseña aquí:
{{action_url}}

El enlace expira en {{expires_days}} días.
""".strip(),
    },
    {
        "slug": "booking_member_invite",
        "name": "Convocatoria a evento",
        "description": "Un líder convoca a un integrante para un evento confirmado.",
        "subject": "{{leader_name}} te convocó a {{event_type}}",
        "available_variables": [
            "member_name",
            "leader_name",
            "app_name",
            "event_type",
            "event_date",
            "event_time",
            "event_location",
            "action_url",
        ],
        "html_body": """
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 560px; margin: 0 auto;">
  <h1 style="color: #111; font-size: 24px;">Nueva convocatoria</h1>
  <p>Hola {{member_name}},</p>
  <p><strong>{{leader_name}}</strong> te convocó a un evento en {{app_name}}.</p>
  <ul>
    <li><strong>Evento:</strong> {{event_type}}</li>
    <li><strong>Fecha:</strong> {{event_date}}</li>
    <li><strong>Hora:</strong> {{event_time}}</li>
    <li><strong>Ubicación:</strong> {{event_location}}</li>
  </ul>
  <p style="margin: 28px 0;">
    <a href="{{action_url}}" style="background:#111;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:600;">
      Ver convocatoria y responder
    </a>
  </p>
</div>
""".strip(),
        "text_body": """
Hola {{member_name}},

{{leader_name}} te convocó a {{event_type}}.
Fecha: {{event_date}}
Hora: {{event_time}}
Ubicación: {{event_location}}

Responde aquí: {{action_url}}
""".strip(),
    },
]

APP_NAME = "ChivApp"
