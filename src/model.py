from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


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
    password: str

class DoctorItem(DoctorItemCreate):
    id: UUID

class DoctorItemUpdate:
    name: str | None
    surname: str | None
    age: int | None
    specialization: str | None
    category: str | None
    password: str | None

class DoctorInDB(DoctorItemCreate):
    hashed_password: str

class ClientItemCreate(BaseModel):
    name: str = Field(max_length=10)
    surname: str = Field(max_length=10)
    email: EmailStr
    age: int = Field(0, ge=0, le=100)
    phone: str = Field(max_length=10)

class ClientItem(ClientItemCreate):
    id: UUID

class ClientItemUpdate:
    name: str | None
    surname: str | None
    email: str | None
    age: int | None
    phone: str | None

class RoomItemCreate(BaseModel):
    number: int = Field(0, ge=0, le=100)

class RoomItem(RoomItemCreate):
    id: UUID

class AppointmentItemCreate(BaseModel):
    date: int = Field(0, ge=0, le=100)

class AppointmentItem(AppointmentItemCreate):
    id: UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None