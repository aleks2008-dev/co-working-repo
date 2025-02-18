from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
#from src import crud
from main import app, get_session
from model import DoctorItemCreate
from database import async_session, engine, Base
import pytest
import json
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

import pytest_asyncio
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client

@pytest.fixture
def mock_get_db(monkeypatch):
    async def mock_db():
        db = AsyncMock()
        yield db
    monkeypatch.setattr("app.main.get_db", mock_db)

@pytest.fixture
def mock_jwt():
    with patch("app.core.security.create_access_token", return_value="mocked_token"):
        yield

@pytest.fixture
def mock_rabbitmq():
    with patch("app.core.rabbitmq.get_rabbitmq_connection", new_callable=AsyncMock) as mock_rabbit:
        yield mock_rabbit

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_doctor():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/doctors/")
    assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_create_user(mock_get_db):
#     mock_db = await mock_get_db()  # Get the mocked DB session
#     mock_db.execute = AsyncMock(return_value=None)  # Mock doctor query to return no existing doctor
#
#     response = client.post("/doctorss/", json={"name": "Deadpond", "surname": "Dive Wilson", "age": 23, "specialization": "Dive Wilson", "category": "first", "password": "Dive Wilson", "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"})
#     assert response.status_code == 200
#     assert response.json()["name"] == "Deadpond"
#
#     # Test with existing user
#     mock_db.execute = AsyncMock(return_value=MagicMock(scalar=AsyncMock(return_value=True)))
#     response = client.post("/doctors/", json={"name": "Deadpond", "surname": "Dive Wilson", "age": 23, "specialization": "Dive Wilson", "category": "first", "password": "Dive Wilson", "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"})
#     assert response.status_code == 400

# def test_read_doctor_id():
#     client = TestClient(app)
#     response = client.get(
#         "/doctors", json={"name": "Deadpond", "surname": "Dive Wilson", "age": 23, "specialization": "Dive Wilson", "category": "first", "password": "Dive Wilson", "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}
#     )
#     data = response.json()
#
#     assert response.status_code == 200
#     assert data["name"] == "Deadpond"
#     assert data["surname"] == "Dive Wilson"
#     assert data["age"] == 23
#     assert data["specialization"] == "Dive Wilson"
#     assert data["category"] == "first"
    #assert data["password"] == "Dive Wilson"
    #assert data["id"] == "3fa85f64-5717-4562-b3fc-2c963f66afa6"

def test_create_doctor_one():
    client = TestClient(app)
    response = client.post(
        "/doctors", json={"name": "Deadpond", "surname": "Dive Wilson", "age": 23, "specialization": "Dive Wilson", "category": "first", "password": "Dive Wilson", "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Deadpond"
    assert data["surname"] == "Dive Wilson"
    assert data["age"] == 23
    assert data["specialization"] == "Dive Wilson"
    assert data["category"] == "first"
    #assert data["password"] == "Dive Wilson"
    #assert data["id"] == "3fa85f64-5717-4562-b3fc-2c963f66afa6"

# @pytest_asyncio.fixture(scope="module")
# async def db():
#     # Настройка вашей тестовой базы данных
#     async_session = sessionmaker(bind=create_async_engine("postgresql+asyncpg://doctors:doctors@postgres-db-test/doctors"), class_=AsyncSession)
#     async with async_session() as session:
#         async with session.begin():
#             await session.run_sync(Base.metadata.create_all)
#         yield session
#         async with session.begin():
#             await session.run_sync(Base.metadata.drop_all)
#
# @pytest.mark.asyncio
# async def test_read_nonexistent_user():
#     async with AsyncClient(
#             transport=ASGITransport(app=app), base_url="http://test"
#     ) as ac:
#         response = await ac.get("/doctors/7218e525-8197-4210-acfa-18cc42563e6i")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Doctor not found"