from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import uuid
from sqlalchemy import UUID, ForeignKey
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

    appointments = relationship("AppointmentORM", back_populates="doctor")
    #doctors = relationship("doctors", back_populates="appointments")

class ClientORM(Base):
    __tablename__ = "clients"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    surname: Mapped[str]
    email: Mapped [str] = mapped_column(unique=True, nullable=False, index=True)
    age: Mapped[int]
    phone: Mapped[int] = mapped_column(unique=True, nullable=False, index=True)

    appointments = relationship("AppointmentORM", back_populates="client")
    #clients = relationship("clients", back_populates="appointments")


class RoomORM(Base):
    __tablename__ = "rooms"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number: Mapped[int]

    appointments = relationship("AppointmentORM", back_populates="room")
    #rooms = relationship("rooms", back_populates="appointments")


class AppointmentORM(Base):
    __tablename__ = "appointments"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[int]

    doctor_id = mapped_column(ForeignKey('doctors.id', ondelete="CASCADE"))
    doctor = relationship("DoctorORM", back_populates="appointments")
    client_id = mapped_column(ForeignKey('clients.id', ondelete="CASCADE"))
    client = relationship("ClientORM", back_populates="appointments")
    room_id = mapped_column(ForeignKey('rooms.id', ondelete="CASCADE"))
    room = relationship("RoomORM", back_populates="appointments")