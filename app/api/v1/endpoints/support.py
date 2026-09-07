from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.models.support_ticket import SupportTicket
from app.models.user import User
from app.schemas.support import SupportTicketCreate, SupportTicketOut

router = APIRouter(prefix="/support", tags=["Support"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


@router.post("/tickets", response_model=SupportTicketOut, status_code=201)
def create_support_ticket(
    payload: SupportTicketCreate,
    request: Request,
    current_user: User | None = Depends(deps.get_current_user_optional),
    db: Session = Depends(deps.get_db),
):
    if not current_user:
        if not payload.guest_name or not payload.guest_email:
            raise HTTPException(
                400, "Nombre y correo son obligatorios si no has iniciado sesión"
            )

    ticket = SupportTicket(
        user_id=current_user.id if current_user else None,
        guest_name=None if current_user else payload.guest_name,
        guest_email=None if current_user else payload.guest_email,
        message=payload.message,
        submitted_ip=_client_ip(request),
        submitted_user_agent=request.headers.get("user-agent"),
        submitted_path=payload.page_path,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tickets/me", response_model=list[SupportTicketOut])
def list_my_support_tickets(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return (
        db.query(SupportTicket)
        .filter(SupportTicket.user_id == current_user.id)
        .order_by(SupportTicket.created_at.desc())
        .all()
    )
