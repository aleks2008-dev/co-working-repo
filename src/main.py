from typing import Annotated
from uuid import UUID
from datetime import datetime, timedelta
from jose import JWTError

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from auth import RoleChecker, create_access_token, get_current_user, verify_password, generate_reset_token, verify_reset_token, send_reset_email, get_password_hash
from crud import (
    create_doctor,
    create_room,
    create_user,
    delete_doctor,
    delete_user,
    get_appointments,
    get_doctor,
    get_doctors,
    get_user,
    get_users,
    get_user_by_email
)
from database import AppointmentORM, DoctorORM, UserORM, get_session
from model import (
    AppointmentItem,
    AppointmentItemCreate,
    DoctorItem,
    DoctorItemCreate,
    DoctorItemUpdate,
    RoomItemCreate,
    UserItem,
    UserItemCreate,
    UserItemUpdate,
    UserRole,
    PasswordResetRequest,
    PasswordResetConfirm
)

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
async def doctor_create(data: DoctorItemCreate, db: Annotated[AsyncSession, Depends(get_session)]) -> DoctorORM:
    """Register a new medical professional in the system."""
    return await create_doctor(db, data)


@app.get("/doctors/", response_model=list[DoctorItem], tags=["doctor"])
async def read_doctors(db: Annotated[AsyncSession, Depends(get_session)], page: int = Query(ge=0, default=1), size: int = Query(ge=1, le=100, default=10)) -> list[DoctorORM]:
    """Retrieve a paginated list of doctors."""
    return await get_doctors(db, page, size)


@app.get("/doctors/{doctor_id}", response_model=DoctorItem, tags=["doctor"])
async def read_doctor(doctor_id: UUID, db: Annotated[AsyncSession, Depends(get_session)]):
    doctor = await get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@app.patch("/doctors/{doctor_id}", response_model=DoctorItemCreate, tags=["doctor"])
async def doctor_update(doctor_id: UUID, doctor: DoctorItemUpdate, db: Annotated[AsyncSession, Depends(get_session)]) -> DoctorORM:
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный пароль")

    access_token = create_access_token(subject=str(user.id), role= user.role, email= user.email)
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
async def user_update(user_id: UUID, user: UserItemUpdate, db: Annotated[AsyncSession, Depends(get_session)]):
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


@app.post("/appointments", tags=["appointments"])
async def create_appointment(appointment_data: AppointmentItemCreate, db: AsyncSession = Depends(get_session), current_user: UserORM = Depends(get_current_user)):
    # Проверка существования врача
    doctor = await get_doctor(db, appointment_data.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Создание записи
    new_appointment = AppointmentORM(
        doctor_id=appointment_data.doctor_id,
        user_id=current_user.id,
        date=int(appointment_data.date.strftime('%Y%m%d')),
        room_id=appointment_data.room_id
    )

    db.add(new_appointment)
    await db.commit()
    await db.refresh(new_appointment)

    return new_appointment


@app.post("/rooms/", response_model=RoomItemCreate, tags=["room"])
async def room_create(data: RoomItemCreate, db: Annotated[AsyncSession, Depends(get_session)]):
    return await create_room(db, data)


@app.get("/appointments/", response_model=list[AppointmentItem], tags=["appointments"])
async def read_appointments(db: Annotated[AsyncSession, Depends(get_session)], page: int = Query(ge=0, default=1), size: int = Query(ge=1, le=100, default=10)) -> list[AppointmentORM]:
    """Retrieve a paginated list of doctors."""
    return await get_appointments(db, page, size)


@app.post("/password-reset")
async def request_password_reset(
        request: PasswordResetRequest,
        db: AsyncSession = Depends(get_session)
):
    user = await get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    # Генерация токена (действителен 1 час)
    reset_token = generate_reset_token(user.email)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    await db.commit()

    # Отправка email (используем FastAPI-Mail)
    await send_reset_email(user.email, reset_token)
    return {"message": "Reset link sent"}


# 2. Подтверждение сброса пароля
@app.post("/password-reset-confirm")
async def confirm_password_reset(
        form_data: PasswordResetConfirm,
        db: AsyncSession = Depends(get_session)
):
    # Проверка токена
    try:
        email = verify_reset_token(form_data.token)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = await get_user_by_email(db, email)
    if not user or user.reset_token != form_data.token:
        raise HTTPException(status_code=400, detail="Invalid token")

    if datetime.utcnow() > user.reset_token_expires:
        raise HTTPException(status_code=400, detail="Token expired")

    # Обновление пароля
    user.hashed_password = get_password_hash(form_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()

    return {"message": "Password updated successfully"}
