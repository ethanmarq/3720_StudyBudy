from __future__ import annotations

import argparse
import sys
from typing import Callable

from .profile_service import ProfileService, ValidationError


def _handle_errors(func: Callable[[], int]) -> int:
    try:
        return func()
    except ValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_create_user(args) -> int:
    svc = ProfileService()
    profile = svc.create_profile(name=args.name, email=args.email)
    print(f"Created profile for {profile.name} ({profile.email})")
    return 0


def cmd_add_course(args) -> int:
    svc = ProfileService()
    profile = svc.add_course(email=args.email, course_code=args.course)
    print(f"Courses for {profile.email}: {', '.join(profile.courses) or 'None'}")
    return 0


def cmd_show_profile(args) -> int:
    svc = ProfileService()
    from . import storage
    profile = storage.get_by_email(args.email)
    if not profile:
        print("Profile not found", file=sys.stderr)
        return 1
    print(f"Name: {profile.name}\nEmail: {profile.email}\nCourses: {', '.join(profile.courses) or 'None'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="StudyBuddy CLI - Sprint 1")
    sub = p.add_subparsers(dest="command", required=True)

    c1 = sub.add_parser("create-user", help="Create a new user profile")
    c1.add_argument("--name", required=True)
    c1.add_argument("--email", required=True)
    c1.set_defaults(func=cmd_create_user)

    c2 = sub.add_parser("add-course", help="Add a course to an existing user")
    c2.add_argument("--email", required=True)
    c2.add_argument("--course", required=True)
    c2.set_defaults(func=cmd_add_course)

    c3 = sub.add_parser("show-profile", help="Show profile by email")
    c3.add_argument("--email", required=True)
    c3.set_defaults(func=cmd_show_profile)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return _handle_errors(lambda: args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
