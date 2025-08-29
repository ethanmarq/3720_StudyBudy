"""StudyBuddy package.

Sprint 1 scope: User profile creation and course management.
"""

from .models import UserProfile, AvailabilitySlot  # noqa: F401
from .profile_service import ProfileService, ProfileError, ValidationError  # noqa: F401
from .availability_service import AvailabilityService  # noqa: F401
