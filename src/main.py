from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, Base, DoctorORM, async_session
from model import DoctorItem, DoctorItemCreate


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

@app.post("/doctors") # , response_model=DoctorItem
async def create_doctors(data: DoctorItemCreate, db: Annotated[AsyncSession, Depends(get_session)]):
    doctor = DoctorORM(name=data.name, age=data.age, category=data.category)
    db.add(doctor)
    await db.commit()



# @app.get("/doctors", response_model=list[DoctorItem])
# async def list_doctors():
#     pass
