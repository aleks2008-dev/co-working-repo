from database import ClientORM
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_delete_existing_client(client: AsyncClient, db_session: AsyncSession):
    test_client = ClientORM(
        name="Robert",
        surname="Duglas",
        email="clientTest@example.com",
        age=35,
        phone="+375298888899"
    )
    db_session.add(test_client)
    await db_session.commit()
    await db_session.refresh(test_client)

    response = await client.delete(f"/clients/{test_client.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Client deleted"}

    # Проверяем что клиент удален из БД
    result = await db_session.execute(select(ClientORM).where(ClientORM.id == test_client.id))
    assert result.scalars().first() is None


@pytest.mark.asyncio
async def test_delete_nonexistent_client(client: AsyncClient):
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/clients/{non_existent_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found"


@pytest.mark.asyncio
async def test_delete_client_invalid_id_format(client: AsyncClient):
    response = await client.delete("/clients/invalid_id")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert any(error["type"] == "uuid_parsing" for error in errors)


@pytest.mark.asyncio
async def test_delete_client_twice(client: AsyncClient, db_session: AsyncSession):
    test_client = ClientORM(
        name="Robert",
        surname="Duglas",
        email="clientTest@example.com",
        age=35,
        phone="+375298888899"
    )
    db_session.add(test_client)
    await db_session.commit()
    await db_session.refresh(test_client)

    response = await client.delete(f"/clients/{test_client.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Client deleted"}

    response2 = await client.delete(f"/clients/{test_client.id}")
    assert response2.status_code == 404