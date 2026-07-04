from collections.abc import Sequence
from datetime import date, datetime
from typing import Protocol

from app.application.dto.employee import EmployeeCreate, EmployeeFilterParams, EmployeeUpdate
from app.domain.employee import Gender


class EmployeeRecord(Protocol):
    id: int
    first_name: str
    last_name: str
    middle_name: str | None
    phone: str
    birth_date: date
    gender: Gender
    photo_path: str | None
    created_at: datetime
    updated_at: datetime


class EmployeeRepositoryPort(Protocol):
    async def list(self, filters: EmployeeFilterParams) -> tuple[Sequence[EmployeeRecord], int]:
        raise NotImplementedError

    async def get_by_id(self, employee_id: int) -> EmployeeRecord | None:
        raise NotImplementedError

    async def get_by_phone(self, phone: str) -> EmployeeRecord | None:
        raise NotImplementedError

    async def create(self, data: EmployeeCreate, photo_path: str | None) -> EmployeeRecord:
        raise NotImplementedError

    async def update(
        self,
        employee: EmployeeRecord,
        data: EmployeeUpdate,
        photo_path: str | None,
    ) -> EmployeeRecord:
        raise NotImplementedError

    async def delete(self, employee: EmployeeRecord) -> None:
        raise NotImplementedError
