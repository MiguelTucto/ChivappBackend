from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.api.booking_helpers import parse_uuid
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me", response_model=list[NotificationOut])
def list_my_notifications(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return notifs


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    notif = db.get(Notification, parse_uuid(notification_id, "notification_id"))
    if not notif:
        raise HTTPException(404, "Notificación no encontrada")

    if notif.user_id != current_user.id:
        raise HTTPException(403, "No puedes modificar esta notificación")

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif
