import os
import uuid
from datetime import date

from dotenv import load_dotenv
from sqlalchemy import UUID, Boolean, Date, ForeignKey
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from model import CategoryEnum, UserRole

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine)


async def get_session() -> AsyncSession:
    """Asynchronous generator that yields database sessions."""
    async with async_session() as session:
        yield session


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DoctorORM(Base):
    """Doctor database model representing medical professionals."""
    __tablename__ = "doctors"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    surname: Mapped[str] = mapped_column(unique=True)
    age: Mapped[int]
    specialization: Mapped[str]
    category: Mapped[CategoryEnum]
    password: Mapped[str]

    appointments: Mapped["AppointmentORM"] = relationship(back_populates="doctor", cascade="all, delete", passive_deletes=True, lazy="joined")


class UserORM(Base):
    """User database model representing system users with authentication."""
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    surname: Mapped[str]
    email: Mapped [str | None] = mapped_column(unique=True)
    age: Mapped[int]
    phone: Mapped[str] = mapped_column(unique=True)
    role: Mapped[UserRole] = mapped_column(nullable=False, server_default="user")
    password: Mapped[str]
    disabled: Mapped [bool] = mapped_column(Boolean, default=False)

    appointments: Mapped["AppointmentORM"] = relationship(back_populates="user", cascade="all, delete", passive_deletes=True, lazy="joined")


class RoomORM(Base):
    """ ORM model representing a room in the database."""
    __tablename__ = "rooms"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number: Mapped[int]

    appointments: Mapped["AppointmentORM"] = relationship(back_populates="room", cascade="all, delete", passive_deletes=True, lazy="joined")


class AppointmentORM(Base):
    """ORM model representing an appointment in the database."""
    __tablename__ = "appointments"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[date] = mapped_column(Date)
    doctor_id = mapped_column(ForeignKey('doctors.id', ondelete="CASCADE"))
    doctor: Mapped["DoctorORM"] = relationship( back_populates="appointments", cascade="all, delete", passive_deletes=True, lazy="joined")
    user_id = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    user: Mapped["UserORM"] = relationship( back_populates="appointments", cascade="all, delete", passive_deletes=True, lazy="joined")
    room_id = mapped_column(ForeignKey('rooms.id', ondelete="CASCADE"))
    room: Mapped["RoomORM"] = relationship( back_populates="appointments", cascade="all, delete", passive_deletes=True, lazy="joined")
