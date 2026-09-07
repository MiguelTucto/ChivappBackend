from sqlalchemy.orm import Session

from app.models.contractor_profile import ContractorProfile
from app.models.musician_profile import MusicianProfile
from app.models.profile_status import ProfileStatus


def is_profile_public(profile: MusicianProfile | ContractorProfile) -> bool:
    """Approved by admin: published status + user verification flag."""
    return (
        profile.status == ProfileStatus.published
        and profile.user.is_verified
    )


def is_musician_listed_publicly(db: Session, profile: MusicianProfile) -> bool:
    """
    Marketplace-ready musicians: verified/published AND every profile phase complete.
    Used for home, search and public discovery — not for app feature access.
    """
    if not is_profile_public(profile):
        return False

    # Lazy import avoids circular dependency with profile_validation.
    from app.services.profile_validation import validate_musician_profile

    result = validate_musician_profile(db, profile)
    return all(step.completed for step in result.steps)
