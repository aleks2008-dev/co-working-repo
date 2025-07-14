import logging
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from auth import AuthConfig
from database import Base, UserORM
from main import app, get_session
from model import UserRole

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
