import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database import UserORM


@pytest.mark.asyncio
async def test_update_user_success(client: AsyncClient, db_session: AsyncSession):
    user_orm = UserORM(
        name="John",
        surname="Doe",
        email="clientTest@example.com",
        age=40,
        phone="+375297777777",
        role="user",
        password="password",
        disabled=False
    )
    db_session.add(user_orm)
    await db_session.commit()
    await db_session.refresh(user_orm)

    update_data = {"name": "Michael", "age": 45}
    response = await client.patch(
        f"/users/{user_orm.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Michael"
    assert data["age"] == 45
    assert data["surname"] == "Doe"

    await db_session.refresh(user_orm)
    assert user_orm.name == "Michael"
    assert user_orm.age == 45


@pytest.mark.asyncio
async def test_update_nonexistent_user(client: AsyncClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.patch(
        f"/users/{fake_id}",
        json={"name": "Test"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_partial_update(client: AsyncClient, db_session: AsyncSession):
    user_orm = UserORM(
        name="John",
        surname="Doe",
        email="clientTest@example.com",
        age=40,
        phone="+375297777777",
        role="user",
        password="password",
        disabled=False
    )
    db_session.add(user_orm)
    await db_session.commit()
    await db_session.refresh(user_orm)

    response = await client.patch(
        f"/users/{user_orm.id}",
        json={"age": 40 }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 40
    assert data["phone"] == "+375297777777"


@pytest.mark.asyncio
async def test_invalid_data_update(client: AsyncClient, db_session: AsyncSession):
    user_orm = UserORM(
        name="John",
        surname="Doe",
        email="clientTest@example.com",
        age=40,
        phone="+375297777777",
        role="user",
        password="password",
        disabled=False
    )
    db_session.add(user_orm)
    await db_session.commit()
    await db_session.refresh(user_orm)

    response = await client.patch(
        f"/users/{user_orm.id}",
        json={"age": "fifty"}
    )

    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any(
        e["loc"] == ["body", "age"]
        for e in error_detail
    ), "Ошибка должна указывать на невалидное поле age"
