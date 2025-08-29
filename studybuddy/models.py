from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class UserProfile:
    name: str
    email: str
    courses: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "email": self.email, "courses": list(self.courses)}

    @staticmethod
    def from_dict(data: dict) -> "UserProfile":
        return UserProfile(name=data["name"], email=data["email"], courses=list(data.get("courses", [])))
