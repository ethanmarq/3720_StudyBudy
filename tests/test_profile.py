import os
import tempfile
import json

from studybuddy.profile_service import ProfileService, ValidationError
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
