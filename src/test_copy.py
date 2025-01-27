from fastapi.testclient import TestClient
from src import crud
from .main import app
import pytest
import json

client = TestClient(app)

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client

def test_get_doctor():
    response = client.get("/doctors/")
    assert response.status_code == 422


def test_read_note_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/notes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

def test_create_hero():
    # Some code here omitted, we will see it later 👈
    client = TestClient(app)

    response = client.post(
        "/heroes/", json={"name": "Deadpond", "secret_name": "Dive Wilson"}
    )
    # Some code here omitted, we will see it later 👈
    data = response.json()

    assert response.status_code == 404
    assert data["name"] == "Deadpond"
    assert data["secret_name"] == "Dive Wilson"
    assert data["age"] is None
    assert data["id"] is not None

def test_create_note_invalid_json(test_app):
    response = test_app.post("/notes/", content=json.dumps({"title": "something"}))
    assert response.status_code == 404