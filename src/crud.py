from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import DoctorORM, UserORM
from model import DoctorItemUpdate, UserItemUpdate, DoctorItem, UserItem, DoctorItemCreate, UserItemCreate
from auth import get_password_hash
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

async def create_doctor(db: AsyncSession, data: DoctorItemCreate):
    hashed_password = await get_password_hash(data.password)
    doctor = DoctorORM(name=data.name, surname=data.surname, age=data.age, specialization=data.specialization,
                       category=data.category, password=hashed_password)
    try:
        db.add(doctor)
        await db.commit()
        await db.refresh(doctor)
    except IntegrityError as e:
        await db.rollback()

        error_msg = "Database integrity error"
        if "unique constraint" in str(e).lower():
            error_msg = "Duplicate entry. Doctor with these details already exists"
        elif "foreign key constraint" in str(e).lower():
            error_msg = "Invalid reference in foreign key"

        raise HTTPException(
            status_code=409,
            detail=error_msg
        )
    return doctor

async def get_doctors(db: AsyncSession, page: int, size: int) -> list[DoctorORM]:
    result = await db.execute(select(DoctorORM).order_by(DoctorORM.name.asc()).offset((page - 1) * size).limit(size))
    doctors = result.scalars().all()
    return doctors

async def get_doctor(db: AsyncSession, doctor_id: str):
    result = await db.execute(select(DoctorORM).filter(DoctorORM.id == doctor_id))
    doctor = result.scalars().first()
    return doctor

async def update_doctor_dump(db: AsyncSession, doctor_id: str, doctor_update: DoctorItemUpdate):
    db_doctor = await get_doctor(db, doctor_id)
    if not db_doctor:
        return None

    update_data = doctor_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_doctor, field, value)

    db.add(db_doctor)
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor

async def delete_doctor(db: AsyncSession, doctor_id: str):
    doctor = await get_doctor(db, doctor_id)
    if not doctor:
        return None
    await db.delete(doctor)
    await db.commit()
    return doctor

async def create_user(db: AsyncSession, data: UserItemCreate):
    hashed_password = await get_password_hash(data.password)
    user = UserORM(name=data.name, surname=data.surname, email=data.email, age=data.age,
                       phone=data.phone, role=data.role, password=hashed_password)
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except IntegrityError as e:
        await db.rollback()

        error_msg = "Database integrity error"
        if "unique constraint" in str(e).lower():
            error_msg = "Duplicate entry. User with these details already exists"
        elif "foreign key constraint" in str(e).lower():
            error_msg = "Invalid reference in foreign key"

        raise HTTPException(
            status_code=409,
            detail=error_msg
        )
    return user

async def get_users(db: AsyncSession, page: int, size: int) -> list[UserORM]:
    result = await db.execute(select(UserORM).order_by(UserORM.name.asc()).offset((page - 1) * size).limit(size))
    users = result.scalars().all()
    return users

async def get_user(db: AsyncSession, user_id: str):
    result = await db.execute(select(UserORM).filter(UserORM.id == user_id))
    user = result.scalars().first()
    return user

async def update_user_dump(db: AsyncSession, user_id: str, user_update: UserItemUpdate):
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    if not user:
        return None
    await db.delete(user)
    await db.commit()
    return user