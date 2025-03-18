import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_client(client: AsyncClient, setup_db):
    client_data = {
        "name": "TestClient",
        "surname": "ClientTest",
        "email": "testClient@example.com",
        "age": 34,
        "phone": "+375298888889"
    }

    response = await client.post("/clients/", json=client_data)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == client_data["name"]

@pytest.mark.asyncio
async def test_health_check(client):
     response = await client.get("/healthcheck/")
     assert response.status_code == 200
     assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_create_client_invalid_data(client):
    invalid_client_data = {"name": "", "surname": ""}
    response = await client.post("/clients/", json=invalid_client_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_client_missing_required_field(client: AsyncClient):
    valid_client_data = {
        "name": "TestClient",
        "surname": "Test",
        "email": "test@example.com",
        "age": 34,
        "phone": "+375298888888"
    }
    invalid_data = valid_client_data.copy()
    del invalid_data["name"]  # Удаляем обязательное поле

    response = await client.post("/clients/", json=invalid_data)
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_create_client_invalid_age(client: AsyncClient):
    valid_client_data_2 = {
        "name": "TestClient",
        "surname": "Test",
        "email": "test@example.com",
        "age": 34,
        "phone": "+375298888888"
    }
    invalid_data = valid_client_data_2.copy()
    invalid_data["age"] = -5

    response = await client.post("/clients/", json=invalid_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("age" in error["loc"] for error in errors)


@pytest.mark.asyncio
async def test_create_client_duplicate(client):
    response1 = await client.post("/clients/", json={"id": "d8eaa409-15b7-48e4-a634-64ef112957b1", "name": "John", "surname": "Doe", "email": "test@example.com", "age": 30, "phone": "+375298888888"})
    assert response1.status_code == 200

    response2 = await client.post("/clients/", json={"id": "d8eaa409-15b7-48e4-a634-64ef112957b1", "name": "John", "surname": "Doe", "email": "test@example.com", "age": 30, "phone": "+375298888888"})
    assert response2.status_code == 409  # ошибка при дублировании