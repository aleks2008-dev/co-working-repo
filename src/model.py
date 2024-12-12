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
    age: int = Field(ge=0)
    category: CategoryEnum


class DoctorItem(DoctorItemCreate):
    id: UUID
