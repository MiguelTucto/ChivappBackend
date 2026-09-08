"""Default email templates seeded on startup. Admin can edit via panel."""

from __future__ import annotations

from app.services.email.email_builder import build_email_layout

APP_NAME = "ChivApp"

EMAIL_TEMPLATE_DEFAULTS: list[dict] = [
    {
        "slug": "welcome",
        "name": "Bienvenida",
        "description": "Se envía al crear una cuenta con correo y contraseña.",
        "subject": "¡Bienvenido a ChivApp, {{user_name}}!",
        "available_variables": [
            "user_name",
            "user_email",
            "app_name",
            "login_url",
        ],
        "html_body": build_email_layout(
            category_badge="Bienvenida",
            badge_bg="#DCFCE7",
            badge_color="#15803D",
            title="¡Bienvenido a {{app_name}}!",
            greeting="Hola {{user_name}},",
            lead_text="Tu cuenta ha sido creada exitosamente con el correo <strong>{{user_email}}</strong>. Desde ChivApp puedes descubrir músicos, gestionar reservas y coordinar tus presentaciones.",
            info_items=[
                ("Correo registrado", "{{user_email}}"),
                ("Plataforma", "{{app_name}}"),
            ],
            cta_label="Ir a ChivApp",
            cta_url="{{login_url}}",
            secondary_note="Si no creaste esta cuenta, puedes ignorar este mensaje.",
        ),
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
        "html_body": build_email_layout(
            category_badge="Seguridad",
            badge_bg="#FEF3C7",
            badge_color="#92400E",
            title="Confirma tu correo electrónico",
            greeting="Hola {{user_name}},",
            lead_text="Para activar tu cuenta en {{app_name}} y mantenerla protegida, confirma que esta dirección de correo te pertenece pulsando el siguiente botón:",
            cta_label="Verificar mi correo",
            cta_url="{{action_url}}",
            secondary_note="⏳ Este enlace expira en {{expires_hours}} horas. Si no creaste una cuenta, puedes ignorar este mensaje.",
        ),
        "text_body": """
Hola {{user_name}},

Confirma tu correo en {{app_name}} visitando:
{{action_url}}

El enlace expira en {{expires_hours}} horas.
Si no creaste una cuenta, ignora este mensaje.
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
        "html_body": build_email_layout(
            category_badge="Seguridad",
            badge_bg="#FEE2E2",
            badge_color="#991B1B",
            title="Restablece tu contraseña",
            greeting="Hola {{user_name}},",
            lead_text="Recibimos una solicitud para restablecer la contraseña asociada a <strong>{{user_email}}</strong>. Haz clic en el botón para crear tu nueva contraseña:",
            cta_label="Crear nueva contraseña",
            cta_url="{{action_url}}",
            secondary_note="⏳ El enlace expira en {{expires_hours}} horas. Si tú no solicitaste este cambio, no te preocupes; tu cuenta sigue segura y puedes ignorar este mensaje.",
        ),
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
        "subject": "{{leader_name}} te invitó a unirte a su agrupación en {{app_name}}",
        "available_variables": [
            "member_name",
            "member_email",
            "leader_name",
            "app_name",
            "action_url",
            "expires_days",
            "specialties",
        ],
        "html_body": build_email_layout(
            category_badge="Agrupación",
            badge_bg="#EDE9FE",
            badge_color="#5B21B6",
            title="Te invitaron a una agrupación musical",
            greeting="Hola {{member_name}},",
            lead_text="<strong>{{leader_name}}</strong> te agregó como integrante en {{app_name}}. Crea tu contraseña para activar tu cuenta, ver convocatorias y coordinar tus presentaciones:",
            info_items=[
                ("Líder / Grupo", "{{leader_name}}"),
                ("Especialidades", "{{specialties}}"),
            ],
            cta_label="Crear mi contraseña y unirme",
            cta_url="{{action_url}}",
            secondary_note="⏳ El enlace de invitación expira en {{expires_days}} días.",
        ),
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
        "subject": "Convocatoria: {{leader_name}} te convocó a {{event_type}}",
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
        "html_body": build_email_layout(
            category_badge="Convocatoria",
            badge_bg="#FEF9C3",
            badge_color="#854D0E",
            title="Nueva convocatoria para evento",
            greeting="Hola {{member_name}},",
            lead_text="<strong>{{leader_name}}</strong> te ha convocado a una presentación en {{app_name}}. Revisa los datos y confirma tu asistencia:",
            info_items=[
                ("Tipo de evento", "{{event_type}}"),
                ("Fecha", "{{event_date}}"),
                ("Hora de inicio", "{{event_time}} (Hora Perú)"),
                ("Ubicación", "{{event_location}}"),
            ],
            cta_label="Ver convocatoria y responder",
            cta_url="{{action_url}}",
            secondary_note="Por favor responde a la brevedad para que el líder pueda cerrar la formación del grupo.",
        ),
        "text_body": """
Hola {{member_name}},

{{leader_name}} te convocó a {{event_type}}.
Fecha: {{event_date}}
Hora: {{event_time}} (Hora Perú)
Ubicación: {{event_location}}

Responde aquí: {{action_url}}
""".strip(),
    },
    {
        "slug": "booking_new_request",
        "name": "Nueva solicitud de reserva",
        "description": "Se envía al músico cuando un cliente genera una solicitud de reserva.",
        "subject": "¡Nueva solicitud de {{contractor_name}} para {{event_type}} en {{app_name}}!",
        "available_variables": [
            "musician_name",
            "contractor_name",
            "app_name",
            "event_type",
            "event_date",
            "event_time",
            "event_location",
            "event_description",
            "action_url",
        ],
        "html_body": build_email_layout(
            category_badge="Nueva Solicitud",
            badge_bg="#E0F2FE",
            badge_color="#0369A1",
            title="¡Tienes una nueva solicitud de reserva!",
            greeting="Hola {{musician_name}},",
            lead_text="El cliente <strong>{{contractor_name}}</strong> está interesado en tu agrupación y te ha enviado una solicitud de reserva en {{app_name}}:",
            info_items=[
                ("Cliente", "{{contractor_name}}"),
                ("Tipo de evento", "{{event_type}}"),
                ("Fecha del evento", "{{event_date}}"),
                ("Hora de inicio", "{{event_time}} (Hora Perú)"),
                ("Lugar / Dirección", "{{event_location}}"),
                ("Detalles / Mensaje", "{{event_description}}"),
            ],
            cta_label="Ver solicitud y cotizar",
            cta_url="{{action_url}}",
            secondary_note="Responde a tiempo para asegurar la reserva y brindar un excelente servicio.",
        ),
        "text_body": """
Hola {{musician_name}},

El cliente {{contractor_name}} te ha enviado una nueva solicitud de reserva en {{app_name}}:

Tipo de evento: {{event_type}}
Fecha: {{event_date}}
Hora: {{event_time}} (Hora Perú)
Ubicación: {{event_location}}
Detalles: {{event_description}}

Revisa la solicitud y envía tu cotización aquí:
{{action_url}}
""".strip(),
    },
]
