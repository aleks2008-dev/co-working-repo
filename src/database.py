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
    surname: Mapped[str]
    age: Mapped[int]
    specialization: Mapped[str]
    category: Mapped[CategoryEnum]

    # appointments = relationship("AppointmentORM", back_populates="doctors")

class ClientORM(Base):
    __tablename__ = "clients"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    surname: Mapped[str]
    email: Mapped [str] = mapped_column(unique=True, index=True)
    age: Mapped[int]
    phone: Mapped[int] = mapped_column(unique=True, index=True)

    # appointments = relationship("AppointmentORM", back_populates="clients")

class RoomORM(Base):
    __tablename__ = "rooms"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number: Mapped[int]

class AppointmentORM(Base):
    __tablename__ = "appointments"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[int]

    # doctor_id = Column(Integer, ForeignKey('doctors.id'))
    # client_id = Column(Integer, ForeignKey('clients.id'))
    # doctor = relationship("DoctorORM", back_populates="appointments")
    # client = relationship("ClientORM", back_populates="appointments")
    # room = relationship("RoomORM", back_populates="appointments")