from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid

from sqlalchemy import UUID
from model import CategoryEnum

engine = create_async_engine("postgresql+asyncpg://doctors:doctors@postgres-db/doctors", echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DoctorORM(Base):
    __tablename__ = "doctors"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    age: Mapped[int]
    category: Mapped[CategoryEnum]

# class DoctorORM(Base):
#     __tablename__ = "doctors"
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str]
#     age: Mapped[int]
#     category: Mapped[CategoryEnum]
