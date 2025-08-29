import os
import tempfile
import json
import pytest

from studybuddy.profile_service import ProfileService, ValidationError
from studybuddy.availability_service import AvailabilityService
from studybuddy import storage


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
