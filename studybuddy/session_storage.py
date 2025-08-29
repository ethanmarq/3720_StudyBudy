from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from .session_models import StudySession

DEFAULT_SESSIONS_PATH = Path("data") / "sessions.json"


def _sessions_path() -> Path:
    custom = os.environ.get("STUDYBUDDY_SESSIONS_PATH")
    return Path(custom) if custom else DEFAULT_SESSIONS_PATH


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_all() -> List[StudySession]:
    path = _sessions_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return [StudySession.from_dict(d) for d in raw.get("sessions", [])]


def save_all(sessions: List[StudySession]) -> None:
    path = _sessions_path()
    _ensure_parent(path)
    data = {"sessions": [s.to_dict() for s in sessions]}
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


def next_id(sessions: List[StudySession]) -> int:
    return (max((s.id for s in sessions), default=0) + 1)


def get(session_id: int) -> Optional[StudySession]:
    for s in load_all():
        if s.id == session_id:
            return s
    return None


def upsert(session: StudySession) -> None:
    sessions = load_all()
    replaced = False
    for i, s in enumerate(sessions):
        if s.id == session.id:
            sessions[i] = session
            replaced = True
            break
    if not replaced:
        sessions.append(session)
    save_all(sessions)
