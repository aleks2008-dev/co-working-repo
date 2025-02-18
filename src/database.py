from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import uuid
from sqlalchemy import UUID, ForeignKey
from model import CategoryEnum

DATABASE_URL = "postgresql+asyncpg://doctors:doctors@postgres-db/doctors"
engine = create_async_engine(DATABASE_URL, echo=True)

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
    password: Mapped[str]

    appointments: Mapped["AppointmentORM"] = relationship(back_populates="doctor", lazy="joined")

class ClientORM(Base):
    __tablename__ = "clients"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    surname: Mapped[str]
    email: Mapped [str | None] = mapped_column(unique=True)
    age: Mapped[int]
    phone: Mapped[str] = mapped_column(unique=True)

    appointments: Mapped["AppointmentORM"] = relationship(back_populates="client", lazy="joined")

class RoomORM(Base):
    __tablename__ = "rooms"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number: Mapped[int]

    appointments: Mapped["AppointmentORM"] = relationship(back_populates="room", lazy="joined")

class AppointmentORM(Base):
    __tablename__ = "appointments"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[int]

    doctor_id = mapped_column(ForeignKey('doctors.id', ondelete="CASCADE"))
    doctor: Mapped["DoctorORM"] = relationship( back_populates="appointments", lazy="joined")
    client_id = mapped_column(ForeignKey('clients.id', ondelete="CASCADE"))
    client: Mapped["ClientORM"] = relationship( back_populates="appointments", lazy="joined")
    room_id = mapped_column(ForeignKey('rooms.id', ondelete="CASCADE"))
    room: Mapped["RoomORM"] = relationship( back_populates="appointments", lazy="joined")