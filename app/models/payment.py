import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Numeric, DateTime, Enum, ForeignKey
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class PaymentStatus(str, enum.Enum):
    initiated = "initiated"
    retained = "retained"
    released = "released"
    refunded = "refunded"
    failed = "failed"
    rejected = "rejected"


class Payment(Base):
    __tablename__ = "payment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    booking_id = Column(UUID(as_uuid=True), ForeignKey("booking.id"))

    amount = Column(Numeric, nullable=False)
    currency = Column(String, default="PEN")

    payment_type = Column(String, nullable=True)
    # Primario (compatibilidad) + lista completa de adjuntos.
    evidence_url = Column(String, nullable=True)
    evidence_urls = Column(JSONB, nullable=True)

    status = Column(Enum(PaymentStatus), default=PaymentStatus.initiated)

    retained_at = Column(DateTime, nullable=True)
    released_at = Column(DateTime, nullable=True)

    # Auditoría de revisión admin (validar/rechazar comprobantes).
    reviewed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String, nullable=True)

    # Datos de desembolso al músico (liquidación realizada por admin / Mercado Pago)
    payout_reference = Column(String, nullable=True)
    payout_evidence_url = Column(String, nullable=True)
    payout_notes = Column(String, nullable=True)

    # Integración pasarela de pagos (Mercado Pago, etc.)

    gateway_provider = Column(String, nullable=True)
    gateway_payment_id = Column(String, nullable=True, index=True)
    gateway_preference_id = Column(String, nullable=True)
    gateway_metadata = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    booking = relationship("Booking")
