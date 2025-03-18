from database import DoctorORM
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_delete_existing_doctor(client: AsyncClient, db_session: AsyncSession):
    test_doctor = DoctorORM(
        name="John",
        surname="Doe",
        age=35,
        specialization="Cardiology",
        category="first",
        password="hashedpass"
    )
    db_session.add(test_doctor)
    await db_session.commit()
    await db_session.refresh(test_doctor)

    response = await client.delete(f"/doctors/{test_doctor.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Doctor deleted"}

    # Проверяем что врач удален из БД
    result = await db_session.execute(select(DoctorORM).where(DoctorORM.id == test_doctor.id))
    assert result.scalars().first() is None


@pytest.mark.asyncio
async def test_delete_nonexistent_doctor(client: AsyncClient):
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/doctors/{non_existent_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Doctor not found"


@pytest.mark.asyncio
async def test_delete_doctor_invalid_id_format(client: AsyncClient):
    response = await client.delete("/doctors/invalid_id")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert any(error["type"] == "uuid_parsing" for error in errors)


@pytest.mark.asyncio
async def test_delete_doctor_twice(client: AsyncClient, db_session: AsyncSession):
    test_doctor = DoctorORM(
        name="John",
        surname="Doe",
        age=35,
        specialization="Cardiology",
        category="first",
        password="hashedpass"
    )
    db_session.add(test_doctor)
    await db_session.commit()
    await db_session.refresh(test_doctor)

    response = await client.delete(f"/doctors/{test_doctor.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Doctor deleted"}

    response2 = await client.delete(f"/doctors/{test_doctor.id}")
    assert response2.status_code == 404
