from datetime import time, datetime
from uuid import UUID

from pydantic import BaseModel


class AvailabilityBase(BaseModel):
    # 0 = domingo, 1 = lunes, ..., 6 = sábado
    day_of_week: int
    start_time: time
    end_time: time


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityUpdate(BaseModel):
    day_of_week: int | None = None
    start_time: time | None = None
    end_time: time | None = None


class AvailabilityOut(AvailabilityBase):
    id: UUID
    musician_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
