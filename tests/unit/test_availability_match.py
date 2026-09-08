from datetime import date, time

from app.models.musician_availability import MusicianAvailability
from app.services.availability_match import (
    matching_slots,
    slot_covers,
    to_stored_day_of_week,
)


def test_to_stored_day_of_week_monday_is_one():
    # Python: Monday=0 -> stored: Sunday=0, Monday=1
    assert to_stored_day_of_week(date(2026, 8, 24)) == 1  # lunes


def test_to_stored_day_of_week_sunday_is_zero():
    assert to_stored_day_of_week(date(2026, 8, 23)) == 0  # domingo


def _slot(day_of_week: int, start: time, end: time) -> MusicianAvailability:
    slot = MusicianAvailability()
    slot.day_of_week = day_of_week
    slot.start_time = start
    slot.end_time = end
    return slot


def test_slot_covers_inside_range():
    slot = _slot(0, time(18, 0), time(23, 0))
    assert slot_covers(slot, time(19, 30)) is True


def test_slot_covers_outside_range():
    slot = _slot(0, time(18, 0), time(23, 0))
    assert slot_covers(slot, time(23, 0)) is False
    assert slot_covers(slot, time(17, 59)) is False


def test_matching_slots_filters_by_day_only():
    sunday_slot = _slot(0, time(10, 0), time(14, 0))
    monday_slot = _slot(1, time(10, 0), time(14, 0))
    result = matching_slots([sunday_slot, monday_slot], date(2026, 8, 23))
    assert result == [sunday_slot]


def test_matching_slots_filters_by_day_and_time():
    early = _slot(0, time(8, 0), time(12, 0))
    late = _slot(0, time(18, 0), time(23, 0))
    result = matching_slots([early, late], date(2026, 8, 23), start_time=time(19, 0))
    assert result == [late]


def test_assert_musician_available_allows_booking_when_no_slots_published(monkeypatch):
    from unittest.mock import MagicMock
    from uuid import uuid4
    from app.services.availability_match import assert_musician_available

    mock_db = MagicMock()
    # When list_musician_slots returns empty, availability is open
    monkeypatch.setattr(
        "app.services.availability_match.list_musician_slots",
        lambda db, m_id: [],
    )
    # Should not raise any HTTPException
    assert_musician_available(
        db=mock_db,
        musician_id=uuid4(),
        event_date=date(2026, 8, 25),
        start_time=time(20, 0),
    )

