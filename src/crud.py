from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import DoctorORM, ClientORM
from model import DoctorItemUpdate, ClientItemUpdate, DoctorItem, ClientItem
from auth import get_password_hash

async def create_doctor(db: AsyncSession, data: DoctorItem):
    hashed_password = get_password_hash(data.password)
    doctor = DoctorORM(name=data.name, surname=data.surname, age=data.age, specialization=data.specialization,
                       category=data.category, password=hashed_password)
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor

async def get_doctors(db: AsyncSession):
    result = await db.execute(select(DoctorORM))
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
    doctor.id = doctor_update.id
    doctor.name = doctor_update.name
    doctor.surname = doctor_update.surname
    doctor.age = doctor_update.age
    doctor.specialization = doctor_update.specialization
    doctor.category = doctor_update.category
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

async def get_clients(db: AsyncSession):
    result = await db.execute(select(ClientORM))
    clients = result.scalars().all()
    return clients

async def get_client(db: AsyncSession, client_id: str):
    result = await db.execute(select(ClientORM).filter(ClientORM.id == client_id))
    client = result.scalars().first()
    return client

async def update_client(db: AsyncSession, client_id: str, client_update: ClientItemUpdate):
    client = await get_client(db, client_id)
    if not client:
        return None
    client.id = client_update.id
    client.name = client_update.name
    client.surname = client_update.surname
    client.email = client_update.email
    client.age = client_update.age
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