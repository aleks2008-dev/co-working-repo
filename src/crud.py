from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import DoctorORM, ClientORM
from model import DoctorItemUpdate, ClientItemUpdate, DoctorItem, ClientItem
from auth import get_password_hash
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

async def create_doctor(db: AsyncSession, data: DoctorItem):
    hashed_password = get_password_hash(data.password)
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

async def create_client(db: AsyncSession, data: ClientItem):
    client = ClientORM(name=data.name, surname=data.surname, email=data.email, age=data.age,
                       phone=data.phone)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client

async def get_clients(db: AsyncSession, page: int, size: int) -> list:
    result = await db.execute(select(ClientORM).offset(page).limit(size))
    clients = result.scalars().all()
    return clients

async def get_client(db: AsyncSession, client_id: str):
    result = await db.execute(select(ClientORM).filter(ClientORM.id == client_id))
    client = result.scalars().first()
    return client

async def update_client_dump(db: AsyncSession, client_id: int, client_update: ClientItemUpdate):
    db_client = await get_client(db, client_id)
    if not db_client:
        return None

    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)

    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client

async def delete_client(db: AsyncSession, client_id: int):
    client = await get_client(db, client_id)
    if not client:
        return None
    await db.delete(client)
    await db.commit()
    return client