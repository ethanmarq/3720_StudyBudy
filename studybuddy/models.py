from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AvailabilitySlot:
    day: str  # MON..SUN
    start: str  # HH:MM 24h
    end: str    # HH:MM 24h

    def to_dict(self) -> Dict[str, Any]:
        return {"day": self.day, "start": self.start, "end": self.end}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AvailabilitySlot":
        return AvailabilitySlot(day=data["day"], start=data["start"], end=data["end"])


@dataclass
class UserProfile:
    name: str
    email: str
    courses: List[str] = field(default_factory=list)
    availability: List[AvailabilitySlot] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "courses": list(self.courses),
            "availability": [slot.to_dict() for slot in self.availability],
        }

    @staticmethod
    def from_dict(data: dict) -> "UserProfile":
        return UserProfile(
            name=data["name"],
            email=data["email"],
            courses=list(data.get("courses", [])),
            availability=[AvailabilitySlot.from_dict(x) for x in data.get("availability", [])],
        )
