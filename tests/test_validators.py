from datetime import date

import pytest
from pydantic import ValidationError

from app.application.dto.employee import EmployeeCreate, EmployeeFilterParams
from app.domain.employee import Gender
from app.domain.validators import calculate_age, subtract_years, validate_phone


def test_validate_phone_accepts_required_format() -> None:
    assert validate_phone("+79991234567") == "+79991234567"


def test_validate_phone_rejects_invalid_format() -> None:
    with pytest.raises(ValueError, match="Телефон должен"):
        validate_phone("89991234567")


def test_calculate_age_before_and_after_birthday() -> None:
    assert calculate_age(date(1990, 7, 4), today=date(2026, 7, 3)) == 35
    assert calculate_age(date(1990, 7, 3), today=date(2026, 7, 3)) == 36


def test_subtract_years_handles_leap_day() -> None:
    assert subtract_years(date(2024, 2, 29), 1) == date(2023, 2, 28)


def test_employee_create_normalizes_names() -> None:
    employee = EmployeeCreate(
        first_name=" Ivan ",
        last_name=" Petrov ",
        middle_name=" Sergeevich ",
        phone="+79991234567",
        birth_date=date(1990, 1, 1),
        gender=Gender.male,
    )

    assert employee.first_name == "Ivan"
    assert employee.last_name == "Petrov"
    assert employee.middle_name == "Sergeevich"


def test_employee_create_rejects_future_birth_date() -> None:
    with pytest.raises(ValidationError):
        EmployeeCreate(
            first_name="Ivan",
            last_name="Petrov",
            phone="+79991234567",
            birth_date=date(2999, 1, 1),
            gender=Gender.male,
        )


def test_employee_filters_reject_inverted_age_range() -> None:
    with pytest.raises(ValidationError, match="Минимальный возраст"):
        EmployeeFilterParams(age_from=50, age_to=20)
