"""Match booking date/time against musician weekly availability slots.

day_of_week convention (aligned with the musician wizard / JS Date.getDay):
0 = Domingo, 1 = Lunes, ..., 6 = Sábado.
"""

from __future__ import annotations

from datetime import date, time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.musician_availability import MusicianAvailability

DAY_LABELS = (
    "Domingo",
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
)


def to_stored_day_of_week(event_date: date) -> int:
    """Python Monday=0 → stored Sunday=0."""
    return (event_date.weekday() + 1) % 7


def list_musician_slots(db: Session, musician_id) -> list[MusicianAvailability]:
    return (
        db.query(MusicianAvailability)
        .filter(MusicianAvailability.musician_id == musician_id)
        .order_by(
            MusicianAvailability.day_of_week,
            MusicianAvailability.start_time,
        )
        .all()
    )


def format_time(value: time) -> str:
    return value.strftime("%H:%M")


def slot_covers(slot: MusicianAvailability, start_time: time) -> bool:
    return slot.start_time <= start_time < slot.end_time


def matching_slots(
    slots: list[MusicianAvailability],
    event_date: date,
    start_time: time | None = None,
) -> list[MusicianAvailability]:
    dow = to_stored_day_of_week(event_date)
    day_slots = [slot for slot in slots if slot.day_of_week == dow]
    if start_time is None:
        return day_slots
    return [slot for slot in day_slots if slot_covers(slot, start_time)]


def assert_musician_available(
    db: Session,
    musician_id,
    event_date: date,
    start_time: time,
) -> None:
    slots = list_musician_slots(db, musician_id)
    if not slots:
        raise HTTPException(
            400,
            "Este músico aún no tiene horarios de disponibilidad publicados.",
        )

    day_slots = matching_slots(slots, event_date)
    if not day_slots:
        labels = sorted({DAY_LABELS[s.day_of_week] for s in slots})
        raise HTTPException(
            400,
            "El músico no está disponible ese día. "
            f"Días disponibles: {', '.join(labels)}.",
        )

    if not matching_slots(slots, event_date, start_time):
        windows = ", ".join(
            f"{format_time(s.start_time)}–{format_time(s.end_time)}" for s in day_slots
        )
        raise HTTPException(
            400,
            f"La hora está fuera de la disponibilidad del músico ({windows}).",
        )
