import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from database import ClientORM


@pytest.mark.asyncio
async def test_get_existing_client(client: AsyncClient, db_session: AsyncSession):
    client_data = {
        "id": "d8eaa409-15b7-48e4-a634-64ef112957b1",
        "name": "TestClient",
        "surname": "Test",
        "email": "test@example.com",
        "age": 34,
        "phone": "+375298888888"
    }

    #Создание через ORM для тестов
    test_client = ClientORM(**client_data)
    db_session.add(test_client)
    await db_session.commit()
    await db_session.refresh(test_client)

    response = await client.get(f"/clients/{test_client.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_client.id)
    assert data["name"] == "TestClient"
    assert data["surname"] == "Test"


@pytest.mark.asyncio
async def test_get_nonexistent_client(client: AsyncClient):
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/clients/{non_existent_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found"


@pytest.mark.asyncio
async def test_get_client_invalid_id_format(client: AsyncClient):
    response = await client.get("/clients/invalid_id_format")

    assert response.status_code == 422
    errors = response.json()["detail"]

    assert any(
        "uuid" in error["msg"].lower() or
        "valid" in error["msg"].lower()
        for error in errors
    ), "Expected UUID validation error"