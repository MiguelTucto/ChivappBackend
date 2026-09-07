import uuid
from datetime import datetime, time

from sqlalchemy import Column, Integer, Time, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class MusicianAvailability(Base):
    __tablename__ = "musician_availability"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    musician_id = Column(
        UUID(as_uuid=True),
        ForeignKey("musician_profile.id"),
        nullable=False
    )

    # 0 = domingo, 1 = lunes, ..., 6 = sábado (misma convención que JS Date.getDay)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    musician = relationship("MusicianProfile")
