from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field


class CategoryEnum(StrEnum):
    FIRST = "first"
    SECOND = "second"
    HIGHEST = "highest"
    NO_CATEGORY = "no_category"


class DoctorItemCreate(BaseModel):
    name: str = Field(min_length=3)
    surname: str = Field(min_length=3)
    age: int = Field(ge=0)
    specialization: str = Field(min_length=3)
    category: CategoryEnum

class DoctorItem(DoctorItemCreate):
    id: UUID


class ClientItemCreate(BaseModel):
    name: str = Field(max_length=10)
    surname: str = Field(max_length=10)
    email: str = Field(max_length=10)
    age: int = Field(0, ge=0, le=100)
    phone: int = Field(8)

class ClientItem(ClientItemCreate):
    id: UUID

class RoomItemCreate(BaseModel):
    number: int = Field(0, ge=0, le=100)

class RoomItem(RoomItemCreate):
    id: UUID

class AppointmentItemCreate(BaseModel):
    date: int = Field(0, ge=0, le=100)

class AppointmentItem(AppointmentItemCreate):
    id: UUID