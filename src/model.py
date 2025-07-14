import re
from datetime import date
from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StrictInt,
    StrictStr,
    computed_field,
    field_validator,
)


class CategoryEnum(StrEnum):
    """Medical doctor qualification categories"""
    FIRST = "first"
    SECOND = "second"
    HIGHEST = "highest"
    NO_CATEGORY = "no_category"


class UserRole(StrEnum):
    """User roles in the healthcare system"""
    user = "user"
    admin = "admin"
    doctor = "doctor"


class DoctorItemCreate(BaseModel):
    name: StrictStr = Field(min_length=3, max_length=10)
    surname: StrictStr = Field(min_length=3, max_length=10)
    age: StrictInt = Field(ge=0)
    specialization: StrictStr = Field(min_length=3)
    category: CategoryEnum
    password: str = Field(exclude=True, min_length=4)

    @field_validator('age')
    def check_age(cls, value):
        if value < 0:
            raise ValueError('Age cannot be negative')
        return value

    @computed_field
    def full_name(self) -> str:
        return f"{self.name} {self.surname}"


class DoctorItem(DoctorItemCreate):
    id: UUID


class DoctorItemUpdate(BaseModel):
    """For updating doctor records with optional fields."""
    name: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    surname: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    age: StrictInt | None = Field(default=None, ge=0)
    specialization: StrictStr | None = Field(default=None, min_length=3)
    category: CategoryEnum | None = None
    password: str | None = Field(default=None, min_length=5, exclude=True)


class BaseUser(BaseModel):
    name: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    surname: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    email: EmailStr
    age: StrictInt | None = Field(default=None, ge=0)
    phone: str | None = None

    @field_validator('phone')
    def validate_phone_number(cls, value: str | None):
        pattern = r"""
                ^(\+375|80)?          # Код страны/оператора
                [\s\-\(\)]*          # Допустимые разделители
                (\d{2})               # Первые 2 цифры
                [\s\-\(\)]*           # Разделители
                (\d{3})              # Следующие 3 цифры
                [\s\-\(\)]*           # Разделители
                (\d{2})              # Предпоследние 2 цифры
                [\s\-\(\)]*           # Разделители
                (\d{2})$             # Последние 2 цифры
            """
        if value is None:
            return None
        if not re.fullmatch(pattern, value, flags=re.VERBOSE):
            raise ValueError("Invalid phone number format")
        cleaned_value = re.sub(r'\D', '', value)
        if not (7 <= len(cleaned_value) <= 15):
            raise ValueError('Phone number must be between 7 and 15 digits.')
        return value


class UserItemCreate(BaseUser):
    password: str = Field(exclude=True, min_length=8)
    role: UserRole | None = None


class UserItem(BaseUser):
    id: UUID
    role: UserRole | None = None


class UserItemUpdate(BaseUser):
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None
    disabled: bool | None = None


class UserPublic(BaseUser):
    id: UUID
    email: str
    name: str
    role: UserRole
    disabled: bool | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "exclude": {"password", "hashed_password"}
        }
    )


class CurrentUser(UserPublic):
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"

    model_config = ConfigDict(
    # class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "john_doe",
                "role": "user",
                "disabled": True,
                "access_token": "eyJhbGciOi...",
                "token_type": "bearer"
            }
        }
    )

class RoomItemCreate(BaseModel):
    number: StrictInt | None = Field(default=None, ge=0, le=100)


class RoomItem(RoomItemCreate):
    id: UUID


class AppointmentItemCreate(BaseModel):
    date: date
    doctor_id: UUID
    room_id: UUID

    @field_validator('date', mode='before')
    def parse_date(cls, value):
        if isinstance(value, int):
            # Преобразуем из формата YYYYMMDD в date
            return date(
                year=value // 10000,
                month=(value % 10000) // 100,
                day=value % 100
            )
        return value


class AppointmentItem(AppointmentItemCreate):
    id: UUID


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str