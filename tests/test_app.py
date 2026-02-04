import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    client = TestClient(app)
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Soccer Team" in data


def test_signup_success():
    client = TestClient(app)
    email = "testuser@example.com"
    r = client.post(f"/activities/Soccer%20Team/signup?email={email}")
    assert r.status_code == 200
    assert email in activities["Soccer Team"]["participants"]


def test_signup_duplicate():
    client = TestClient(app)
    # liam@mergington.edu is already in the initial sample data
    email = "liam@mergington.edu"
    r = client.post(f"/activities/Soccer%20Team/signup?email={email}")
    assert r.status_code == 400


def test_signup_activity_not_found():
    client = TestClient(app)
    email = "a@b.com"
    r = client.post(f"/activities/UnknownActivity/signup?email={email}")
    assert r.status_code == 404


def test_unregister_success():
    client = TestClient(app)
    email = "remove_me@example.com"
    # sign up first
    r1 = client.post(f"/activities/Soccer%20Team/signup?email={email}")
    assert r1.status_code == 200

    # then unregister
    r2 = client.post(f"/activities/Soccer%20Team/unregister?email={email}")
    assert r2.status_code == 200
    assert email not in activities["Soccer Team"]["participants"]


def test_unregister_not_enrolled():
    client = TestClient(app)
    email = "not_enrolled@example.com"
    r = client.post(f"/activities/Soccer%20Team/unregister?email={email}")
    assert r.status_code == 400


def test_unregister_activity_not_found():
    client = TestClient(app)
    email = "a@b.com"
    r = client.post(f"/activities/NoSuchActivity/unregister?email={email}")
    assert r.status_code == 404


def test_manga_maniacs_exists():
    """Test that Manga Maniacs club is present in the activities"""
    client = TestClient(app)
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Manga Maniacs" in data
    assert data["Manga Maniacs"]["description"] == "Explore the fantastic stories of the most interesting characters from Japanese Manga (graphic novels)."
    assert data["Manga Maniacs"]["schedule"] == "Tuesdays at 7pm"
    assert data["Manga Maniacs"]["max_participants"] == 15
    assert data["Manga Maniacs"]["participants"] == []
