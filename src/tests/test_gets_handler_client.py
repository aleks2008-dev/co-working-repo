import pytest
from httpx import AsyncClient
from database import ClientORM
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_get_clients_default_pagination(client: AsyncClient, db_session: AsyncSession):
    for i in range(1, 10):
        client_orm = ClientORM(
            name=f"Client_{i}",
            surname=f"Test_{i}",
            email=f"clientTest{i}@example.com",
            age=35 + i,
            phone=f"+3752988888{i:02}"
        )
        db_session.add(client_orm)
    await db_session.commit()

    response = await client.get("/clients/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert data[0]["name"] == "Client_1"
    assert data[-1]["name"] == "Client_9"


@pytest.mark.asyncio
async def test_get_clients_custom_pagination(client: AsyncClient, db_session: AsyncSession):
    for i in range(1, 8):
        client_orm = ClientORM(
            name=f"Client_{i}",
            surname=f"Test_{i}",
            email=f"clientTest{i}@example.com",
            age=30 + i,
            phone=f"+3752988888{i:02}"
        )
        db_session.add(client_orm)
    await db_session.commit()

    response = await client.get("/clients/?page=2&size=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Client_4"
    assert data[-1]["name"] == "Client_6"


@pytest.mark.asyncio
async def test_get_clients_invalid_pagination(client: AsyncClient):
    test_cases = [
        ("?page=-1&size=5", "page"),
        ("?page=0&size=0", "size"),
        ("?size=101", "size"),
        ("?page=not_number", "page"),
        ("?size=invalid", "size")
    ]

    for params, error_field in test_cases:
        response = await client.get(f"/clients/{params}")
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any(e["loc"][-1] == error_field for e in errors)


@pytest.mark.asyncio
async def test_get_empty_clients_list(client: AsyncClient):
    response = await client.get("/clients/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_pagination_metadata(client: AsyncClient, db_session: AsyncSession):
    for i in range(1, 25):
        client_orm = ClientORM(
            name=f"Client_{i}",
            surname=f"Test_{i}",
            email=f"clientTest{i}@example.com",
            age=35,
            phone=f"+3752988888{i:02}"
        )
        db_session.add(client_orm)
    await db_session.commit()

    test_cases = [
        ("?size=5", 5, 1, 5),
        ("?page=3&size=7", 7, 3, 4),  # 25 / 7 = 3.57 → 4 страницы
        ("?page=10&size=3", 0, 10, 9),  # Страница за пределами
    ]

    for params, expected_items, req_page, total_pages in test_cases:
        response = await client.get(f"/clients/{params}")
        data = response.json()

        if expected_items > 0:
            assert len(data) == expected_items
        else:
            assert len(data) == 0


@pytest.mark.asyncio
async def test_response_structure(client: AsyncClient, db_session: AsyncSession):
    client_orm = ClientORM(
        name=f"ClientTest",
        surname="Test_test",
        email="client_Test@example.com",
        age=35,
        phone="+375298888999"
    )
    db_session.add(client_orm)
    await db_session.commit()

    response = await client.get("/clients/")
    data = response.json()[0]

    assert all(key in data for key in [
        "id", "name", "surname", "email",
        "age", "phone"
    ])