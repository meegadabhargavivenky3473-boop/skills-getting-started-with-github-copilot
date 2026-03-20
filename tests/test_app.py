import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_initial_data():
    response = client.get("/activities")
    assert response.status_code == 200
    result = response.json()

    assert "Chess Club" in result
    assert "Programming Class" in result
    assert result["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant_and_prevents_duplicates():
    email = "testnew@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    response = client.get("/activities")
    assert response.status_code == 200
    participants = response.json()["Chess Club"]["participants"]
    assert email in participants

    # duplicate signup prevented
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_success_and_not_found():
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess Club/participants?email={email}")
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]

    response = client.get("/activities")
    assert email not in response.json()["Chess Club"]["participants"]

    # removing again returns 404
    response = client.delete(f"/activities/Chess Club/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_activity_not_found_sign_up_and_remove():
    response = client.post("/activities/Unknown/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

    response = client.delete("/activities/Unknown/participants?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
