from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError


class AppException(Exception):
    status_code = 400

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValidationException(AppException):
    status_code = 400

    def __init__(
        self,
        message: str = "Ошибка валидации.",
        errors: Mapping[str, str] | None = None,
        form_data: Mapping[str, Any] | None = None,
    ) -> None:
        self.errors = dict(errors or {})
        self.form_data = dict(form_data or {})
        super().__init__(message)

    @classmethod
    def from_pydantic(
        cls,
        exc: ValidationError,
        form_data: Mapping[str, Any],
    ) -> "ValidationException":
        errors: dict[str, str] = {}
        for error in exc.errors():
            location = error.get("loc", ())
            field = str(location[-1]) if location else "form"
            errors[field] = _translate_pydantic_error(field, error)
        return cls(errors=errors, form_data=form_data)


class EmployeeNotFound(AppException):
    status_code = 404

    def __init__(self, employee_id: int) -> None:
        self.employee_id = employee_id
        super().__init__(f"Сотрудник #{employee_id} не найден.")


class DuplicateEmployeePhone(AppException):
    status_code = 400

    def __init__(self) -> None:
        super().__init__("Сотрудник с таким телефоном уже существует.")


class FileUploadException(ValidationException):
    status_code = 400


def _translate_pydantic_error(field: str, error: dict[str, Any]) -> str:
    error_type = str(error.get("type", ""))
    context = error.get("ctx") or {}

    if error_type == "value_error":
        return str(error["msg"]).removeprefix("Value error, ")
    if error_type == "missing":
        return "Это поле обязательно."
    if error_type == "string_too_short":
        return "Это поле обязательно."
    if error_type == "string_too_long":
        return f"Максимум {context.get('max_length')} символов."
    if error_type.startswith("date_"):
        return "Введите корректную дату рождения."
    if field == "gender" and error_type == "enum":
        return "Выберите пол."
    if error_type == "greater_than_equal":
        return f"Значение должно быть не меньше {context.get('ge')}."
    if error_type == "less_than_equal":
        return f"Значение должно быть не больше {context.get('le')}."
    return str(error["msg"])
