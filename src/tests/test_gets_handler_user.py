from datetime import datetime, timezone, timedelta
from uuid import uuid4
import pytest
from fastapi import status
from httpx import AsyncClient
from conftest import client
from model import UserItem, UserRole
from auth import AuthConfig
import jwt
from database import UserORM
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_pagination_works(client: AsyncClient, admin_token: str, test_users):
    """Проверка работы пагинации"""
    # Первая страница (5 пользователей)
    response = await client.get(
    "/users/?page=1&size=5",
    headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert len(response.json()) == 1

    # Вторая страница (5 пользователей)
    response = await client.get(
        "/users/?page=2&size=5",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert len(response.json()) == 1

    # Третья страница (5 пользователей)
    response = await client.get(
    "/users/?page=3&size=5",
    headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_no_token_unauthorized(client: AsyncClient):
    """Запрос без токена должен возвращать 401"""
    response = await client.get("/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]

