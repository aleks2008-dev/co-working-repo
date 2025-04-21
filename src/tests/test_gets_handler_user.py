from select import select

import pytest
from httpx import AsyncClient
from database import UserORM
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

# Тесты на авторизацию
@pytest.mark.asyncio
async def test_get_users_unauthorized(client: AsyncClient):
    response = await client.get("/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_users_forbidden(client: AsyncClient, user_token: str):
    response = await client.get(
        "/users/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Тесты на успешный доступ
@pytest.mark.asyncio
async def test_get_users_success(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK


# Тесты на пагинацию
# @pytest.mark.asyncio
# async def test_pagination_default_params(
#         client: AsyncClient,
#         admin_token: str,
#         session
# ):
#     # Создаем 15 тестовых пользователей с ведущими нулями для правильной сортировки
#     for i in range(1, 16):
#         session.add(UserORM(name=f"User {i:02}", email=f"user{i}@example.com"))  # <-- Исправление формата
#     await session.commit()
#
#
#     response = await client.get(
#         "/users/",
#         headers={"Authorization": f"Bearer {admin_token}"}
#     )
#
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()


# @pytest.mark.asyncio
# async def test_pagination_custom_params(
#         client: AsyncClient,
#         admin_token: str,
#         session
# ):
#     # Создаем 25 тестовых пользователей
#     for i in range(1, 26):
#         session.add(UserORM(name=f"User {i}", email=f"user{i}@example.com"))
#     await session.commit()
#
#     response = await client.get(
#         "/users/?page=2&size=5",
#         headers={"Authorization": f"Bearer {admin_token}"}
#     )
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert len(data) == 5
#     assert data[0]["name"] == "User 6"


# Тесты на валидацию параметров
@pytest.mark.asyncio
async def test_invalid_page_param(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/users/?page=-1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_invalid_size_param(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/users/?size=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = await client.get(
        "/users/?size=101",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Тест структуры ответа
# @pytest.mark.asyncio
# async def test_response_structure(client: AsyncClient, admin_token: str, session: AsyncSession):
#     await session.execute("DELETE FROM users WHERE email='test@example.com'")
#     session.add(UserORM(name="Test User", email="test@example.com"))
#     await session.commit()
#
#     response = await client.get(
#         "/users/",
#         headers={"Authorization": f"Bearer {admin_token}"}
#     )
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#
#     assert isinstance(data, list)
#     assert all(
#         {"id", "name", "email"}.issubset(user.keys())
#         for user in data
#     )