from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SupportTicketCreate(BaseModel):
    message: str = Field(min_length=5, max_length=2000)
    guest_name: str | None = Field(default=None, max_length=120)
    guest_email: EmailStr | None = None
    # Ruta desde la que se abrió el widget de ayuda, para dar contexto al admin.
    page_path: str | None = Field(default=None, max_length=300)


class SupportTicketOut(BaseModel):
    id: UUID
    message: str
    status: str
    admin_response: str | None
    responded_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminSupportTicketOut(SupportTicketOut):
    user_id: UUID | None
    submitter_name: str | None
    submitter_email: str | None
    submitted_ip: str | None
    submitted_user_agent: str | None
    submitted_path: str | None


class SupportTicketRespond(BaseModel):
    response: str = Field(min_length=2, max_length=2000)
    status: str = Field(default="resolved")
