import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from database import DoctorORM


@pytest.mark.asyncio
async def test_get_existing_doctor(client: AsyncClient, db_session: AsyncSession):
    doctor_data = {
        "id": "d8eaa409-15b7-48e4-a634-64ef112957b1",
        "name": "TestDoctor",
        "surname": "Test",
        "age": 34,
        "specialization": "travm",
        "category": "first",
        "password": "string"
    }

    #Создание через ORM для тестов
    test_doctor = DoctorORM(**doctor_data)
    db_session.add(test_doctor)
    await db_session.commit()
    await db_session.refresh(test_doctor)

    response = await client.get(f"/doctors/{test_doctor.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_doctor.id)
    assert data["name"] == "TestDoctor"
    assert data["category"] == "first"


@pytest.mark.asyncio
async def test_get_nonexistent_doctor(client: AsyncClient):
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/doctors/{non_existent_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Doctor not found"


@pytest.mark.asyncio
async def test_get_doctor_invalid_id_format(client: AsyncClient):
    response = await client.get("/doctors/invalid_id_format")

    assert response.status_code == 422
    errors = response.json()["detail"]

    assert any(
        "uuid" in error["msg"].lower() or
        "valid" in error["msg"].lower()
        for error in errors
    ), "Expected UUID validation error"
