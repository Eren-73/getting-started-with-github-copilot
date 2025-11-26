from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before each test to avoid cross-test pollution."""
    original = deepcopy(app_module.activities)
    try:
        yield
    finally:
        app_module.activities.clear()
        app_module.activities.update(original)


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities(client):
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Some known activities from the default data
    assert "Chess Club" in data


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    email = "test.student@example.com"

    # Ensure email not present at start
    res = client.get("/activities")
    assert res.status_code == 200
    assert email not in res.json()[activity]["participants"]

    # Signup
    path = f"/activities/{quote(activity)}/signup"
    res = client.post(path, params={"email": email})
    assert res.status_code == 200
    body = res.json()
    assert "Signed up" in body.get("message", "")

    # Ensure participant appears
    res = client.get("/activities")
    assert res.status_code == 200
    assert email in res.json()[activity]["participants"]

    # Unregister
    path = f"/activities/{quote(activity)}/unregister"
    res = client.post(path, params={"email": email})
    assert res.status_code == 200
    body = res.json()
    assert "Unregistered" in body.get("message", "")

    # Ensure participant removed
    res = client.get("/activities")
    assert res.status_code == 200
    assert email not in res.json()[activity]["participants"]
