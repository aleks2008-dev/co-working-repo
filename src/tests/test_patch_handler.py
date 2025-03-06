import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from database import DoctorORM


@pytest.mark.asyncio
async def test_update_doctor_success(client: AsyncClient, db_session: AsyncSession):
    doctor = DoctorORM(
        name="John",
        surname="Doe",
        age=40,
        specialization="Cardiology",
        category="first",
        password="secret"
    )
    db_session.add(doctor)
    await db_session.commit()
    await db_session.refresh(doctor)

    update_data = {"name": "Michael", "age": 45}
    response = await client.patch(
        f"/doctors/{doctor.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Michael"
    assert data["age"] == 45
    assert data["surname"] == "Doe"

    await db_session.refresh(doctor)
    assert doctor.name == "Michael"
    assert doctor.age == 45


@pytest.mark.asyncio
async def test_update_nonexistent_doctor(client: AsyncClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.patch(
        f"/doctors/{fake_id}",
        json={"name": "Test"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Doctor not found"}


@pytest.mark.asyncio
async def test_partial_update(client: AsyncClient, db_session: AsyncSession):
    doctor = DoctorORM(
        name="Alice",
        surname="Smith",
        age=35,
        specialization="Neurology",
        category="second",
        password="pass"
    )
    db_session.add(doctor)
    await db_session.commit()
    await db_session.refresh(doctor)

    response = await client.patch(
        f"/doctors/{doctor.id}",
        json={"specialization": "Pediatrics"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["specialization"] == "Pediatrics"
    assert data["age"] == 35


@pytest.mark.asyncio
async def test_invalid_data_update(client: AsyncClient, db_session: AsyncSession):
    doctor = DoctorORM(
        name="Bob",
        surname="Brown",
        age=50,
        specialization="Surgery",
        category="first",
        password="qwerty"
    )
    db_session.add(doctor)
    await db_session.commit()
    await db_session.refresh(doctor)

    response = await client.patch(
        f"/doctors/{doctor.id}",
        json={"age": "fifty"}
    )

    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any(
        e["loc"] == ["body", "age"]
        for e in error_detail
    ), "Ошибка должна указывать на невалидное поле age"


@pytest.mark.asyncio
async def test_update_password_ignored(client: AsyncClient, db_session: AsyncSession):
    doctor = DoctorORM(
        name="Eve",
        surname="Wilson",
        age=28,
        specialization="Dermatology",
        category="first",
        password="original"
    )
    db_session.add(doctor)
    await db_session.commit()
    await db_session.refresh(doctor)

    response = await client.patch(
        f"/doctors/{doctor.id}",
        json={"password": "new_password"}
    )

    assert response.status_code == 200
    assert "password" not in response.json()

    await db_session.refresh(doctor)
    assert doctor.password == "original"