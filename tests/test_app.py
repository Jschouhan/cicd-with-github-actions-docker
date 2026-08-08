import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "message" in data
    assert data["message"] == "Hello from the CI/CD demo app!"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"


def test_add(client):
    resp = client.get("/add/2/3")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["sum"] == 5


def test_add_negative(client):
    resp = client.get("/add/-4/10")
    assert resp.get_json()["sum"] == 6
