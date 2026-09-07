from app.models.user import User
from app.services.email.defaults import APP_NAME


def build_sample_email_context(user: User) -> dict[str, str]:
    return {
        "user_name": user.fullname,
        "user_email": user.email,
        "member_name": "María Integrante",
        "member_email": "integrante@email.com",
        "leader_name": user.fullname,
        "app_name": APP_NAME,
        "login_url": "https://chivapp.com/",
        "action_url": "https://chivapp.com/ejemplo",
        "expires_hours": "48",
        "expires_days": "14",
        "specialties": "Trompeta, Coro",
        "event_type": "Boda",
        "event_date": "15/08/2026",
        "event_time": "19:00",
        "event_location": "Salón Jardín, Lima",
    }
