import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_doctor(client: AsyncClient, db_session: AsyncSession):
    doctor_data = {
        "name": "TestDoctor",
        "surname": "Test",
        "age": 34,
        "specialization": "travm",
        "category": "first",
        "password": "password"
    }

    response = await client.post("/doctors/", json=doctor_data)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == doctor_data["name"]


@pytest.mark.asyncio
async def test_create_doctor_invalid_data(client):
    invalid_doctor_data = {"name": "", "specialization": ""}
    response = await client.post("/doctors/", json=invalid_doctor_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_doctor_missing_required_field(client: AsyncClient):
    valid_doctor_data = {
        "name": "John",
        "surname": "Doe",
        "age": 35,
        "specialization": "Cardiology",
        "category": "first",
        "password": "string"
    }
    invalid_data = valid_doctor_data.copy()
    del invalid_data["name"]  # Удаляем обязательное поле

    response = await client.post("/doctors/", json=invalid_data)
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_create_doctor_invalid_age(client: AsyncClient):
    valid_doctor_data = {
        "name": "John",
        "surname": "Doe",
        "age": 35,
        "specialization": "Cardiology",
        "category": "first",
        "password": "string"
    }
    invalid_data = valid_doctor_data.copy()
    invalid_data["age"] = -5

    response = await client.post("/doctors/", json=invalid_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("age" in error["loc"] for error in errors)


@pytest.mark.asyncio
async def test_create_doctor_short_password(client: AsyncClient):
    valid_doctor_data = {
        "name": "John",
        "surname": "Doe",
        "age": 35,
        "specialization": "Cardiology",
        "category": "first",
        "password": "string"
    }
    invalid_data = valid_doctor_data.copy()
    invalid_data["password"] = "123"  # Слишком короткий пароль

    response = await client.post("/doctors/", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_doctor_duplicate(client):
    response1 = await client.post("/doctors/", json={"id": "d8eaa409-15b7-48e4-a634-64ef112957b1", "name": "John", "surname": "Doe", "age": 30, "specialization": "Cardiology", "category": "first", "password": "password"})
    assert response1.status_code == 200

    response2 = await client.post("/doctors/", json={"id": "d8eaa409-15b7-48e4-a634-64ef112957b1", "name": "Jane", "surname": "Doe", "age": 28, "specialization": "Cardiology", "category": "first", "password": "password"})
    assert response2.status_code == 409  # ошибка при дублировании