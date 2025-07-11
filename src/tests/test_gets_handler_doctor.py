import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database import DoctorORM


@pytest.mark.asyncio
async def test_get_doctors_default_pagination(client: AsyncClient, db_session: AsyncSession):
    for i in range(1, 10):
        doctor = DoctorORM(
            name=f"Doctor_{i}",
            surname=f"Test_{i}",
            age=30 + i,
            specialization="General",
            category="first",
            password="password"
        )
        db_session.add(doctor)
    await db_session.commit()

    response = await client.get("/doctors/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert data[0]["name"] == "Doctor_1"
    assert data[-1]["name"] == "Doctor_9"


@pytest.mark.asyncio
async def test_get_doctors_custom_pagination(client: AsyncClient, db_session: AsyncSession):
    for i in range(1, 8):
        doctor = DoctorORM(
            name=f"Doctor_{i}",
            surname=f"Test_{i}",
            age=30 + i,
            specialization="General",
            category="first",
            password="password"
        )
        db_session.add(doctor)
    await db_session.commit()

    response = await client.get("/doctors/?page=2&size=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Doctor_4"
    assert data[-1]["name"] == "Doctor_6"


@pytest.mark.asyncio
async def test_get_doctors_invalid_pagination(client: AsyncClient):
    test_cases = [
        ("?page=-1&size=5", "page"),
        ("?page=0&size=0", "size"),
        ("?size=101", "size"),
        ("?page=not_number", "page"),
        ("?size=invalid", "size")
    ]

    for params, error_field in test_cases:
        response = await client.get(f"/doctors/{params}")
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any(e["loc"][-1] == error_field for e in errors)


@pytest.mark.asyncio
async def test_get_empty_doctors_list(client: AsyncClient):
    response = await client.get("/doctors/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_pagination_metadata(client: AsyncClient, db_session: AsyncSession):
    for i in range(1, 25):
        doctor = DoctorORM(
            name=f"Doctor_{i}",
            surname=f"Test_{i}",
            age=30 + i,
            specialization="General",
            category="first",
            password="password"
        )
        db_session.add(doctor)
    await db_session.commit()

    test_cases = [
        ("?size=5", 5, 1, 5),
        ("?page=3&size=7", 7, 3, 4),  # 25 / 7 = 3.57 → 4 страницы
        ("?page=10&size=3", 0, 10, 9),  # Страница за пределами
    ]

    for params, expected_items, _req_page, _total_pages in test_cases:
        response = await client.get(f"/doctors/{params}")
        data = response.json()

        if expected_items > 0:
            assert len(data) == expected_items
        else:
            assert len(data) == 0


@pytest.mark.asyncio
async def test_response_structure(client: AsyncClient, db_session: AsyncSession):
    doctor = DoctorORM(
        name="Doctor",
        surname="Test",
        age=30,
        specialization="General",
        category="first",
        password="password"
    )
    db_session.add(doctor)
    await db_session.commit()

    response = await client.get("/doctors/")
    data = response.json()[0]

    assert "password" not in data
    assert all(key in data for key in [
        "id", "name", "surname", "age",
        "specialization", "category"
    ])
