from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from .models import UserProfile


DEFAULT_DATA_PATH = Path("data") / "users.json"


def _data_path() -> Path:
    # Allow override for tests via environment variable
    custom = os.environ.get("STUDYBUDDY_DATA_PATH")
    if custom:
        return Path(custom)
    return DEFAULT_DATA_PATH


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_all() -> List[UserProfile]:
    path = _data_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return [UserProfile.from_dict(d) for d in raw.get("users", [])]


def save_all(users: List[UserProfile]) -> None:
    path = _data_path()
    _ensure_parent(path)
    data = {"users": [u.to_dict() for u in users]}
    tmp_path = path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp_path.replace(path)


def get_by_email(email: str) -> Optional[UserProfile]:
    email_lower = email.lower()
    for u in load_all():
        if u.email.lower() == email_lower:
            return u
    return None


def upsert(user: UserProfile) -> None:
    users = load_all()
    updated = False
    for idx, existing in enumerate(users):
        if existing.email.lower() == user.email.lower():
            users[idx] = user
            updated = True
            break
    if not updated:
        users.append(user)
    save_all(users)
