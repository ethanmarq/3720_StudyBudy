from __future__ import annotations

import argparse
import sys
from typing import Callable

from .profile_service import ProfileService, ValidationError
from .availability_service import AvailabilityService
from .search_service import SearchService
from .session_service import SessionService
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

    # Search classmates by course (Story 3)
    s1 = sub.add_parser("search-classmates", help="List classmates in a course (excluding yourself)")
    s1.add_argument("--email", required=True, help="Your (requester) email")
    s1.add_argument("--course", required=True, help="Course code e.g. CPSC 3720")
    s1.set_defaults(func=cmd_search_classmates)

    s2 = sub.add_parser("search-classmates-availability", help="List classmates with weekly availability")
    s2.add_argument("--email", required=True)
    s2.add_argument("--course", required=True)
    s2.set_defaults(func=cmd_search_classmates_availability)

    s3 = sub.add_parser("search-overlap", help="Show overlap between you and classmates (sorted by total overlap)")
    s3.add_argument("--email", required=True)
    s3.add_argument("--course", required=True)
    s3.set_defaults(func=cmd_search_overlap)

    # Session proposal & confirmation (Story 4)
    ss1 = sub.add_parser("propose-session", help="Propose study session")
    ss1.add_argument("--from", dest="from_email", required=True, help="Requester email")
    ss1.add_argument("--to", dest="to_email", required=True, help="Invitee email")
    ss1.add_argument("--course", required=True)
    ss1.add_argument("--day", required=True)
    ss1.add_argument("--start", required=True, help="Start time (24h or 12h)")
    ss1.add_argument("--end", required=True, help="End time (24h or 12h)")
    ss1.add_argument("--message", required=False)
    ss1.set_defaults(func=cmd_propose_session)

    ss2 = sub.add_parser("list-requests", help="List incoming/outgoing pending session requests")
    ss2.add_argument("--email", required=True)
    ss2.set_defaults(func=cmd_list_requests)

    ss3 = sub.add_parser("list-sessions", help="List confirmed (accepted) sessions for a user")
    ss3.add_argument("--email", required=True)
    ss3.set_defaults(func=cmd_list_sessions)

    ss4 = sub.add_parser("respond-session", help="Accept or decline a pending session (invitee only)")
    ss4.add_argument("--email", required=True, help="Invitee email")
    ss4.add_argument("--id", type=int, required=True, help="Session ID")
    ss4.add_argument("--action", required=True, choices=["accept", "decline"])
    ss4.set_defaults(func=cmd_respond_session)
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


def cmd_search_classmates(args) -> int:
    svc = SearchService()
    classmates = svc.classmates_in_course(args.email, args.course)
    if not classmates:
        print("No classmates found for that course.")
        return 0
    print(f"Classmates in {args.course}:")
    for c in classmates:
        print(f"- {c.name} <{c.email}> | Courses: {', '.join(c.courses)}")
    return 0


def cmd_search_classmates_availability(args) -> int:
    svc = SearchService()
    entries = svc.classmates_with_availability(args.email, args.course)
    if not entries:
        print("No classmates found for that course.")
        return 0
    print(f"Classmates in {args.course} (with availability):")
    for e in entries:
        print(f"- {e['name']} <{e['email']}>")
        # Show only days that have entries
        for day, slots in e['availability'].items():
            if slots:
                formatted = ', '.join(f"{s}-{end}" for s, end in slots)
                print(f"    {day}: {formatted}")
    return 0


def cmd_search_overlap(args) -> int:
    svc = SearchService()
    overlaps = svc.overlap_with_classmates(args.email, args.course)
    if not overlaps:
        print("No classmates found for that course.")
        return 0
    print(f"Overlap with classmates in {args.course} (minutes sorted):")
    for entry in overlaps:
        name = entry['name']
        email = entry['email']
        total = entry['total_minutes']
        print(f"- {name} <{email}> Total: {total} min")
        if not entry['overlaps']:
            print("    (No overlapping availability)")
            continue
        for day, slots in entry['overlaps'].items():
            formatted = ', '.join(f"{s}-{e} ({dur}m)" for s, e, dur in slots)
            print(f"    {day}: {formatted}")
    return 0


def cmd_propose_session(args) -> int:
    svc = SessionService()
    session = svc.propose(
        requester=args.from_email,
        invitee=args.to_email,
        course=args.course,
        day=args.day,
        start=args.start,
        end=args.end,
        message=args.message,
    )
    print(f"Proposed session ID {session.id} {session.course} {session.day} {session.start}-{session.end} to {session.invitee}")
    return 0


def cmd_list_requests(args) -> int:
    svc = SessionService()
    incoming = svc.incoming_requests(args.email)
    outgoing = svc.outgoing_requests(args.email)
    print("Incoming pending requests:")
    if not incoming:
        print("  None")
    for s in incoming:
        print(f"  ID {s.id} from {s.requester} {s.course} {s.day} {s.start}-{s.end} msg={s.message or ''}")
    print("Outgoing pending requests:")
    if not outgoing:
        print("  None")
    for s in outgoing:
        print(f"  ID {s.id} to {s.invitee} {s.course} {s.day} {s.start}-{s.end} msg={s.message or ''}")
    return 0


def cmd_list_sessions(args) -> int:
    svc = SessionService()
    sessions = svc.confirmed_sessions(args.email)
    if not sessions:
        print("No confirmed sessions.")
        return 0
    print("Confirmed sessions:")
    for s in sessions:
        role = "(You requested)" if s.requester.lower() == args.email.lower() else "(You invited)"
        print(f"  ID {s.id} {s.course} {s.day} {s.start}-{s.end} with {s.invitee if s.requester.lower()==args.email.lower() else s.requester} {role}")
    return 0


def cmd_respond_session(args) -> int:
    svc = SessionService()
    session = svc.respond(session_id=args.id, responder_email=args.email, action=args.action)
    print(f"Session {session.id} now {session.status}")
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return _handle_errors(lambda: args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
