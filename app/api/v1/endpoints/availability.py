from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.api.profile_helpers import get_or_create_musician_profile
from app.api.booking_helpers import parse_uuid
from app.models.user import User, UserRole
from app.models.musician_profile import MusicianProfile
from app.models.musician_availability import MusicianAvailability
from app.models.profile_status import ProfileStatus
from app.schemas.availability import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityOut,
)
from app.services.availability_match import list_musician_slots

router = APIRouter(prefix="/availability", tags=["Musician Availability"])

DAY_LABELS = [
    "domingo",
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
]


def _get_current_musician_profile(db: Session, current_user: User) -> MusicianProfile:
    if current_user.role != UserRole.musician:
        raise HTTPException(403, "Solo los músicos pueden gestionar disponibilidad")

    return get_or_create_musician_profile(db, current_user)


def _times_overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    return start_a < end_b and start_b < end_a


def _assert_no_overlap(
    db: Session,
    musician_id,
    day_of_week: int,
    start_time: time,
    end_time: time,
    exclude_id=None,
) -> None:
    """Evita horarios duplicados o que se crucen para el mismo día."""
    query = db.query(MusicianAvailability).filter(
        MusicianAvailability.musician_id == musician_id,
        MusicianAvailability.day_of_week == day_of_week,
    )
    if exclude_id is not None:
        query = query.filter(MusicianAvailability.id != exclude_id)

    for slot in query.all():
        if _times_overlap(start_time, end_time, slot.start_time, slot.end_time):
            day_label = DAY_LABELS[day_of_week] if 0 <= day_of_week <= 6 else "ese día"
            raise HTTPException(
                400,
                (
                    f"Ya tienes un horario los {day_label} de "
                    f"{slot.start_time.strftime('%H:%M')} a {slot.end_time.strftime('%H:%M')} "
                    "que se cruza con el horario que intentas agregar."
                ),
            )


@router.get("/me", response_model=list[AvailabilityOut])
def list_my_availability(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    musician = _get_current_musician_profile(db, current_user)
    return list_musician_slots(db, musician.id)


@router.get("/musician/{musician_id}", response_model=list[AvailabilityOut])
def list_public_musician_availability(
    musician_id: str,
    db: Session = Depends(deps.get_db),
):
    """Disponibilidad semanal de un músico publicado (para calendario de reserva)."""
    musician = db.get(MusicianProfile, parse_uuid(musician_id, "musician_id"))
    if not musician or musician.status != ProfileStatus.published:
        raise HTTPException(404, "Músico no encontrado")

    return list_musician_slots(db, musician.id)


@router.post("/me", response_model=AvailabilityOut, status_code=201)
def create_my_availability(
    payload: AvailabilityCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    musician = _get_current_musician_profile(db, current_user)

    if payload.day_of_week < 0 or payload.day_of_week > 6:
        raise HTTPException(400, "day_of_week debe estar entre 0 y 6")

    if payload.end_time <= payload.start_time:
        raise HTTPException(400, "end_time debe ser mayor que start_time")

    _assert_no_overlap(
        db,
        musician.id,
        payload.day_of_week,
        payload.start_time,
        payload.end_time,
    )

    availability = MusicianAvailability(
        musician_id=musician.id,
        day_of_week=payload.day_of_week,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )

    db.add(availability)
    db.commit()
    db.refresh(availability)

    return availability


@router.put("/me/{availability_id}", response_model=AvailabilityOut)
def update_my_availability(
    availability_id: str,
    payload: AvailabilityUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    musician = _get_current_musician_profile(db, current_user)

    availability = db.get(
        MusicianAvailability,
        parse_uuid(availability_id, "availability_id"),
    )
    if not availability or availability.musician_id != musician.id:
        raise HTTPException(404, "Disponibilidad no encontrada")

    data = payload.model_dump(exclude_unset=True)

    if "day_of_week" in data:
        if data["day_of_week"] < 0 or data["day_of_week"] > 6:
            raise HTTPException(400, "day_of_week debe estar entre 0 y 6")

    if "start_time" in data and "end_time" in data:
        if data["end_time"] <= data["start_time"]:
            raise HTTPException(400, "end_time debe ser mayor que start_time")

    effective_day = data.get("day_of_week", availability.day_of_week)
    effective_start = data.get("start_time", availability.start_time)
    effective_end = data.get("end_time", availability.end_time)
    if effective_end <= effective_start:
        raise HTTPException(400, "end_time debe ser mayor que start_time")

    _assert_no_overlap(
        db,
        musician.id,
        effective_day,
        effective_start,
        effective_end,
        exclude_id=availability.id,
    )

    for field, value in data.items():
        setattr(availability, field, value)

    db.commit()
    db.refresh(availability)

    return availability


@router.delete("/me/{availability_id}", status_code=204)
def delete_my_availability(
    availability_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    musician = _get_current_musician_profile(db, current_user)

    availability = db.get(
        MusicianAvailability,
        parse_uuid(availability_id, "availability_id"),
    )
    if not availability or availability.musician_id != musician.id:
        raise HTTPException(404, "Disponibilidad no encontrada")

    db.delete(availability)
    db.commit()
