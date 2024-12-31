from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import engine, Base, DoctorORM, async_session
from model import DoctorItem, DoctorItemCreate

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

@app.post("/doctors", response_model=DoctorItem)
async def create_doctors(data: DoctorItemCreate, db: Annotated[AsyncSession, Depends(get_session)]):
    doctor = DoctorORM(name=data.name, age=data.age, category=data.category)
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return DoctorItem(id=data.id, name=data.name, age=data.age, category=data.category)

@app.get("/doctors/", response_model=list[DoctorItem])
async def read_doctors(db: Annotated[AsyncSession, Depends(get_session)]):
        result = await db.execute(select(DoctorORM))
        doctors = result.scalars().all()
        return [DoctorItem(id=doctor.id, name=doctor.name, age=doctor.age, category=doctor.category) for doctor in doctors]

@app.get("/doctors/{doctor_id}", response_model=DoctorItem)
async def read_doctor(doctor_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
        result = await db.execute(select(DoctorORM).filter(DoctorORM.id == doctor_id))
        doctor = result.scalars().first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return DoctorItem(id=doctor.id, name=doctor.name, age=doctor.age, category=doctor.category)

@app.patch("/doctors/{doctor_id}", response_model=DoctorItem)
async def update_doctor(doctor_id: str, doctor: DoctorItem, db: Annotated[AsyncSession, Depends(get_session)]):
        result = await db.execute(select(DoctorORM).filter(DoctorORM.id == doctor_id))
        existing_doctor = result.scalars().first()
        if not existing_doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        existing_doctor.name = doctor.name
        existing_doctor.age = doctor.age
        existing_doctor.category = doctor.category
        await db.commit()
        await db.refresh(existing_doctor)
        return DoctorItem(id=doctor.id, name=doctor.name, age=doctor.age, category=doctor.category)

@app.delete("/doctors/{doctor_id}", response_model=DoctorItem)
async def delete_doctor(doctor_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
            result = await db.execute(select(DoctorORM).filter(DoctorORM.id == doctor_id))
            doctor = result.scalars().first()
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
            await db.delete(doctor)
            await db.commit()
            return DoctorItem(id=doctor.id, name=doctor.name, age=doctor.age, category=doctor.category)
