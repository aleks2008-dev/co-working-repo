import re
from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field, StrictStr, StrictInt
from datetime import date

class CategoryEnum(StrEnum):
    FIRST = "first"
    SECOND = "second"
    HIGHEST = "highest"
    NO_CATEGORY = "no_category"

class DoctorItemCreate(BaseModel):
    name: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    surname: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    age: StrictInt | None = Field(default=None, ge=0)
    specialization: StrictStr | None = Field(default=None, min_length=3)
    category: CategoryEnum | None = None
    password: str | None = Field(default=None, exclude=True)

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
    name: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    surname: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    age: StrictInt | None = Field(default=None, ge=0)
    specialization: StrictStr | None = Field(default=None, min_length=3)
    category: CategoryEnum | None = None
    password: str | None = Field(default=None, min_length=5, exclude=True)

class DoctorInDB(DoctorItemCreate):
    hashed_password: str

class ClientItemCreate(BaseModel):
    name: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    surname: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    email: EmailStr | None = None
    age: StrictInt | None = Field(default=None, ge=0)
    phone: str

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

class ClientItem(ClientItemCreate):
    id: UUID

class ClientItemUpdate(BaseModel):
    name: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    surname: StrictStr | None = Field(default=None, min_length=3, max_length=10)
    email: EmailStr | None = None
    age: StrictInt | None = Field(default=None, ge=0)
    phone: str

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

class RoomItemCreate(BaseModel):
    number: StrictInt | None = Field(default=None, ge=0, le=100)

class RoomItem(RoomItemCreate):
    id: UUID

class AppointmentItemCreate(BaseModel):
    date: date

class AppointmentItem(AppointmentItemCreate):
    id: UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None