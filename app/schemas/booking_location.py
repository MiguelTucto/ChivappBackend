from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LiveLocationCoords(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)


class LiveLocationEventPoint(BaseModel):
    lat: float | None = None
    lng: float | None = None
    address: str | None = None
    city: str | None = None


class LiveLocationParticipantOut(BaseModel):
    user_id: UUID
    role: str
    display_name: str
    is_me: bool = False
    sharing: bool
    lat: float | None = None
    lng: float | None = None
    accuracy: float | None = None
    updated_at: datetime | None = None
    visible: bool = False
    pending_request: bool = False
    requested_by_me: bool = False


class LiveLocationSessionOut(BaseModel):
    booking_id: UUID
    sharing_count: int = 0
    event: LiveLocationEventPoint
    me: LiveLocationParticipantOut
    participants: list[LiveLocationParticipantOut]


class LiveLocationPingOut(BaseModel):
    id: UUID
    booking_id: UUID
    user_id: UUID | None
    party: str
    action: str
    lat: float | None
    lng: float | None
    accuracy: float | None
    created_at: datetime

    model_config = {"from_attributes": True}
