import os
import tempfile
import json
import pytest

from studybuddy.profile_service import ProfileService, ValidationError
from studybuddy.availability_service import AvailabilityService
from studybuddy import storage
from studybuddy.search_service import SearchService
from studybuddy.session_service import SessionService


def use_temp_store(func):
    def wrapper():
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "users.json")
            os.environ["STUDYBUDDY_DATA_PATH"] = path
            try:
                func()
            finally:
                os.environ.pop("STUDYBUDDY_DATA_PATH", None)
    return wrapper


@use_temp_store
def test_create_profile_success():
    svc = ProfileService()
    p = svc.create_profile("Alice", "alice@clemson.edu")
    assert p.email == "alice@clemson.edu"
    assert storage.get_by_email("alice@clemson.edu") is not None


@use_temp_store
def test_create_profile_invalid_email():
    svc = ProfileService()
    try:
        svc.create_profile("Bob", "bob@gmail.com")
        assert False, "Expected ValidationError"
    except ValidationError:
        pass


@use_temp_store
def test_add_course_and_no_duplicates():
    svc = ProfileService()
    svc.create_profile("Carol", "carol@clemson.edu")
    svc.add_course("carol@clemson.edu", "CPSC 3720")
    svc.add_course("carol@clemson.edu", "CPSC3720")  # duplicate variant
    courses = svc.list_courses("carol@clemson.edu")
    assert courses == ["CPSC 3720"]


@use_temp_store
def test_invalid_course_code():
    svc = ProfileService()
    svc.create_profile("Dan", "dan@clemson.edu")
    try:
        svc.add_course("dan@clemson.edu", "3720 CPSC")
        assert False, "Expected ValidationError"
    except ValidationError:
        pass

@use_temp_store
def test_add_availability_success():
    """Test adding a single, valid availability slot."""
    ProfileService().create_profile("Eve", "eve@clemson.edu")
    svc = AvailabilityService()
    slots = svc.add_slot("eve@clemson.edu", "Mon", "9:00am", "11:00am")
    assert len(slots) == 1
    assert slots[0].day == "MON"
    assert slots[0].start == "09:00"
    assert slots[0].end == "11:00"

@use_temp_store
def test_add_availability_merges_overlapping_slots():
    """Test that two overlapping slots are merged into one."""
    ProfileService().create_profile("Frank", "frank@clemson.edu")
    svc = AvailabilityService()
    svc.add_slot("frank@clemson.edu", "Tue", "1:00pm", "3:00pm")
    slots = svc.add_slot("frank@clemson.edu", "Tue", "2:00pm", "4:00pm") # Overlaps
    assert len(slots) == 1
    assert slots[0].day == "TUE"
    assert slots[0].start == "13:00"
    assert slots[0].end == "16:00"

@use_temp_store
def test_add_availability_merges_adjacent_slots():
    """Test that two adjacent (touching) slots are merged."""
    ProfileService().create_profile("Grace", "grace@clemson.edu")
    svc = AvailabilityService()
    svc.add_slot("grace@clemson.edu", "Wed", "09:00", "10:00")
    slots = svc.add_slot("grace@clemson.edu", "Wed", "10:00", "11:00") # Adjacent
    assert len(slots) == 1
    assert slots[0].day == "WED"
    assert slots[0].start == "09:00"
    assert slots[0].end == "11:00"

@use_temp_store
def test_add_availability_keeps_separate_slots():
    """Test that two separate slots on the same day remain separate."""
    ProfileService().create_profile("Heidi", "heidi@clemson.edu")
    svc = AvailabilityService()
    svc.add_slot("heidi@clemson.edu", "Thu", "9am", "10am")
    slots = svc.add_slot("heidi@clemson.edu", "Thu", "2pm", "3pm") # Separate
    assert len(slots) == 2
    assert slots[0].start == "09:00"
    assert slots[0].end == "10:00"
    assert slots[1].start == "14:00"
    assert slots[1].end == "15:00"

@use_temp_store
def test_add_availability_invalid_time_range():
    """Test that an error is raised if end time is not after start time."""
    ProfileService().create_profile("Ivan", "ivan@clemson.edu")
    svc = AvailabilityService()
    with pytest.raises(ValidationError, match="End time must be after start time"):
        svc.add_slot("ivan@clemson.edu", "Fri", "14:00", "13:00")

@use_temp_store
def test_list_and_remove_availability():
    """Test listing slots in sorted order and removing one by index."""
    ProfileService().create_profile("Judy", "judy@clemson.edu")
    svc = AvailabilityService()
    svc.add_slot("judy@clemson.edu", "Mon", "10:00", "11:00") # 2nd
    svc.add_slot("judy@clemson.edu", "Sun", "15:00", "16:00") # 3rd
    svc.add_slot("judy@clemson.edu", "Mon", "09:00", "09:30") # 1st

    # Test listing (should be sorted by day, then time)
    slots = svc.list_slots("judy@clemson.edu")
    assert len(slots) == 3
    assert slots[0].start == "09:00"
    assert slots[1].start == "10:00"
    assert slots[2].day == "SUN"

    # Test removing the middle slot (Mon 10:00-11:00)
    remaining_slots = svc.remove_slot("judy@clemson.edu", index=2)
    assert len(remaining_slots) == 2
    assert remaining_slots[0].start == "09:00" # First slot remains
    assert remaining_slots[1].day == "SUN"   # Third slot is now second

@use_temp_store
def test_remove_availability_invalid_index():
    """Test that removing an out-of-bounds index raises an error."""
    ProfileService().create_profile("Ken", "ken@clemson.edu")
    svc = AvailabilityService()
    svc.add_slot("ken@clemson.edu", "Sat", "10:00", "11:00")
    
    with pytest.raises(ValidationError, match="Index out of range"):
        svc.remove_slot("ken@clemson.edu", index=0) # Index too low
        
    with pytest.raises(ValidationError, match="Index out of range"):
        svc.remove_slot("ken@clemson.edu", index=2) # Index too high

def use_temp_stores(func):
    """Decorator to isolate both user and session storage for a test."""
    def wrapper():
        with tempfile.TemporaryDirectory() as d:
            users_path = os.path.join(d, "users.json")
            sessions_path = os.path.join(d, "sessions.json")
            os.environ["STUDYBUDDY_DATA_PATH"] = users_path
            os.environ["STUDYBUDDY_SESSIONS_PATH"] = sessions_path
            try:
                func()
            finally:
                os.environ.pop("STUDYBUDDY_DATA_PATH", None)
                os.environ.pop("STUDYBUDDY_SESSIONS_PATH", None)
    return wrapper

# --- Helper function to set up a common scenario for tests ---

def _setup_search_and_session_scenario():
    """Creates Alice, Bob, and Charlie with specific courses and availability."""
    ps = ProfileService()
    avs = AvailabilityService()

    # Alice: CPSC 3720, available Mon 9-11am
    ps.create_profile("Alice", "alice@clemson.edu")
    ps.add_course("alice@clemson.edu", "CPSC 3720")
    avs.add_slot("alice@clemson.edu", "Mon", "9:00", "11:00")

    # Bob: CPSC 3720, available Mon 10am-12pm (overlaps 10-11 with Alice)
    ps.create_profile("Bob", "bob@clemson.edu")
    ps.add_course("bob@clemson.edu", "CPSC 3720")
    avs.add_slot("bob@clemson.edu", "Mon", "10:00", "12:00")

    # Charlie: MATH 2060, different course
    ps.create_profile("Charlie", "charlie@clemson.edu")
    ps.add_course("charlie@clemson.edu", "MATH 2060")
    avs.add_slot("charlie@clemson.edu", "Mon", "9:00", "10:00")


# --- Tests for SearchService (User Story 3) ---

@use_temp_stores
def test_search_classmates_in_course():
    """Test finding classmates in the same course, excluding self and others."""
    _setup_search_and_session_scenario()
    svc = SearchService()
    
    # Alice should find Bob in CPSC 3720, but not Charlie or herself
    classmates = svc.classmates_in_course("alice@clemson.edu", "CPSC 3720")
    assert len(classmates) == 1
    assert classmates[0].email == "bob@clemson.edu"

    # Search should be case-insensitive and handle spacing
    classmates_variant = svc.classmates_in_course("alice@clemson.edu", "cpsc3720")
    assert len(classmates_variant) == 1
    
    # Alice, when searching MATH 2060, should find Charlie
    math_classmates = svc.classmates_in_course("alice@clemson.edu", "MATH 2060")
    assert len(math_classmates) == 1
    assert math_classmates[0].email == "charlie@clemson.edu"


@use_temp_stores
def test_search_overlap_with_classmates():
    """Test calculating the overlapping availability between two users."""
    _setup_search_and_session_scenario()
    svc = SearchService()

    # Alice (9-11) and Bob (10-12) overlap on Mon from 10-11 (60 min)
    overlaps = svc.overlap_with_classmates("alice@clemson.edu", "CPSC 3720")
    assert len(overlaps) == 1
    
    bob_overlap = overlaps[0]
    assert bob_overlap["email"] == "bob@clemson.edu"
    assert bob_overlap["total_minutes"] == 60
    assert "MON" in bob_overlap["overlaps"]
    
    mon_slots = bob_overlap["overlaps"]["MON"]
    assert len(mon_slots) == 1
    start, end, duration = mon_slots[0]
    assert start == "10:00 AM"
    assert end == "11:00 AM"
    assert duration == 60


# --- Tests for SessionService (User Story 4) ---

@use_temp_stores
def test_propose_and_respond_to_session_success():
    """Test the full lifecycle: propose, check requests, accept, and confirm."""
    _setup_search_and_session_scenario()
    svc = SessionService()

    # 1. Alice proposes a session to Bob within their overlap
    session = svc.propose(
        requester="alice@clemson.edu",
        invitee="bob@clemson.edu",
        course="CPSC 3720",
        day="Mon",
        start="10:15",
        end="10:45",
        message="Let's review the rubric"
    )
    assert session.id == 1
    assert session.status == "pending"

    # 2. Check pending requests
    assert len(svc.incoming_requests("bob@clemson.edu")) == 1
    assert len(svc.outgoing_requests("alice@clemson.edu")) == 1
    assert len(svc.incoming_requests("alice@clemson.edu")) == 0

    # 3. Bob accepts the request
    svc.respond(session_id=1, responder_email="bob@clemson.edu", action="accept")
    
    # 4. Verify the session is now confirmed for both
    alice_confirmed = svc.confirmed_sessions("alice@clemson.edu")
    bob_confirmed = svc.confirmed_sessions("bob@clemson.edu")
    assert len(alice_confirmed) == 1
    assert len(bob_confirmed) == 1
    assert alice_confirmed[0].id == 1
    assert alice_confirmed[0].status == "accepted"

    # 5. Verify pending requests are cleared
    assert len(svc.incoming_requests("bob@clemson.edu")) == 0

@use_temp_stores
def test_propose_session_fails_if_unavailable():
    """Test that proposals fail if the time is outside a user's availability."""
    _setup_search_and_session_scenario()
    svc = SessionService()
    
    # Fail because Bob is not available at 9:00 AM
    with pytest.raises(ValidationError, match="Invitee not available"):
        svc.propose("alice@clemson.edu", "bob@clemson.edu", "CPSC 3720", "Mon", "9:00", "10:00")

    # Fail because Alice is not available at 11:30 AM
    with pytest.raises(ValidationError, match="Requester not available"):
        svc.propose("alice@clemson.edu", "bob@clemson.edu", "CPSC 3720", "Mon", "11:00", "11:30")

@use_temp_stores
def test_propose_session_fails_if_not_in_course():
    """Test that proposals fail if users don't share the specified course."""
    _setup_search_and_session_scenario()
    svc = SessionService()
    
    with pytest.raises(ValidationError, match="Both users must be enrolled"):
        svc.propose("alice@clemson.edu", "charlie@clemson.edu", "CPSC 3720", "Mon", "9:15", "9:45")

@use_temp_stores
def test_respond_to_session_permission_denied():
    """Test that only the designated invitee can respond to a request."""
    _setup_search_and_session_scenario()
    svc = SessionService()
    svc.propose("alice@clemson.edu", "bob@clemson.edu", "CPSC 3720", "Mon", "10:30", "11:00")

    # Fail because Alice (the requester) cannot accept her own request
    with pytest.raises(ValidationError, match="Only invitee can respond"):
        svc.respond(session_id=1, responder_email="alice@clemson.edu", action="accept")
        
    # Fail because Charlie (a third party) cannot accept
    with pytest.raises(ValidationError, match="Only invitee can respond"):
        svc.respond(session_id=1, responder_email="charlie@clemson.edu", action="accept")

