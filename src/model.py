import re
from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field, StrictStr, StrictInt
from datetime import date
from typing import Optional

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

class DoctorInDB(DoctorItemCreate):
    hashed_password: str

class UserItemCreate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: EmailStr | None = None
    age: StrictInt = Field(default=None, ge=0)
    phone: Optional[str] = None
    role: UserRole = Field(default="user")
    password: Optional[str] = Field(default=None, exclude=True, min_length=8)
    disabled: bool = False

    # @field_validator('phone')
    # def validate_phone_number(cls, value):
    #     pattern = r"""
    #         ^(\+375|80)?          # Код страны/оператора
    #         [\s\-\(\)]*          # Допустимые разделители
    #         (\d{2})               # Первые 2 цифры
    #         [\s\-\(\)]*           # Разделители
    #         (\d{3})              # Следующие 3 цифры
    #         [\s\-\(\)]*           # Разделители
    #         (\d{2})              # Предпоследние 2 цифры
    #         [\s\-\(\)]*           # Разделители
    #         (\d{2})$             # Последние 2 цифры
    #     """
    #     if not re.fullmatch(pattern, value, flags=re.VERBOSE):
    #         raise ValueError("Invalid phone number format")
    #     cleaned_value = re.sub(r'\D', '', value)
    #     if not (7 <= len(cleaned_value) <= 15):
    #         raise ValueError('Phone number must be between 7 and 15 digits.')
    #     return value

class UserItem(UserItemCreate):
    id: UUID

    class Config:
        orm_mode = True

class UserItemUpdate(BaseModel):
    name: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    surname: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    email: EmailStr | None = None
    age: StrictInt | None = Field(default=None, ge=0)
    phone: StrictStr | None = Field(default=None)
    role: UserRole  | None = Field(default="user")
    password: str | None = Field(default=None, min_length=5, exclude=True)
    disabled: bool | None = Field(default=False)

    @field_validator('phone')
    def validate_phone_number(cls, value):
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
        if not re.fullmatch(pattern, value, flags=re.VERBOSE):
            raise ValueError("Invalid phone number format")
        cleaned_value = re.sub(r'\D', '', value)
        if not (7 <= len(cleaned_value) <= 15):
            raise ValueError('Phone number must be between 7 and 15 digits.')
        return value

    @field_validator("age")
    def validate_age(cls, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("Age must be an integer")
        return value

class UserInDB(UserItemCreate):
    id: int
    role: UserRole
    is_active: bool = True
    hashed_password: str

    class Config:
        from_attributes = True

class UserPublic(UserInDB):
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    class Config:
        exclude = {"hashed_password"}

    #hashed_password: str

class CurrentUser(UserPublic):
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "john_doe",
                "role": "user",
                "is_active": True,
                "access_token": "eyJhbGciOi...",
                "token_type": "bearer"
            }
        }

class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class RoomItemCreate(BaseModel):
    number: StrictInt | None = Field(default=None, ge=0, le=100)

class RoomItem(RoomItemCreate):
    id: UUID

class AppointmentItemCreate(BaseModel):
    date: date

class AppointmentItem(AppointmentItemCreate):
    id: UUID

class Token(BaseModel):
    access_token: str | None = None
    token_type: str | None = None

class TokenData(BaseModel):
    name: str | None = None
    role: StrictStr = Field(default="user")