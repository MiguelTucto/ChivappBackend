import pytest

from app.models.musician_profile import AvailabilityType, MusicianProfile
from app.models.profile_status import ProfileStatus
from app.models.user import User, UserRole
from app.services.uniqueness import next_available_musician_slug

pytestmark = pytest.mark.db


def _create_musician(db_session, email: str, stage_name: str, slug: str) -> MusicianProfile:
    user = User(email=email, fullname=stage_name, role=UserRole.musician)
    db_session.add(user)
    db_session.flush()

    profile = MusicianProfile(
        user_id=user.id,
        stage_name=stage_name,
        slug=slug,
        status=ProfileStatus.draft,
        availability_type=AvailabilityType.both,
    )
    db_session.add(profile)
    db_session.flush()
    return profile


def test_next_available_slug_is_base_when_free(db_session):
    assert next_available_musician_slug(db_session, "Mariachi Nuevo") == "mariachi-nuevo"


def test_next_available_slug_adds_suffix_on_collision(db_session):
    _create_musician(db_session, "uno@example.com", "Mariachi Popular", "mariachi-popular")
    assert next_available_musician_slug(db_session, "Mariachi Popular") == "mariachi-popular-2"


def test_next_available_slug_skips_taken_suffixes_too(db_session):
    # Nombres artísticos distintos (la unicidad de stage_name es case-insensitive
    # pero no ignora acentos) que, al quitarles los acentos, producen el mismo slug.
    _create_musician(db_session, "uno@example.com", "Mariachi Ánimo", "mariachi-animo")
    _create_musician(db_session, "dos@example.com", "Mariachi Animo", "mariachi-animo-2")
    assert next_available_musician_slug(db_session, "Mariachi ánimo") == "mariachi-animo-3"


def test_next_available_slug_excludes_given_profile_id(db_session):
    profile = _create_musician(db_session, "uno@example.com", "Mariachi Popular", "mariachi-popular")
    # El propio perfil no debe "chocar" consigo mismo al recalcular su slug.
    assert (
        next_available_musician_slug(db_session, "Mariachi Popular", exclude_profile_id=profile.id)
        == "mariachi-popular"
    )
