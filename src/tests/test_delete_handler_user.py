import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import UserORM


@pytest.mark.asyncio
async def test_delete_existing_user(client: AsyncClient, db_session: AsyncSession):
    test_user = UserORM(
        name="Robert",
        surname="Duglas",
        email="clientTest@example.com",
        age=35,
        phone="+375298888899",
        role = "user",
        password = "password",
        disabled = False
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)

    response = await client.delete(f"/users/{test_user.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "User deleted"}

    result = await db_session.execute(select(UserORM).where(UserORM.id == test_user.id))
    assert result.scalars().first() is None


@pytest.mark.asyncio
async def test_delete_nonexistent_user(client: AsyncClient):
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/users/{non_existent_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_user_invalid_id_format(client: AsyncClient):
    response = await client.delete("/users/invalid_id")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert any(error["type"] == "uuid_parsing" for error in errors)


@pytest.mark.asyncio
async def test_delete_user_twice(client: AsyncClient, db_session: AsyncSession):
    test_user = UserORM(
        name="Robert",
        surname="Duglas",
        email="clientTest@example.com",
        age=35,
        phone="+375298888899",
        role = "user",
        password = "password",
        disabled = False
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)

    response = await client.delete(f"/users/{test_user.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "User deleted"}

    response2 = await client.delete(f"/users/{test_user.id}")

    assert response2.status_code == 404
    assert response2.json() == {"detail": "User not found"}
