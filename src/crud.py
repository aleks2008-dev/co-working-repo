from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import DoctorORM, ClientORM
from model import DoctorItemUpdate, ClientItemUpdate, DoctorItem, ClientItem
from auth import get_password_hash
from fastapi import Query

async def create_doctor(db: AsyncSession, data: DoctorItem):
    hashed_password = get_password_hash(data.password)
    doctor = DoctorORM(name=data.name, surname=data.surname, age=data.age, specialization=data.specialization,
                       category=data.category, password=hashed_password)
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor

async def get_doctors(db: AsyncSession, page: int, size: int) -> list:
    result = await db.execute(select(DoctorORM).offset(page).limit(size))
    doctors = result.scalars().all()
    return doctors

async def get_doctor(db: AsyncSession, doctor_id: str):
    result = await db.execute(select(DoctorORM).filter(DoctorORM.id == doctor_id))
    doctor = result.scalars().first()
    return doctor

async def update_doctor(db: AsyncSession, doctor_id: int, doctor_update: DoctorItemUpdate):
    doctor = await get_doctor(db, doctor_id)
    if not doctor:
        return None
    if doctor_update.name is not None:
        doctor.name = doctor_update.name
    if doctor_update.surname is not None:
        doctor.surname = doctor_update.surname
    if doctor_update.age is not None:
        doctor.age = doctor_update.age
    if doctor_update.specialization is not None:
        doctor.specialization = doctor_update.specialization
    if doctor_update.category is not None:
        doctor.category = doctor_update.category
    if doctor_update.password is not None:
        doctor.password = doctor_update.password
    await db.commit()
    await db.refresh(doctor)
    return doctor

async def delete_doctor(db: AsyncSession, doctor_id: int):
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

async def update_client(db: AsyncSession, client_id: int, client_update: ClientItemUpdate):
    client = await get_client(db, client_id)
    if not client:
        return None
    if client_update.name is not None:
        client.name = client_update.name
    if client_update.surname is not None:
        client.surname = client_update.surname
    if client_update.email is not None:
        client.email = client_update.email
    if client_update.age is not None:
        client.age = client_update.age
    if client_update.phone is not None:
        client.phone = client_update.phone
    await db.commit()
    await db.refresh(client)
    return client

async def delete_client(db: AsyncSession, client_id: int):
    client = await get_client(db, client_id)
    if not client:
        return None
    await db.delete(client)
    await db.commit()
    return client