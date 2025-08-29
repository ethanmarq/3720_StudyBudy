from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Dict, Any

Status = Literal["pending", "accepted", "declined"]


@dataclass
class StudySession:
    id: int
    requester: str
    invitee: str
    course: str
    day: str  # MON..SUN
    start: str  # HH:MM 24h
    end: str    # HH:MM 24h
    status: Status = "pending"
    message: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "requester": self.requester,
            "invitee": self.invitee,
            "course": self.course,
            "day": self.day,
            "start": self.start,
            "end": self.end,
            "status": self.status,
            "message": self.message,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "StudySession":
        return StudySession(
            id=d["id"],
            requester=d["requester"],
            invitee=d["invitee"],
            course=d["course"],
            day=d["day"],
            start=d["start"],
            end=d["end"],
            status=d.get("status", "pending"),
            message=d.get("message"),
        )
