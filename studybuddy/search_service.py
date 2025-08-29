from __future__ import annotations

from typing import List, Dict, Tuple

from . import storage
from .models import UserProfile
from .profile_service import ValidationError
from .availability_service import AvailabilityService


class SearchService:
    """Search and retrieval operations for classmates and their availability."""

    def __init__(self) -> None:
        self._availability = AvailabilityService()

    def classmates_in_course(self, requester_email: str, course_code: str) -> List[UserProfile]:
        requestor = storage.get_by_email(requester_email)
        if not requestor:
            raise ValidationError("Requester profile not found")
        norm_course = self._normalize_course(course_code)
        users = storage.load_all()
        results = []
        for u in users:
            if u.email.lower() == requester_email.lower():
                continue
            if norm_course in u.courses:
                results.append(u)
        return results

    def classmates_with_availability(self, requester_email: str, course_code: str) -> List[Dict]:
        classmates = self.classmates_in_course(requester_email, course_code)
        enriched: List[Dict] = []
        for c in classmates:
            overview = self._availability.weekly_overview(c.email)
            enriched.append({
                "name": c.name,
                "email": c.email,
                "courses": list(c.courses),
                "availability": overview,
            })
        return enriched

    def overlap_with_classmates(self, requester_email: str, course_code: str) -> List[Dict]:
        """Return overlap windows between requester and each classmate for the course.

        Each entry: {
          name, email, overlaps: {DAY: [(start12h, end12h, minutes)]}, total_minutes
        }
        Only days with at least one overlap are included in overlaps dict.
        """
        requester = storage.get_by_email(requester_email)
        if not requester:
            raise ValidationError("Requester profile not found")
        requester_slots = requester.availability  # already merged when stored
        classmates = self.classmates_in_course(requester_email, course_code)
        results: List[Dict] = []
        for mate in classmates:
            mate_slots = mate.availability
            overlaps = self._compute_overlaps(requester_slots, mate_slots)
            if overlaps:
                total = sum(dur for _, _, _, dur in overlaps)
                # group by day for formatting
                day_map: Dict[str, List[Tuple[str, str, int]]] = {}
                for day, s12, e12, dur in overlaps:
                    day_map.setdefault(day, []).append((s12, e12, dur))
                results.append({
                    "name": mate.name,
                    "email": mate.email,
                    "total_minutes": total,
                    "overlaps": day_map,
                })
            else:
                results.append({
                    "name": mate.name,
                    "email": mate.email,
                    "total_minutes": 0,
                    "overlaps": {},
                })
        # Sort by total overlap descending
        results.sort(key=lambda x: x["total_minutes"], reverse=True)
        return results

    def _compute_overlaps(self, slots_a, slots_b) -> List[Tuple[str, str, str, int]]:
        """Compute overlaps between two availability slot lists.

        Returns list of tuples: (DAY, start12h, end12h, duration_minutes)
        """
        overlaps: List[Tuple[str, str, str, int]] = []
        # Build per-day lists (they are already merged individually)
        from .availability_service import _parse_time, AvailabilityService as AS
        conv = AS._to_12h  # reuse formatting
        by_day_a: Dict[str, List[Tuple[int, int]]] = {}
        by_day_b: Dict[str, List[Tuple[int, int]]] = {}
        for s in slots_a:
            by_day_a.setdefault(s.day, []).append((_parse_time(s.start), _parse_time(s.end)))
        for s in slots_b:
            by_day_b.setdefault(s.day, []).append((_parse_time(s.start), _parse_time(s.end)))
        for day, intervals_a in by_day_a.items():
            if day not in by_day_b:
                continue
            for sa_start, sa_end in intervals_a:
                for sb_start, sb_end in by_day_b[day]:
                    start = max(sa_start, sb_start)
                    end = min(sa_end, sb_end)
                    if end > start:
                        overlaps.append((day, conv(f"{start//60:02d}:{start%60:02d}"), conv(f"{end//60:02d}:{end%60:02d}"), end - start))
        return overlaps

    @staticmethod
    def _normalize_course(raw: str) -> str:
        r = raw.strip().upper().replace(" ", "")
        letters = ''.join(ch for ch in r if ch.isalpha())
        digits = ''.join(ch for ch in r if ch.isdigit())
        if not letters or not digits:
            raise ValidationError("Invalid course code")
        return f"{letters} {digits}"
