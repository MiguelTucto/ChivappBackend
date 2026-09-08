from datetime import date, datetime, time
from zoneinfo import ZoneInfo

PERU_TIMEZONE = ZoneInfo("America/Lima")


def now_peru() -> datetime:
    """Retorna el datetime actual timezone-aware en zona horaria de Perú (America/Lima)."""
    return datetime.now(PERU_TIMEZONE)


def now_peru_naive() -> datetime:
    """
    Retorna el datetime actual en horario de Perú sin offset tzinfo.
    Ideal para columnas PostgreSQL de tipo TIMESTAMP WITHOUT TIME ZONE.
    """
    return datetime.now(PERU_TIMEZONE).replace(tzinfo=None)


def to_peru_datetime(dt: datetime | None) -> datetime | None:
    """
    Convierte un datetime (naive asumido como UTC o aware) a horario de Perú timezone-aware.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Si no tiene tzinfo, se asume UTC y se convierte a Perú
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(PERU_TIMEZONE)


def combine_peru_datetime(d: date, t: time) -> datetime:
    """
    Combina fecha y hora acordadas en Perú en un datetime con zona horaria America/Lima.
    """
    return datetime.combine(d, t).replace(tzinfo=PERU_TIMEZONE)
