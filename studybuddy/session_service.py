from __future__ import annotations

from typing import List, Dict

from . import storage
from .session_models import StudySession
from . import session_storage
from .profile_service import ValidationError
from .availability_service import _parse_time, AvailabilityService, DAY_ORDER, _norm_day


class SessionService:
    """Service handling proposal and confirmation of study sessions."""

    def __init__(self) -> None:
        self._availability = AvailabilityService()

    def propose(self, requester: str, invitee: str, course: str, day: str, start: str, end: str, message: str | None = None) -> StudySession:
        if requester.lower() == invitee.lower():
            raise ValidationError("Cannot invite yourself")
        req_profile = storage.get_by_email(requester)
        inv_profile = storage.get_by_email(invitee)
        if not req_profile or not inv_profile:
            raise ValidationError("Both requester and invitee must exist")
        norm_course = self._normalize_course(course)
        if norm_course not in req_profile.courses or norm_course not in inv_profile.courses:
            raise ValidationError("Both users must be enrolled in the course")
        day_norm = _norm_day(day)
        start_min = _parse_time(start)
        end_min = _parse_time(end)
        if end_min <= start_min:
            raise ValidationError("End must be after start")
        # Validate window inside each user's availability
        if not self._window_allowed(req_profile.email, day_norm, start_min, end_min):
            raise ValidationError("Requester not available for entire window")
        if not self._window_allowed(inv_profile.email, day_norm, start_min, end_min):
            raise ValidationError("Invitee not available for entire window")
        sessions = session_storage.load_all()
        sid = session_storage.next_id(sessions)
        session = StudySession(
            id=sid,
            requester=req_profile.email,
            invitee=inv_profile.email,
            course=norm_course,
            day=day_norm,
            start=f"{start_min//60:02d}:{start_min%60:02d}",
            end=f"{end_min//60:02d}:{end_min%60:02d}",
            status="pending",
            message=message,
        )
        session_storage.upsert(session)
        return session

    def incoming_requests(self, email: str) -> List[StudySession]:
        return [s for s in session_storage.load_all() if s.invitee.lower() == email.lower() and s.status == "pending"]

    def outgoing_requests(self, email: str) -> List[StudySession]:
        return [s for s in session_storage.load_all() if s.requester.lower() == email.lower() and s.status == "pending"]

    def confirmed_sessions(self, email: str) -> List[StudySession]:
        return [s for s in session_storage.load_all() if s.status == "accepted" and (s.requester.lower() == email.lower() or s.invitee.lower() == email.lower())]

    def respond(self, session_id: int, responder_email: str, action: str) -> StudySession:
        session = session_storage.get(session_id)
        if not session:
            raise ValidationError("Session not found")
        if session.status != "pending":
            raise ValidationError("Session already finalized")
        if responder_email.lower() != session.invitee.lower():
            raise ValidationError("Only invitee can respond")
        act = action.lower()
        if act not in {"accept", "decline"}:
            raise ValidationError("Action must be accept or decline")
        session.status = "accepted" if act == "accept" else "declined"
        session_storage.upsert(session)
        return session

    def _window_allowed(self, email: str, day: str, start: int, end: int) -> bool:
        # A window is allowed if completely contained in any one availability slot
        profile = storage.get_by_email(email)
        if not profile:
            return False
        for slot in profile.availability:
            if slot.day != day:
                continue
            s = _parse_time(slot.start)
            e = _parse_time(slot.end)
            if start >= s and end <= e:
                return True
        return False

    @staticmethod
    def _normalize_course(raw: str) -> str:
        r = raw.strip().upper().replace(" ", "")
        letters = ''.join(ch for ch in r if ch.isalpha())
        digits = ''.join(ch for ch in r if ch.isdigit())
        if not letters or not digits:
            raise ValidationError("Invalid course code")
        return f"{letters} {digits}"
