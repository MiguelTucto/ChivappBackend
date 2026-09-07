from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from app.models.musician_media import MediaType


class MusicianMediaBase(BaseModel):
    type: MediaType
    url: str
    thumbnail_url: str | None = None
    order_index: int = 0


class MusicianMediaCreate(MusicianMediaBase):
    pass


class MusicianMediaUpdate(BaseModel):
    type: MediaType | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    order_index: int | None = None


class MusicianMediaOut(MusicianMediaBase):
    id: UUID
    musician_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
