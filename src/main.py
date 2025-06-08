from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import crud
from database import engine, Base, DoctorORM, UserORM, async_session, get_session
from model import DoctorItem, UserItem, DoctorItemCreate, UserItemUpdate, DoctorItemUpdate, UserItemCreate, LoginInput, UserRole
from auth import verify_password, create_access_token
from crud import get_doctors, get_doctor, get_user, get_users, update_user_dump, delete_doctor, delete_user, create_doctor, create_user, update_doctor_dump
from auth import RoleChecker

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Starting up...")
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     print("Shutting down...")
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

app = FastAPI()#lifespan=lifespan)

@app.get("/healthcheck/")
async def healthcheck():
    return {"status": "ok"}

# async def get_session() -> AsyncSession:
#     """Asynchronous generator that yields database sessions."""
#     async with async_session() as session:
#         yield session

@app.post("/doctors/", response_model=DoctorItem, tags=["doctor"])
async def doctor_create(data: DoctorItemCreate, db: Annotated[AsyncSession, Depends(get_session)]) -> DoctorItem:
    """Register a new medical professional in the system."""
    return await create_doctor(db, data)

# Вход в систему врач
# @app.post("/auth/login")
# async def login(data: LoginInput, db: Annotated[AsyncSession, Depends(get_session)]):
#     """Authenticate a doctor and generate an access token."""
#     result = await db.execute(select(DoctorORM).filter(DoctorORM.name == data.name))
#     doctor = result.scalar_one_or_none()
#
#     if not doctor:
#         return HTTPException(status_code=400, detail="Incorrect doctor name")
#     if not verify_password(data.password, doctor.password):
#         return HTTPException(status_code=400, detail="Incorrect doctor password")
#
#     access_token = create_access_token(data={"sub": doctor.name, "email": doctor.surname})
#     return {"access_token": access_token, "token_type": "bearer"}

@app.get("/doctors/", response_model=list[DoctorItem], tags=["doctor"])
async def read_doctors(db: Annotated[AsyncSession, Depends(get_session)], page: int = Query(ge=0, default=1), size: int = Query(ge=1, le=100, default=10)) -> list[DoctorItem]:
    """Retrieve a paginated list of doctors."""
    return await get_doctors(db, page, size)

@app.get("/doctors/{doctor_id}", response_model=DoctorItem, tags=["doctor"])
async def read_doctor(doctor_id: UUID, db: Annotated[AsyncSession, Depends(get_session)]):
    doctor = await get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.patch("/doctors/{doctor_id}", response_model=DoctorItemCreate, tags=["doctor"])
async def doctor_update(doctor_id: str, doctor: DoctorItemUpdate, db: Annotated[AsyncSession, Depends(get_session)]) -> DoctorItem:
    """Retrieve details of a specific doctor by their ID."""
    db_doctor = await crud.update_doctor_dump(db, doctor_id, doctor)
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@app.delete("/doctors/{doctor_id}", tags=["doctor"])
async def doctor_delete(doctor_id: UUID, db: Annotated[AsyncSession, Depends(get_session)]):
    """Delete a doctor by their ID."""
    doctor = await delete_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"message": "Doctor deleted"}

# Вход в систему User
@app.post("/token")
async def login(data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(UserORM).where(UserORM.name == data.username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя пользователя")
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Неверный пароль")

    # Генерация токена
    access_token =create_access_token(data={"sub": str(user.id), "role": user.role.value, "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserItem, tags=["user"])
async def user_create(data: UserItemCreate, db: Annotated[AsyncSession, Depends(get_session)]):
    return await create_user(db, data)

@app.get("/users/", response_model=list[UserItem], dependencies=[Depends(RoleChecker([UserRole.admin]))], tags=["user"])
async def read_users(db: Annotated[AsyncSession, Depends(get_session)], page: int = Query(ge=0, default=1), size: int = Query(ge=1, le=100, default=10)) -> list:
    return await get_users(db, page, size)

@app.get("/users/{user_id}", response_model=UserItem, tags=["user"])
async def read_user(user_id: UUID, db: Annotated[AsyncSession, Depends(get_session)]):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=UserItemCreate, tags=["user"])
async def user_update(user_id: str, user: UserItemUpdate, db: Annotated[AsyncSession, Depends(get_session)]):
    db_user = await crud.update_user_dump(db, user_id, user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", tags=["user"])
async def user_delete(user_id: UUID, db: Annotated[AsyncSession, Depends(get_session)]):
    user = await delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}