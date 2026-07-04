from __future__ import annotations

import logging

from sqlalchemy import Integer, String, and_, cast, func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.employee import EmployeeCreate, EmployeeFilterParams, EmployeeUpdate
from app.application.exceptions import DuplicateEmployeePhone
from app.infrastructure.database.models.employee import Employee

logger = logging.getLogger(__name__)


class EmployeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, filters: EmployeeFilterParams) -> tuple[list[Employee], int]:
        conditions = self._build_conditions(filters)
        statement = select(Employee).order_by(Employee.last_name, Employee.first_name, Employee.id)
        count_statement = select(func.count()).select_from(Employee)

        if conditions:
            statement = statement.where(and_(*conditions))
            count_statement = count_statement.where(and_(*conditions))

        statement = statement.limit(filters.per_page).offset(filters.offset)

        try:
            rows = await self.session.scalars(statement)
            total = await self.session.scalar(count_statement)
        except SQLAlchemyError:
            logger.exception("database_error_list_employees")
            raise

        return list(rows), int(total or 0)

    async def get_by_id(self, employee_id: int) -> Employee | None:
        try:
            return await self.session.get(Employee, employee_id)
        except SQLAlchemyError:
            logger.exception("database_error_get_employee", extra={"employee_id": employee_id})
            raise

    async def get_by_phone(self, phone: str) -> Employee | None:
        statement = select(Employee).where(Employee.phone == phone)
        try:
            return await self.session.scalar(statement)
        except SQLAlchemyError:
            logger.exception("database_error_get_employee_by_phone")
            raise

    async def create(self, data: EmployeeCreate, photo_path: str | None) -> Employee:
        employee = Employee(**data.model_dump(), photo_path=photo_path)
        self.session.add(employee)
        try:
            await self.session.flush()
            await self.session.refresh(employee)
        except IntegrityError as exc:
            logger.info("database_duplicate_employee_phone", extra={"phone": data.phone})
            raise DuplicateEmployeePhone() from exc
        except SQLAlchemyError:
            logger.exception("database_error_create_employee")
            raise
        return employee

    async def update(
        self,
        employee: Employee,
        data: EmployeeUpdate,
        photo_path: str | None,
    ) -> Employee:
        update_data = data.model_dump()
        for field_name, value in update_data.items():
            setattr(employee, field_name, value)
        employee.photo_path = photo_path

        try:
            await self.session.flush()
            await self.session.refresh(employee)
        except IntegrityError as exc:
            logger.info(
                "database_duplicate_employee_phone",
                extra={"employee_id": employee.id, "phone": data.phone},
            )
            raise DuplicateEmployeePhone() from exc
        except SQLAlchemyError:
            logger.exception("database_error_update_employee", extra={"employee_id": employee.id})
            raise
        return employee

    async def delete(self, employee: Employee) -> None:
        try:
            await self.session.delete(employee)
            await self.session.flush()
        except SQLAlchemyError:
            logger.exception("database_error_delete_employee", extra={"employee_id": employee.id})
            raise

    def _build_conditions(self, filters: EmployeeFilterParams) -> list[object]:
        conditions: list[object] = []

        if filters.search:
            search_pattern = f"%{filters.search}%"
            age_as_text = cast(self._age_expression(), String)
            search_conditions: list[object] = [
                self._full_name_expression().ilike(search_pattern),
                Employee.phone.ilike(search_pattern),
                age_as_text.ilike(search_pattern),
            ]
            conditions.append(or_(*search_conditions))

        if filters.gender is not None:
            conditions.append(Employee.gender == filters.gender)

        if filters.age_from is not None and filters.age_to is not None:
            conditions.append(self._age_expression().between(filters.age_from, filters.age_to))
        elif filters.age_from is not None:
            conditions.append(self._age_expression() >= filters.age_from)
        elif filters.age_to is not None:
            conditions.append(self._age_expression() <= filters.age_to)

        return conditions

    def _full_name_expression(self) -> object:
        return func.concat(
            Employee.last_name,
            " ",
            Employee.first_name,
            " ",
            func.coalesce(Employee.middle_name, ""),
        )

    def _age_expression(self) -> object:
        return cast(
            func.date_part("year", func.age(func.current_date(), Employee.birth_date)),
            Integer,
        )
