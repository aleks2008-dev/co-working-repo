import pytest_asyncio
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from main import app, get_session
from database import Base
from httpx import AsyncClient
import logging
from httpx import ASGITransport

logging.basicConfig(level=logging.DEBUG)

TEST_DATABASE_URL = "postgresql+asyncpg://doctors:doctors@postgres-db-test:5432/doctors"


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
    async with engine.connect() as conn:
        await conn.begin()
        try:
            AsyncSessionLocal = async_sessionmaker(
                bind=conn,
                expire_on_commit=False,
                autoflush=False
            )
            async with AsyncSessionLocal() as session:
                yield session
                await session.close()
        finally:
            await conn.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    def override_get_session():
        return db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as cl:
        yield cl

    app.dependency_overrides.clear()
    await cl.aclose()