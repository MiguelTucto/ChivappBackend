from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: str
    type: str
    title: str
    message: str
    meta: dict | None = None


class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    meta: dict | None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
