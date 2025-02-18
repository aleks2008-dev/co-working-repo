import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app, get_session
from database import Base

# Настройка тестовой базы данных
TEST_DATABASE_URL = "sqlalchemy.url = postgresql+asyncpg://doctors:doctors@postgres-db-test/doctors"


@pytest.fixture
async def async_client():
    # Создаем асинхронный клиент для тестов
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session():
    # Создаем асинхронный движок и сессию для тестов
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


@pytest.fixture
async def override_get_db(db_session):
    # Переопределяем зависимость get_session для тестов
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_db
    yield
    app.dependency_overrides.clear()