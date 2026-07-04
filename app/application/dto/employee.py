from datetime import date, datetime
from math import ceil
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from app.domain.employee import Gender
from app.domain.validators import (
    calculate_age,
    normalize_name,
    normalize_optional_name,
    validate_phone,
)


class EmployeeBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    phone: str
    birth_date: date
    gender: Gender

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_required_name(cls, value: str) -> str:
        normalized = normalize_name(value)
        if not normalized:
            raise ValueError("Это поле обязательно.")
        return normalized

    @field_validator("middle_name")
    @classmethod
    def normalize_middle_name(cls, value: str | None) -> str | None:
        return normalize_optional_name(value)

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        return validate_phone(value)

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Дата рождения должна быть в прошлом.")
        return value


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_path: str | None = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def age(self) -> int:
        return calculate_age(self.birth_date)

    @computed_field
    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(part for part in parts if part)


class EmployeeFilterParams(BaseModel):
    search: str | None = Field(default=None, max_length=100)
    gender: Gender | None = None
    age_from: int | None = Field(default=None, ge=0, le=150)
    age_to: int | None = Field(default=None, ge=0, le=150)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)

    @field_validator("search")
    @classmethod
    def normalize_search(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.strip().split())
        return normalized or None

    @model_validator(mode="after")
    def validate_age_range(self) -> Self:
        if self.age_from is not None and self.age_to is not None and self.age_from > self.age_to:
            raise ValueError("Минимальный возраст не может быть больше максимального.")
        return self

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class EmployeePage(BaseModel):
    items: list[EmployeeRead]
    total: int
    page: int
    per_page: int

    @computed_field
    @property
    def pages(self) -> int:
        if self.total == 0:
            return 1
        return ceil(self.total / self.per_page)
