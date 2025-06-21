import pytest_asyncio
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from main import app, get_session
from database import Base
from httpx import AsyncClient
import logging
from httpx import ASGITransport
from auth import create_access_token, AuthConfig
from uuid import uuid4
from datetime import timedelta, datetime, timezone
from database import UserORM
import jwt
from model import UserRole
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

TEST_DATABASE_URL = os.getenv("DATABASE_URL")

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        poolclass=NullPool  # Для изоляции тестов
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    app.dependency_overrides[get_session] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as cl:
        yield cl


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    """Создает администратора в тестовой БД"""
    user = UserORM(
        id=uuid4(),
        email="admin@test.com",
        name="admin",
        surname="admin",
        age=39,
        phone="292342323",
        role=UserRole.admin,
        password="hashed_admin_pass",
        disabled=False
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def regular_user(db_session: AsyncSession):
    """Создает обычного пользователя в тестовой БД"""
    user = UserORM(
        id=uuid4(),
        email="admin@test.com",
        name="admin",
        surname="admin",
        age=39,
        phone="292342323",
        role=UserRole.user,
        password="hashed_user_pass",
        disabled=False
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def user_token(regular_user):
    """Генерирует валидный токен пользователя"""
    payload = {
        "sub": str(regular_user.id),
        "role": regular_user.role.value,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(payload, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)


@pytest_asyncio.fixture
async def admin_token(admin_user):
    return jwt.encode(
        {
            "sub": str(admin_user.id),
            "role": admin_user.role.value,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        },
        AuthConfig.SECRET_KEY,
        algorithm=AuthConfig.ALGORITHM
    )


@pytest_asyncio.fixture
async def test_users(db_session: AsyncSession):
    """Создает 15 тестовых пользователей для проверки пагинации"""
    users = [
        UserORM(
            id=uuid4(),
            email=f"user{i}@test.com",
            name=f"user{i}",
            surname=f"user{i}",
            age=39,
            phone=f"2923423{i}",
            role=UserRole.user,
            password=f"hash{i}",
            disabled=False
        ) for i in range(15)
    ]
    db_session.add_all(users)
    await db_session.commit()
    return users