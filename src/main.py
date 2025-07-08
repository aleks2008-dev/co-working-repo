from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import engine, Base, DoctorORM, async_session
from model import DoctorItem, ClientItem
from auth import verify_password, create_access_token
from crud import get_doctors, get_doctor, get_client, get_clients, update_doctor, update_client, delete_doctor, delete_client, create_doctor, create_client


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

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


async def get_session():
    async with async_session() as session:
        yield session


@app.post("/doctors", response_model=DoctorItem, tags=["doctor"])
async def doctor_create(data: DoctorItem, db: Annotated[AsyncSession, Depends(get_session)]):
    return await create_doctor(db, data)

# Вход в систему
@app.post("/auth/login")
async def login(data: DoctorItem, db: Annotated[AsyncSession, Depends(get_session)]):
    result = await db.execute(select(DoctorORM).filter(DoctorORM.name == data.name))
    doctor = result.scalar_one_or_none()

    if not doctor:
        return HTTPException(status_code=400, detail="Incorrect doctor name")
    if not verify_password(data.password, doctor.password):
        return HTTPException(status_code=400, detail="Incorrect doctor password")

    access_token = create_access_token(data={"sub": doctor.name})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/doctors/", response_model=list[DoctorItem], tags=["doctor"])
async def read_doctors(db: Annotated[AsyncSession, Depends(get_session)]):
    return await get_doctors(db)

@app.get("/doctors/{doctor_id}", response_model=DoctorItem, tags=["doctor"])
async def read_doctor(doctor_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
    doctor = await get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.patch("/doctors/{doctor_id}", response_model=DoctorItem, tags=["doctor"])
async def doctor_update(doctor_id: str, doctor: DoctorItem, db: Annotated[AsyncSession, Depends(get_session)]):
    return await update_doctor(db, doctor_id, doctor)

@app.delete("/doctors/{doctor_id}", tags=["doctor"])
async def doctor_delete(doctor_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
    doctor = await delete_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"message": "Doctor deleted"}

@app.post("/clients", response_model=ClientItem, tags=["client"])
async def client_create(data: ClientItem, db: Annotated[AsyncSession, Depends(get_session)]):
    return await create_client(db, data)

@app.get("/clients/", response_model=list[ClientItem], tags=["client"])
async def read_clients(db: Annotated[AsyncSession, Depends(get_session)]):
    return await get_clients(db)

@app.get("/clients/{client_id}", response_model=ClientItem, tags=["client"])
async def read_client(client_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
    client = await get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@app.patch("/clients/{client_id}", response_model=ClientItem, tags=["client"])
async def client_update(client_id: str, client: ClientItem, db: Annotated[AsyncSession, Depends(get_session)]):
    return await update_client(db, client_id, client)

@app.delete("/clients/{client_id}", tags=["client"])
async def client_delete(client_id: str, db: Annotated[AsyncSession, Depends(get_session)]):
    client = await delete_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted"}
