from app.application.dto.employee import (
    EmployeeCreate,
    EmployeeFilterParams,
    EmployeePage,
    EmployeeRead,
    EmployeeUpdate,
)
from app.application.exceptions import (
    DuplicateEmployeePhone,
    EmployeeNotFound,
    FileUploadException,
    ValidationException,
)
from app.application.ports.employee_repository import EmployeeRecord, EmployeeRepositoryPort
from app.application.ports.file_storage import FileStoragePort, UploadedFile


class EmployeeService:
    def __init__(self, repository: EmployeeRepositoryPort, file_storage: FileStoragePort) -> None:
        self.repository = repository
        self.file_storage = file_storage

    async def list_employees(self, filters: EmployeeFilterParams) -> EmployeePage:
        employees, total = await self.repository.list(filters)
        return EmployeePage(
            items=[EmployeeRead.model_validate(employee) for employee in employees],
            total=total,
            page=filters.page,
            per_page=filters.per_page,
        )

    async def get_employee(self, employee_id: int) -> EmployeeRead:
        employee = await self._get_existing_employee(employee_id)
        return EmployeeRead.model_validate(employee)

    async def create_employee(
        self,
        data: EmployeeCreate,
        photo_file: UploadedFile | None,
        form_data: dict[str, object],
    ) -> EmployeeRead:
        await self._ensure_phone_available(data.phone, form_data=form_data)
        photo_path = await self._save_photo(photo_file, form_data)

        try:
            employee = await self.repository.create(data, photo_path=photo_path)
        except DuplicateEmployeePhone as exc:
            await self.file_storage.delete(photo_path)
            raise ValidationException(
                errors={"phone": exc.message},
                form_data=form_data,
            ) from exc

        return EmployeeRead.model_validate(employee)

    async def update_employee(
        self,
        employee_id: int,
        data: EmployeeUpdate,
        photo_file: UploadedFile | None,
        form_data: dict[str, object],
    ) -> EmployeeRead:
        employee = await self._get_existing_employee(employee_id)
        await self._ensure_phone_available(
            data.phone,
            current_employee_id=employee_id,
            form_data=form_data,
        )

        old_photo_path = employee.photo_path
        new_photo_path = await self._save_photo(photo_file, form_data)
        photo_path = new_photo_path or old_photo_path

        try:
            updated_employee = await self.repository.update(employee, data, photo_path=photo_path)
        except DuplicateEmployeePhone as exc:
            await self.file_storage.delete(new_photo_path)
            raise ValidationException(
                errors={"phone": exc.message},
                form_data=form_data,
            ) from exc

        if new_photo_path and old_photo_path and old_photo_path != new_photo_path:
            await self.file_storage.delete(old_photo_path)

        return EmployeeRead.model_validate(updated_employee)

    async def delete_employee(self, employee_id: int) -> None:
        employee = await self._get_existing_employee(employee_id)
        photo_path = employee.photo_path
        await self.repository.delete(employee)
        await self.file_storage.delete(photo_path)

    async def _get_existing_employee(self, employee_id: int) -> EmployeeRecord:
        employee = await self.repository.get_by_id(employee_id)
        if employee is None:
            raise EmployeeNotFound(employee_id)
        return employee

    async def _ensure_phone_available(
        self,
        phone: str,
        current_employee_id: int | None = None,
        form_data: dict[str, object] | None = None,
    ) -> None:
        existing_employee = await self.repository.get_by_phone(phone)
        if existing_employee is None:
            return
        if current_employee_id is not None and existing_employee.id == current_employee_id:
            return
        raise ValidationException(
            errors={"phone": "Сотрудник с таким телефоном уже существует."},
            form_data=form_data or {},
        )

    async def _save_photo(
        self,
        photo_file: UploadedFile | None,
        form_data: dict[str, object],
    ) -> str | None:
        try:
            return await self.file_storage.save(photo_file)
        except FileUploadException as exc:
            raise FileUploadException(
                message=exc.message,
                errors=exc.errors,
                form_data=form_data,
            ) from exc
