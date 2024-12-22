from contextlib import asynccontextmanager
from typing import Annotated, List
from uuid import uuid4

from model import CategoryEnum
from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
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


@app.get("/doctors/{doctor_id}", response_model=DoctorItem)
async def get_doctor_id(doctor_id: int):
    print(doctor_id)
    return {"id": uuid4(), "name": "aleks", "age": 23, "category": CategoryEnum.FIRST}


@app.get("/doctors/", response_model=list[DoctorItem])
async def read_doctors(db: async_session = Depends(get_session)):
    textual_sql = text("SELECT * FROM doctors")
    orm_sql = select(DoctorORM).from_statement(textual_sql)
    for user_obj in db.execute(orm_sql).scalars():
        print(user_obj)


# @app.get("/doctors/", response_model=list[DoctorItem])
# async def read_doctors(skip: int = 0, limit: int = 10, db: async_session = Depends(get_session)):
#     return db.execute(select(DoctorORM).offset(skip).limit(limit)).all()

# @app.get("/", response_model=List[DoctorItem])
# def select_doctors():
#     with async_session() as session:
#         doctors = session.exec(select(DoctorORM)).all()
#         session.commit()
#         print(doctors.data)


# @app.get("/", response_model=List[DoctorItem])
# async def read_all_doctors(db: Annotated[AsyncSession, Depends(get_session)]):
#     query = DoctorORM.select()
#     return await db.fetch_all(query=query)

