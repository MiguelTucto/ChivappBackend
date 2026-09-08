"""Transiciones de estado para validar/rechazar comprobantes (solo admin)."""

from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.timezone import now_peru_naive
from app.models.booking import Booking, BookingStatus
from app.models.contract import Contract
from app.models.payment import Payment, PaymentStatus
from app.models.user import User


def _latest_payment(db: Session, booking_id, payment_type: str | None = None) -> Payment | None:
    query = db.query(Payment).filter(Payment.booking_id == booking_id)
    if payment_type is not None:
        query = query.filter(Payment.payment_type == payment_type)
    return query.order_by(Payment.created_at.desc()).first()


def _mark_reviewed(payment: Payment, admin_user: User) -> None:
    payment.reviewed_by_user_id = admin_user.id
    payment.reviewed_at = now_peru_naive()


def validate_advance_payment(db: Session, booking: Booking, admin_user: User) -> Booking:
    if booking.status != BookingStatus.payment_pending:
        raise HTTPException(
            status_code=400,
            detail="La reserva debe estar en estado 'payment_pending'",
        )

    payment = _latest_payment(db, booking.id)
    if not payment or payment.status != PaymentStatus.initiated:
        raise HTTPException(400, "El pago no está pendiente de validación")

    payment.status = PaymentStatus.retained
    payment.retained_at = now_peru_naive()
    _mark_reviewed(payment, admin_user)
    booking.status = BookingStatus.payment_retained
    return booking


def reject_advance_payment(
    db: Session, booking: Booking, admin_user: User, reason: str
) -> Booking:
    if booking.status != BookingStatus.payment_pending:
        raise HTTPException(
            status_code=400,
            detail="La reserva debe estar en estado 'payment_pending'",
        )

    payment = _latest_payment(db, booking.id)
    if not payment or payment.status != PaymentStatus.initiated:
        raise HTTPException(400, "El pago no está pendiente de validación")

    payment.status = PaymentStatus.rejected
    payment.rejection_reason = reason
    _mark_reviewed(payment, admin_user)

    contract = db.query(Contract).filter(Contract.booking_id == booking.id).first()
    if contract:
        contract.terms_accepted = False
        contract.terms_accepted_at = None
        contract.terms_accepted_ip = None
        contract.contractor_signed = False
        contract.contractor_sign_timestamp = None
        contract.contractor_sign_ip = None
        contract.contractor_signature_url = None
        contract.contract_signed_pdf_url = None

    booking.status = BookingStatus.contract_pending
    return booking


def validate_balance_payment(db: Session, booking: Booking, admin_user: User) -> Booking:
    if booking.status != BookingStatus.balance_review:
        raise HTTPException(400, "No hay un abono final pendiente de validación")

    payment = _latest_payment(db, booking.id, payment_type="balance")
    if not payment or payment.status != PaymentStatus.initiated:
        raise HTTPException(404, "No se encontró el comprobante del abono final")

    payment.status = PaymentStatus.retained
    payment.retained_at = now_peru_naive()
    _mark_reviewed(payment, admin_user)
    booking.status = BookingStatus.in_progress
    return booking


def reject_balance_payment(
    db: Session, booking: Booking, admin_user: User, reason: str
) -> Booking:
    if booking.status != BookingStatus.balance_review:
        raise HTTPException(400, "No hay un abono final pendiente de validación")

    payment = _latest_payment(db, booking.id, payment_type="balance")
    if not payment or payment.status != PaymentStatus.initiated:
        raise HTTPException(404, "No se encontró el comprobante del abono final")

    payment.status = PaymentStatus.rejected
    payment.rejection_reason = reason
    _mark_reviewed(payment, admin_user)
    booking.status = BookingStatus.balance_pending
    return booking
