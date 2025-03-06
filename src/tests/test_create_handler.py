import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_doctor(client: AsyncClient, setup_db):
    doctor_data = {
        "id": "d8eaa409-15b7-48e4-a634-64ef112957b1",
        "name": "TestDoctor",
        "surname": "Test",
        "age": 34,
        "specialization": "travm",
        "category": "first",
        "password": "string"
    }

    response = await client.post("/doctors/", json=doctor_data)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == doctor_data["name"]

@pytest.mark.asyncio
async def test_health_check(client):
     response = await client.get("/healthcheck/")
     assert response.status_code == 200
     assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_create_doctor_invalid_data(client):
    invalid_doctor_data = {"name": "", "specialization": ""}
    response = await client.post("/doctors/", json=invalid_doctor_data)

    assert response.status_code == 422

VALID_DOCTOR_DATA = {
    "name": "John",
    "surname": "Doe",
    "age": 35,
    "specialization": "Cardiology",
    "category": "first",
    "password": "string"
}

@pytest.mark.asyncio
class TestDoctorCreate:
    async def test_create_doctor_missing_required_field(self, client: AsyncClient):
        invalid_data = VALID_DOCTOR_DATA.copy()
        del invalid_data["name"]  # Удаляем обязательное поле

        response = await client.post("/doctors/", json=invalid_data)
        assert response.status_code == 422
        assert "detail" in response.json()

    async def test_create_doctor_invalid_age(self, client: AsyncClient):
        invalid_data = VALID_DOCTOR_DATA.copy()
        invalid_data["age"] = -5

        response = await client.post("/doctors/", json=invalid_data)
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("age" in error["loc"] for error in errors)

    async def test_create_doctor_short_password(self, client: AsyncClient):
        invalid_data = VALID_DOCTOR_DATA.copy()
        invalid_data["password"] = "123"  # Слишком короткий пароль

        response = await client.post("/doctors/", json=invalid_data)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_doctor_duplicate(client):
    response1 = await client.post("/doctors/", json={"id": "d8eaa409-15b7-48e4-a634-64ef112957b1", "name": "John", "surname": "Doe", "age": 30, "specialization": "Cardiology", "category": "first", "password": "password"})
    assert response1.status_code == 200

    response2 = await client.post("/doctors/", json={"id": "d8eaa409-15b7-48e4-a634-64ef112957b1", "name": "Jane", "surname": "Doe", "age": 28, "specialization": "Cardiology", "category": "first", "password": "password"})
    assert response2.status_code == 409  # ошибка при дублировании