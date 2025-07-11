import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, setup_db):
    user_data = {
        "name": "TestClient",
        "surname": "ClientTest",
        "email": "testClient@example.com",
        "age": 34,
        "phone": "+375298888889",
        "role": "user",
        "password": "secure_password"
    }

    response = await client.post("/users/", json=user_data)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == user_data["name"]


@pytest.mark.asyncio
async def test_health_check(client):
     response = await client.get("/healthcheck/")
     assert response.status_code == 200
     assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_user_invalid_data(client):
    invalid_user_data = {"name": "", "surname": "", "email": "", "password": ""}

    response = await client.post("/users/", json=invalid_user_data)

    assert response.status_code == 422  # Expecting Unprocessable Entity
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_create_user_missing_required_field(client: AsyncClient):
    valid_user_data = {
        "name": "TestClient",
        "surname": "Test",
        "email": "test@example.com",
        "age": 34,
        "phone": "+375298888888",
        "role": "user",
        "password": "secure_password"
    }

    await client.post("/users/", json=valid_user_data)

    invalid_data = valid_user_data.copy()
    del invalid_data["name"]  # Удаляем обязательное поле

    response = await client.post("/users/", json=invalid_data)

    assert response.status_code == 409
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_create_user_invalid_age(client: AsyncClient):
    valid_user_data_2 = {
        "name": "TestClient",
        "surname": "Test",
        "email": "test@example.com",
        "age": 34,
        "phone": "+375298888888",
        "role": "user"
    }
    invalid_data = valid_user_data_2.copy()
    invalid_data["age"] = -5

    response = await client.post("/users/", json=invalid_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("age" in error["loc"] for error in errors)


@pytest.mark.asyncio
async def test_create_user_duplicate(client: AsyncClient):
    # First user creation
    response1 = await client.post("/users/", json={
        "id": "d8eaa409-15b7-48e4-a634-64ef112957b1",
        "name": "John",
        "surname": "Doe",
        "email": "test@example.com",
        "age": 30,
        "phone": "+375298888888",
        "role": "user",
        "password": "secure_password"  # Include password if it's required
    })
    assert response1.status_code == 200

    response2 = await client.post("/users/", json={
        "id": "d8eaa409-15b7-48e4-a634-64ef112957b1",
        "name": "John",
        "surname": "Doe",
        "email": "test@example.com",
        "age": 30,
        "phone": "+375298888888",
        "role": "user",
        "password": "secure_password"
    })

    assert response2.status_code == 409
