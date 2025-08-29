from __future__ import annotations

import argparse
import sys
from typing import Callable

from .profile_service import ProfileService, ValidationError
from .availability_service import AvailabilityService
from .availability_service import DAY_ORDER as _DAY_ORDER


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


def cmd_add_availability(args) -> int:
    svc = AvailabilityService()
    slots = svc.add_slot(email=args.email, day=args.day, start=args.start, end=args.end)
    _print_slots(slots)
    return 0


def cmd_list_availability(args) -> int:
    svc = AvailabilityService()
    slots = svc.list_slots(email=args.email)
    _print_slots(slots)
    return 0


def cmd_remove_availability(args) -> int:
    svc = AvailabilityService()
    slots = svc.remove_slot(email=args.email, index=args.index)
    _print_slots(slots)
    return 0


def _print_slots(slots):  # minimal formatting
    if not slots:
        print("No availability set")
        return
    for i, s in enumerate(slots, start=1):
        print(f"{i}. {s.day} {s.start}-{s.end}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="StudyBuddy CLI - Sprint 1 + Availability")
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

    # Availability commands (Story 2)
    a1 = sub.add_parser("add-availability", help="Add availability slot: day start end (start/end accept 09:00 or 9:00am)")
    a1.add_argument("--email", required=True)
    a1.add_argument("--day", required=True, help="Mon Tue Wed Thu Fri Sat Sun")
    a1.add_argument("--start", required=True, help="Start time (24h HH:MM or 12h like 9am / 1:30pm)")
    a1.add_argument("--end", required=True, help="End time (24h HH:MM or 12h like 11am / 4:15pm)")
    a1.set_defaults(func=cmd_add_availability)

    a2 = sub.add_parser("list-availability", help="List availability slots with indices")
    a2.add_argument("--email", required=True)
    a2.set_defaults(func=cmd_list_availability)

    a3 = sub.add_parser("remove-availability", help="Remove availability slot by index (see list-availability)")
    a3.add_argument("--email", required=True)
    a3.add_argument("--index", type=int, required=True)
    a3.set_defaults(func=cmd_remove_availability)

    a4 = sub.add_parser("week-availability", help="Show all days with availability (12h format)")
    a4.add_argument("--email", required=True)
    a4.set_defaults(func=cmd_week_availability)
    return p


def cmd_week_availability(args) -> int:
    svc = AvailabilityService()
    overview = svc.weekly_overview(email=args.email)
    print("Weekly Availability (EST):")
    for day in _DAY_ORDER:
        entries = overview.get(day, [])
        if not entries:
            print(f"{day}: None")
        else:
            print(f"{day}: {', '.join(f'{s}-{e}' for s, e in entries)}")
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return _handle_errors(lambda: args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
