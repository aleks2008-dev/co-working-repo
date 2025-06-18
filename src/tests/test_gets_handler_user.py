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
class TestUsersEndpoint:
    async def test_admin_access_success(self, client: AsyncClient, admin_token: str, test_users):
        """Администратор может получить список пользователей"""
        response = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        assert len(response.json()) == 10  # Проверка дефолтного размера страницы
        assert all(UserItem(**user) for user in response.json())

    async def test_regular_user_forbidden(self, client: AsyncClient, user_token: str):
        """Обычный пользователь не может получить список"""
        response = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not permitted" in response.json()["detail"].lower()

    async def test_pagination_works(self, client: AsyncClient, admin_token: str, test_users):
        """Проверка работы пагинации"""
        # Первая страница (5 пользователей)
        response = await client.get(
            "/users/?page=1&size=5",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert len(response.json()) == 5

        # Вторая страница (5 пользователей)
        response = await client.get(
            "/users/?page=2&size=5",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert len(response.json()) == 5

        # Третья страница (5 пользователей)
        response = await client.get(
            "/users/?page=3&size=5",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert len(response.json()) == 5

    async def test_invalid_pagination_params(self, client: AsyncClient, admin_token: str):
        """Проверка валидации параметров пагинации"""
        test_cases = [
            ("/users/?page=-1", "page must be greater than or equal to 0"),
            ("/users/?size=0", "size must be greater than or equal to 1"),
            ("/users/?size=101", "size must be less than or equal to 100")
        ]

        for url, error_msg in test_cases:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert error_msg in str(response.json())

    async def test_no_token_unauthorized(self, client: AsyncClient):
        """Запрос без токена должен возвращать 401"""
        response = await client.get("/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"]

    async def test_invalid_token_rejected(self, client: AsyncClient):
        """Невалидный токен должен отклоняться"""
        # Создаем токен с неправильным секретным ключом
        invalid_token = jwt.encode(
            {
                "sub": str(uuid4()),
                "role": "admin",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
            },
            "wrong_secret_key",  # Неправильный ключ
            algorithm=AuthConfig.ALGORITHM
        )

        response = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    # async def test_expired_token_rejected(self, client: AsyncClient, admin_user):
    #     """Просроченный токен должен отклоняться"""
    #     expired_token = jwt.encode(
    #         {
    #             "sub": str(admin_user.id),
    #             "role": admin_user.role.value,
    #             "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    #         },
    #         AuthConfig.SECRET_KEY,
    #         algorithm=AuthConfig.ALGORITHM
    #     )
    #
    #     response = await client.get(
    #         "/users/",
    #         headers={"Authorization": f"Bearer {expired_token}"}
    #     )
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED
    #     assert "expired" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_expired_token_rejected(async_client: AsyncClient, async_db: AsyncSession):
    """Тест на отклонение просроченного токена"""
    # 1. Создаем тестового пользователя
    user_id = uuid4()
    async with async_db.begin():
        user = UserORM(
            id=uuid4(),
            email=f"user{user_id}@test.com",
            name=f"user{user_id}",
            surname=f"user{user_id}",
            age=39,
            phone=f"2923423{user_id}",
            role=UserRole.user,
            password=f"hash{user_id}",
            disabled=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_db.add(user)
        await async_db.flush()

        # 2. Генерируем просроченный токен
        expired_token = jwt.encode(
            {
                "sub": str(user.id),
                "role": user.role.value,
                "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
            },
            AuthConfig.SECRET_KEY,
            algorithm=AuthConfig.ALGORITHM
        )

    # 3. Отправляем запрос
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    # 4. Проверяем результат
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expired" in response.json()["detail"].lower()