from datetime import date, time

import pytest

from app.core.hashing import hash_password
from app.models.booking import Booking, BookingStatus
from app.models.contractor_profile import ContractorProfile
from app.models.musician_profile import MusicianProfile
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole
from app.services import payment_review

pytestmark = pytest.mark.db


def _user(db, *, role, email):
    user = User(email=email, fullname=f"{role.value} test", role=role)
    db.add(user)
    db.flush()
    return user


def _booking(db, *, status):
    musician_user = _user(db, role=UserRole.musician, email="musician@test.com")
    contractor_user = _user(db, role=UserRole.contractor, email="contractor@test.com")
    admin_user = _user(db, role=UserRole.admin, email="admin@test.com")

    musician = MusicianProfile(user_id=musician_user.id, stage_name="Mariachi Test")
    contractor = ContractorProfile(user_id=contractor_user.id)
    db.add_all([musician, contractor])
    db.flush()

    booking = Booking(
        contractor_id=contractor.id,
        musician_id=musician.id,
        event_date=date(2026, 1, 1),
        start_time=time(20, 0),
        location_address="Av. Test 123",
        event_type="Boda",
        status=status,
    )
    db.add(booking)
    db.flush()
    return booking, admin_user


def _payment(db, booking, *, payment_type, status=PaymentStatus.initiated):
    payment = Payment(
        booking_id=booking.id,
        amount=100,
        payment_type=payment_type,
        status=status,
    )
    db.add(payment)
    db.flush()
    return payment


def test_validate_advance_payment_confirms_booking_and_stamps_audit(db_session):
    booking, admin = _booking(db_session, status=BookingStatus.payment_pending)
    payment = _payment(db_session, booking, payment_type="advance")

    payment_review.validate_advance_payment(db_session, booking, admin)

    assert booking.status == BookingStatus.payment_retained
    assert payment.status == PaymentStatus.retained
    assert payment.reviewed_by_user_id == admin.id
    assert payment.reviewed_at is not None


def test_reject_advance_payment_returns_to_contract_pending_and_keeps_history(db_session):
    booking, admin = _booking(db_session, status=BookingStatus.payment_pending)
    payment = _payment(db_session, booking, payment_type="advance")

    payment_review.reject_advance_payment(db_session, booking, admin, "Monto no coincide")

    assert booking.status == BookingStatus.contract_pending
    assert payment.status == PaymentStatus.rejected
    assert payment.rejection_reason == "Monto no coincide"
    # El pago rechazado se conserva (no se borra) para trazabilidad del admin.
    assert db_session.query(Payment).filter(Payment.id == payment.id).count() == 1


def test_validate_advance_payment_wrong_status_raises(db_session):
    from fastapi import HTTPException

    booking, admin = _booking(db_session, status=BookingStatus.contract_pending)

    with pytest.raises(HTTPException):
        payment_review.validate_advance_payment(db_session, booking, admin)


def test_validate_balance_payment_enables_event_phase(db_session):
    booking, admin = _booking(db_session, status=BookingStatus.balance_review)
    payment = _payment(db_session, booking, payment_type="balance")

    payment_review.validate_balance_payment(db_session, booking, admin)

    assert booking.status == BookingStatus.in_progress
    assert payment.status == PaymentStatus.retained
    assert payment.reviewed_by_user_id == admin.id


def test_reject_balance_payment_returns_to_balance_pending(db_session):
    booking, admin = _booking(db_session, status=BookingStatus.balance_review)
    payment = _payment(db_session, booking, payment_type="balance")

    payment_review.reject_balance_payment(db_session, booking, admin, "Comprobante ilegible")

    assert booking.status == BookingStatus.balance_pending
    assert payment.status == PaymentStatus.rejected
    assert payment.rejection_reason == "Comprobante ilegible"


def _login(client, email, password):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response


def test_admin_advance_endpoints_full_http_cycle(client, db_session):
    """Ejercita el router real: auth admin, joinedload de partes, notificaciones y serialización."""
    booking, _ = _booking(db_session, status=BookingStatus.payment_pending)
    _payment(db_session, booking, payment_type="advance")

    admin = db_session.query(User).filter(User.role == UserRole.admin).first()
    admin.password_hash = hash_password("AdminPass123")
    db_session.commit()

    musician = db_session.query(User).filter(User.role == UserRole.musician).first()
    musician.password_hash = hash_password("MusicPass123")
    db_session.commit()

    # Un músico no puede usar los endpoints de admin.
    _login(client, musician.email, "MusicPass123")
    forbidden = client.post(f"/api/v1/admin/bookings/{booking.id}/advance/validate")
    assert forbidden.status_code == 403

    _login(client, admin.email, "AdminPass123")

    pending = client.get("/api/v1/admin/payments/pending-review")
    assert pending.status_code == 200
    assert any(item["booking_id"] == str(booking.id) for item in pending.json())

    validated = client.post(f"/api/v1/admin/bookings/{booking.id}/advance/validate")
    assert validated.status_code == 200, validated.text
    assert validated.json()["status"] == "payment_retained"

    # Ya no queda pendiente de revisión.
    pending_after = client.get("/api/v1/admin/payments/pending-review")
    assert not any(item["booking_id"] == str(booking.id) for item in pending_after.json())


def test_admin_booking_detail_composes_full_view(client, db_session):
    """El detalle debe responder aunque la reserva no tenga contrato/mensajes/queja aún."""
    booking, _ = _booking(db_session, status=BookingStatus.payment_pending)
    payment = _payment(db_session, booking, payment_type="advance")
    payment.status = PaymentStatus.rejected
    payment.rejection_reason = "Monto no coincide"
    db_session.commit()

    admin = db_session.query(User).filter(User.role == UserRole.admin).first()
    admin.password_hash = hash_password("AdminPass123")
    db_session.commit()
    _login(client, admin.email, "AdminPass123")

    response = client.get(f"/api/v1/admin/bookings/{booking.id}/detail")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["id"] == str(booking.id)
    assert body["contract"] is None
    assert body["complaint"] is None
    assert body["messages"] == []
    assert body["reviews"] == []
    assert len(body["payments"]) == 1
    assert body["payments"][0]["rejection_reason"] == "Monto no coincide"
    assert body["balance_due"] >= 0

    pdf_response = client.get(f"/api/v1/admin/bookings/{booking.id}/contract-pdf")
    assert pdf_response.status_code == 404  # sin contrato asociado todavía


def test_get_contractor_profile_or_400_allows_unverified_contractor(db_session):
    from app.api.booking_helpers import get_contractor_profile_or_400
    contractor_user = _user(db_session, role=UserRole.contractor, email="unverified_c@test.com")
    contractor_user.is_verified = False

    profile = get_contractor_profile_or_400(db_session, contractor_user)
    assert profile is not None
    assert profile.user_id == contractor_user.id

