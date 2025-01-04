from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import engine, Base, DoctorORM, ClientORM, async_session
from model import DoctorItem, DoctorItemCreate, ClientItem, ClientItemCreate

from sqlmodel import select


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print("Shutting down...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

app = FastAPI(lifespan=lifespan)

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


async def get_session():
    async with async_session() as session:
        yield session

@app.post("/doctors", response_model=DoctorItem, tags=["doctor"])
async def create_doctors(data: DoctorItem, db: Annotated[AsyncSession, Depends(get_session)]):
    doctor = DoctorORM(name=data.name, surname=data.surname,age=data.age, specialization=data.specialization, category=data.category)
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return DoctorItem(id=data.id, name=data.name, surname=data.surname,age=data.age, specialization=data.specialization, category=data.category)

@app.get("/doctors/", response_model=list[DoctorItem], tags=["doctor"])
async def read_doctors(db: Annotated[AsyncSession, Depends(get_session)]):
        result = await db.execute(select(DoctorORM))
        doctors = result.scalars().all()
        return [DoctorItem(id=doctor.id, name=doctor.name, surname=doctor.surname,age=doctor.age, specialization=doctor.specialization, category=doctor.category) for doctor in doctors]

@app.get("/doctors/{doctor_id}", response_model=DoctorItem, tags=["doctor"])
async def read_doctor(doctor_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
        result = await db.execute(select(DoctorORM).filter(DoctorORM.id == doctor_id))
        doctor = result.scalars().first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return DoctorItem(id=doctor.id, name=doctor.name, surname=doctor.surname, age=doctor.age, specialization=doctor.specialization, category=doctor.category)

@app.patch("/doctors/{doctor_id}", response_model=DoctorItem, tags=["doctor"])
async def update_doctor(doctor_id: str, doctor: DoctorItem, db: Annotated[AsyncSession, Depends(get_session)]):
        result = await db.execute(select(DoctorORM).filter(DoctorORM.id == doctor_id))
        existing_doctor = result.scalars().first()
        if not existing_doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        existing_doctor.id = doctor.id
        existing_doctor.name = doctor.name
        existing_doctor.surname = doctor.surname
        existing_doctor.age = doctor.age
        existing_doctor.specialization = doctor.specialization
        existing_doctor.category = doctor.category
        await db.commit()
        await db.refresh(existing_doctor)
        return DoctorItem(id=doctor.id, name=doctor.name, age=doctor.age, category=doctor.category)

@app.delete("/doctors/{doctor_id}", response_model=DoctorItem, tags=["doctor"])
async def delete_doctor(doctor_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
            result = await db.execute(select(DoctorORM).filter(DoctorORM.id == doctor_id))
            doctor = result.scalars().first()
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
            await db.delete(doctor)
            await db.commit()
            return DoctorItem(id=doctor.id, name=doctor.name, surname=doctor.name, age=doctor.age, specialization=doctor.specialization, category=doctor.category)


@app.post("/clients", response_model=ClientItem, tags=["client"])
async def create_clients(data: ClientItem, db: Annotated[AsyncSession, Depends(get_session)]):
    client = ClientORM(name=data.name, surname=data.surname, email=data.email, age=data.age, phone=data.phone)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return ClientItem(id=data.id, name=data.name, surname=data.surname, email=data.email, age=data.age, phone=data.phone)

@app.get("/clients/", response_model=list[ClientItem], tags=["client"])
async def read_clients(db: Annotated[AsyncSession, Depends(get_session)]):
        result = await db.execute(select(ClientORM))
        clients = result.scalars().all()
        return [ClientItem(id=client.id, name=client.name, surname=client.surname, email=client.email, age=client.age, phone=client.phone) for client in clients]

@app.get("/clients/{client_id}", response_model=ClientItem, tags=["client"])
async def read_client(client_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
        result = await db.execute(select(ClientORM).filter(ClientORM.id == client_id))
        client = result.scalars().first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return ClientItem(id=client.id, name=client.name, surname=client.surname, email=client.email, age=client.age, phone=client.phone)

@app.patch("/clients/{client_id}", response_model=ClientItem, tags=["client"])
async def update_client(client_id: str, client: ClientItem, db: Annotated[AsyncSession, Depends(get_session)]):
        result = await db.execute(select(ClientORM).filter(ClientORM.id == client_id))
        existing_client = result.scalars().first()
        if not existing_client:
            raise HTTPException(status_code=404, detail="Client not found")

        existing_client.id = client.id
        existing_client.name = client.name
        existing_client.surname = client.surname
        existing_client.email = client.email
        existing_client.age = client.age
        existing_client.phone = client.phone
        await db.commit()
        await db.refresh(existing_client)
        return ClientItem(id=client.id, name=client.name, surname=client.surname, email=client.email, age=client.age, phone=client.phone)

@app.delete("/clients/{client_id}", response_model=ClientItem, tags=["client"])
async def delete_client(client_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
            result = await db.execute(select(ClientORM).filter(ClientORM.id == client_id))
            client = result.scalars().first()
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")
            await db.delete(client)
            await db.commit()
            return ClientItem(id=client.id, name=client.name, surname=client.surname, email=client.email, age=client.age, phone=client.phone)