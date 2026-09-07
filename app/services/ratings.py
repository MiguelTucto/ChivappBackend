from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingReview
from app.models.contractor_profile import ContractorProfile
from app.models.contractor_recommendation import ContractorRecommendation
from app.models.musician_profile import MusicianProfile


def recompute_musician_rating(db: Session, musician_id) -> None:
    profile = db.query(MusicianProfile).filter(MusicianProfile.id == musician_id).first()
    if not profile:
        return

    row = (
        db.query(
            func.avg(BookingReview.rating),
            func.count(BookingReview.id),
        )
        .join(Booking, Booking.id == BookingReview.booking_id)
        .filter(
            Booking.musician_id == musician_id,
            BookingReview.is_final.is_(True),
        )
        .one()
    )
    avg_value, count = row
    if not count:
        profile.rating_avg = None
        profile.rating_count = 0
        return

    profile.rating_avg = Decimal(str(round(float(avg_value), 1)))
    profile.rating_count = int(count)


def recompute_contractor_rating(db: Session, contractor_id) -> None:
    profile = (
        db.query(ContractorProfile)
        .filter(ContractorProfile.id == contractor_id)
        .first()
    )
    if not profile:
        return

    row = (
        db.query(
            func.avg(ContractorRecommendation.rating),
            func.count(ContractorRecommendation.id),
        )
        .filter(ContractorRecommendation.contractor_id == contractor_id)
        .one()
    )
    avg_value, count = row
    if not count:
        profile.rating_avg = None
        profile.rating_count = 0
        return

    profile.rating_avg = Decimal(str(round(float(avg_value), 1)))
    profile.rating_count = int(count)
