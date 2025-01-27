from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app
# import pytest
# from httpx import ASGITransport, AsyncClient

client = TestClient(app)

# @pytest.mark.anyio
# async def test_root():
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as ac:
#         response = await ac.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Tomato"}


def test_read_items():
    response = client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_item(sample_item):
    client.post("/items/", json=sample_item.dict())
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == sample_item.dict()

def test_read_nonexistent_item():
    response = client.get("/items/999")
    assert response.status_code == 200
    assert response.json() == {"error": "Item not found"}