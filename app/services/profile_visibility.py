from sqlalchemy.orm import Session

from app.models.contractor_profile import ContractorProfile
from app.models.musician_profile import MusicianProfile
from app.models.profile_status import ProfileStatus


def is_profile_public(profile: MusicianProfile | ContractorProfile) -> bool:
    """Approved by admin: published status + user verification flag."""
    user = getattr(profile, "user", None)
    return (
        profile.status == ProfileStatus.published
        and user is not None
        and bool(user.is_verified)
    )


def is_musician_listed_publicly(db: Session, profile: MusicianProfile) -> bool:
    """
    Marketplace-ready musicians: verified and published by admin.
    Used for home, search, direct detail and public discovery.
    """
    return is_profile_public(profile)

