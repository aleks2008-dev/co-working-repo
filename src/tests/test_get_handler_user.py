import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from database import UserORM


@pytest.mark.asyncio
async def test_get_existing_user(client: AsyncClient, db_session: AsyncSession):
    unique_id = uuid.uuid4()

    user_data = {
        "id": unique_id,
        "name": "TestUser",
        "surname": "Test",
        "email": "test@example.com",
        "age": 34,
        "phone": "+375298888888",
        "role": "user",
        "password": "password",
        "disabled": False
    }

    test_user = UserORM(**user_data)
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)

    response = await client.get(f"/users/{test_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["name"] == "TestUser"
    assert data["surname"] == "Test"


@pytest.mark.asyncio
async def test_get_nonexistent_user(client: AsyncClient):
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/users/{non_existent_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_get_user_invalid_id_format(client: AsyncClient):
    response = await client.get("/users/invalid_id_format")

    assert response.status_code == 422
    errors = response.json()["detail"]

    assert any(
        "uuid" in error["msg"].lower() or
        "valid" in error["msg"].lower()
        for error in errors
    ), "Expected UUID validation error"