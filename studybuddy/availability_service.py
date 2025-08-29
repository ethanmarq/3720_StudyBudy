from __future__ import annotations

from typing import List

from .models import UserProfile, AvailabilitySlot
from . import storage
from .profile_service import ValidationError


DAY_ORDER = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
_DAY_MAP = {d: i for i, d in enumerate(DAY_ORDER)}


def _norm_day(day: str) -> str:
    d = day.strip().upper()[:3]
    aliases = {"MON": "MON", "TUE": "TUE", "WED": "WED", "THU": "THU", "FRI": "FRI", "SAT": "SAT", "SUN": "SUN"}
    if d not in aliases:
        raise ValidationError("Day must be one of Mon Tue Wed Thu Fri Sat Sun")
    return aliases[d]


def _parse_time(t: str) -> int:
    parts = t.split(":")
    if len(parts) != 2:
        raise ValidationError("Time must be HH:MM")
    try:
        h = int(parts[0])
        m = int(parts[1])
    except ValueError:
        raise ValidationError("Time must be numeric HH:MM") from None
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValidationError("Hour 0-23, minute 0-59")
    return h * 60 + m


def _time_str(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


class AvailabilityService:
    """Manage weekly availability slots for user profiles."""

    def _get_profile(self, email: str) -> UserProfile:
        p = storage.get_by_email(email)
        if not p:
            raise ValidationError("Profile not found for email")
        return p

    def add_slot(self, email: str, day: str, start: str, end: str) -> List[AvailabilitySlot]:
        day_norm = _norm_day(day)
        start_min = _parse_time(start)
        end_min = _parse_time(end)
        if end_min <= start_min:
            raise ValidationError("End time must be after start time")
        profile = self._get_profile(email)
        # Insert then merge overlapping for that day
        profile.availability.append(AvailabilitySlot(day=day_norm, start=_time_str(start_min), end=_time_str(end_min)))
        profile.availability = self._merge(profile.availability)
        storage.upsert(profile)
        return list(profile.availability)

    def list_slots(self, email: str) -> List[AvailabilitySlot]:
        profile = self._get_profile(email)
        return self._sorted(profile.availability)

    def remove_slot(self, email: str, index: int) -> List[AvailabilitySlot]:
        profile = self._get_profile(email)
        slots = self._sorted(profile.availability)
        if index < 1 or index > len(slots):
            raise ValidationError("Index out of range")
        # Remove by identity match
        target = slots[index - 1]
        profile.availability = [s for s in profile.availability if not (s.day == target.day and s.start == target.start and s.end == target.end)]
        storage.upsert(profile)
        return self._sorted(profile.availability)

    def _sorted(self, slots: List[AvailabilitySlot]) -> List[AvailabilitySlot]:
        return sorted(slots, key=lambda s: (_DAY_MAP.get(s.day, 99), s.start))

    def _merge(self, slots: List[AvailabilitySlot]) -> List[AvailabilitySlot]:
        # Merge overlapping or contiguous slots per day
        grouped = {}
        for s in slots:
            grouped.setdefault(s.day, []).append(s)
        merged_all: List[AvailabilitySlot] = []
        for day, day_slots in grouped.items():
            # sort by start
            def to_min(s: AvailabilitySlot):
                return _parse_time(s.start), _parse_time(s.end)
            day_slots.sort(key=lambda x: _parse_time(x.start))
            cur_start, cur_end = to_min(day_slots[0])
            for s in day_slots[1:]:
                s_start, s_end = to_min(s)
                if s_start <= cur_end:  # overlap or touch
                    cur_end = max(cur_end, s_end)
                else:
                    merged_all.append(AvailabilitySlot(day=day, start=_time_str(cur_start), end=_time_str(cur_end)))
                    cur_start, cur_end = s_start, s_end
            merged_all.append(AvailabilitySlot(day=day, start=_time_str(cur_start), end=_time_str(cur_end)))
        return self._sorted(merged_all)
