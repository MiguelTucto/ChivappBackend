from decimal import Decimal

from app.models.booking import Booking
from app.models.booking_complaint import REFUND_STATUS_AWAITING_TRANSFER, REFUND_STATUS_NONE, BookingComplaint
from app.services.settlement import (
    complaint_refund_amount,
    complaint_refund_status,
    fee_portion_from_gross,
    musician_pool_from_gross,
)


def _booking(price_agreed, platform_fee_amount, platform_fee_percent=None) -> Booking:
    booking = Booking()
    booking.price_agreed = price_agreed
    booking.platform_fee_amount = platform_fee_amount
    booking.platform_fee_percent = platform_fee_percent
    return booking


def test_musician_pool_from_gross_excludes_platform_fee():
    booking = _booking(Decimal("500"), Decimal("10"), Decimal("2"))
    assert musician_pool_from_gross(booking, 533.15) == 500.0


def test_fee_portion_from_gross_is_the_remainder():
    booking = _booking(Decimal("500"), Decimal("10"), Decimal("2"))
    assert fee_portion_from_gross(booking, 533.15) == 33.15


def test_fee_portion_from_gross_never_negative():
    booking = _booking(Decimal("500"), Decimal("10"), Decimal("2"))
    # gross menor al pool esperado no debe producir una comisión negativa
    assert fee_portion_from_gross(booking, 100.0) >= 0.0


def test_complaint_refund_amount_none_complaint_is_zero():
    assert complaint_refund_amount(None) == 0.0


def test_complaint_refund_amount_reads_admin_amount():
    complaint = BookingComplaint()
    complaint.admin_contractor_refund = Decimal("45.50")
    assert complaint_refund_amount(complaint) == 45.5


def test_complaint_refund_status_defaults_to_none():
    assert complaint_refund_status(None) == REFUND_STATUS_NONE


def test_complaint_refund_status_reads_field():
    complaint = BookingComplaint()
    complaint.refund_status = REFUND_STATUS_AWAITING_TRANSFER
    assert complaint_refund_status(complaint) == REFUND_STATUS_AWAITING_TRANSFER
