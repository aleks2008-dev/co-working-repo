from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi import status
from httpx import AsyncClient

from auth import AuthConfig
from database import UserORM
from model import UserRole


@pytest.mark.asyncio
async def test_read_users_unauthenticated(client):
    """Неаутентифицированный пользователь получает 401."""
    response = await client.get("/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_read_users_pagination_valid(client, db_session):
    """Проверка рабочей пагинации."""
    # Создаем тестового пользователя и сразу получаем его ID
    user_id = uuid4()
    user = UserORM(
        id=user_id,
        email="testuser@example.com",
        name="Test",
        surname="User",
        age=30,
        phone="292362323",
        role=UserRole.user,
        password="hashed_password",
        disabled=False
    )
    db_session.add(user)
    await db_session.commit()

    # Создаем токен для аутентификации, используя уже известный ID
    payload = {
        "sub": str(user_id),  # Используем заранее известный ID
        "role": UserRole.user.value,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    token = jwt.encode(payload, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)

    # Создаем еще 14 пользователей для тестирования пагинации
    for i in range(1, 10):
        user = UserORM(
            id=uuid4(),
            email=f"user{i}@example.com",
            name=f"User{i}",
            surname="Test",
            age=20 + i,
            phone=f"29234234{i}",
            role=UserRole.user,
            password=f"hashed_pass_{i}",
            disabled=False
        )
        db_session.add(user)
    await db_session.commit()

    # Делаем запрос с пагинацией
    response = await client.get(
        "/users/?page=1&size=10",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10  # Проверяем размер страницы


@pytest.mark.asyncio
async def test_read_users(client, db_session):
    """Проверка рабочей пагинации."""
    # Создаем тестового пользователя и сразу получаем его ID
    user_id = uuid4()
    user = UserORM(
        id=user_id,
        email="testuser@example.com",
        name="Test",
        surname="User",
        age=30,
        phone="292362323",
        role=UserRole.user,
        password="hashed_password",
        disabled=False
    )
    db_session.add(user)
    await db_session.commit()

    # Создаем токен для аутентификации, используя уже известный ID
    payload = {
        "sub": str(user_id),  # Используем заранее известный ID
        "role": UserRole.user.value,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    token = jwt.encode(payload, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)

    response = await client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_read_users_forbidden_role(client, db_session):
    """Проверка рабочей пагинации."""
    # Создаем тестового пользователя и сразу получаем его ID
    user_id = uuid4()
    user = UserORM(
        id=user_id,
        email="testuser@example.com",
        name="Test",
        surname="User",
        age=30,
        phone="292362323",
        role=UserRole.admin,
        password="hashed_password",
        disabled=False
    )
    db_session.add(user)
    await db_session.commit()

    # Создаем токен для аутентификации, используя уже известный ID
    payload = {
        "sub": str(user_id),  # Используем заранее известный ID
        "role": UserRole.admin.value,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    token = jwt.encode(payload, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)

    response = await client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_no_token_unauthorized(client: AsyncClient):
    """Запрос без токена должен возвращать 401"""
    response = await client.get("/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]


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
