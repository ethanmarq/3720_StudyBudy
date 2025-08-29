from __future__ import annotations

import re
from typing import List

from .models import UserProfile
from . import storage


class ProfileError(Exception):
    """Base exception for profile issues."""


class ValidationError(ProfileError):
    pass


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9_.+-]+@clemson\.edu$", re.IGNORECASE)
COURSE_PATTERN = re.compile(r"^[A-Z]{3,4}\s?\d{4}$")  # e.g., CPSC3720 or CPSC 3720


class ProfileService:
    """Service layer for user profile operations."""

    def create_profile(self, name: str, email: str) -> UserProfile:
        name = name.strip()
        email = email.strip()
        if not name:
            raise ValidationError("Name is required")
        if not EMAIL_PATTERN.match(email):
            raise ValidationError("Email must be a valid Clemson address ending in @clemson.edu")
        if storage.get_by_email(email):
            raise ValidationError("A profile with that email already exists")
        profile = UserProfile(name=name, email=email, courses=[])
        storage.upsert(profile)
        return profile

    def add_course(self, email: str, course_code: str) -> UserProfile:
        profile = storage.get_by_email(email)
        if not profile:
            raise ValidationError("Profile not found for email")
        norm = self._normalize_course(course_code)
        if norm not in profile.courses:
            profile.courses.append(norm)
            storage.upsert(profile)
        return profile

    def list_courses(self, email: str) -> List[str]:
        profile = storage.get_by_email(email)
        if not profile:
            raise ValidationError("Profile not found for email")
        return list(profile.courses)

    @staticmethod
    def _normalize_course(raw: str) -> str:
        candidate = raw.strip().upper().replace(" ", "")
        # Reinsert space between letters and digits for display: CPSC3720 -> CPSC 3720
        if not COURSE_PATTERN.match(candidate):
            raise ValidationError("Course code must look like CPSC 3720")
        letters = ''.join(ch for ch in candidate if ch.isalpha())
        digits = ''.join(ch for ch in candidate if ch.isdigit())
        return f"{letters} {digits}"
