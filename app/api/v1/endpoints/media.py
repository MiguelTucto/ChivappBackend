from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.api.profile_helpers import demote_published_profile, get_or_create_musician_profile
from app.api.booking_helpers import parse_uuid
from app.models.user import User, UserRole
from app.models.musician_profile import MusicianProfile
from app.models.musician_media import MusicianMedia
from app.schemas.media import (
    MusicianMediaCreate,
    MusicianMediaUpdate,
    MusicianMediaOut,
)
from app.services.booking_notifications import notify_profile_needs_resubmit

router = APIRouter(prefix="/musicians/media", tags=["Musician Media"])


def _get_current_musician_profile(db: Session, current_user: User) -> MusicianProfile:
    if current_user.role != UserRole.musician:
        raise HTTPException(403, "Solo los músicos pueden gestionar su media")

    return get_or_create_musician_profile(db, current_user)


@router.get("/me", response_model=list[MusicianMediaOut])
def list_my_media(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    musician = _get_current_musician_profile(db, current_user)

    rows = (
        db.query(MusicianMedia)
        .filter(MusicianMedia.musician_id == musician.id)
        .order_by(MusicianMedia.order_index.asc(), MusicianMedia.created_at.asc())
        .all()
    )

    return rows


@router.post("/me", response_model=MusicianMediaOut, status_code=201)
def create_my_media(
    payload: MusicianMediaCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    musician = _get_current_musician_profile(db, current_user)
    if demote_published_profile(musician):
        notify_profile_needs_resubmit(
            db,
            user=current_user,
            profile_role="musician",
            profile_id=str(musician.id),
        )

    media = MusicianMedia(
        musician_id=musician.id,
        type=payload.type,
        url=payload.url,
        thumbnail_url=payload.thumbnail_url,
        order_index=payload.order_index,
    )

    db.add(media)
    db.commit()
    db.refresh(media)

    return media


@router.put("/me/{media_id}", response_model=MusicianMediaOut)
def update_my_media(
    media_id: str,
    payload: MusicianMediaUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    musician = _get_current_musician_profile(db, current_user)

    media = db.get(MusicianMedia, parse_uuid(media_id, "media_id"))
    if not media or media.musician_id != musician.id:
        raise HTTPException(404, "Media no encontrada")

    changed = False
    for field, value in payload.model_dump(exclude_unset=True).items():
        if getattr(media, field) != value:
            changed = True
        setattr(media, field, value)

    if changed and demote_published_profile(musician):
        notify_profile_needs_resubmit(
            db,
            user=current_user,
            profile_role="musician",
            profile_id=str(musician.id),
        )

    db.commit()
    db.refresh(media)

    return media


@router.delete("/me/{media_id}", status_code=204)
def delete_my_media(
    media_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    musician = _get_current_musician_profile(db, current_user)

    media = db.get(MusicianMedia, parse_uuid(media_id, "media_id"))
    if not media or media.musician_id != musician.id:
        raise HTTPException(404, "Media no encontrada")

    if demote_published_profile(musician):
        notify_profile_needs_resubmit(
            db,
            user=current_user,
            profile_role="musician",
            profile_id=str(musician.id),
        )
    db.delete(media)
    db.commit()
