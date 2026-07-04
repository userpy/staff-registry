import re
from datetime import date

PHONE_PATTERN = re.compile(r"^\+7\d{10}$")


def normalize_name(value: str) -> str:
    return " ".join(value.strip().split())


def normalize_optional_name(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = normalize_name(value)
    return normalized or None


def validate_phone(value: str) -> str:
    normalized = value.strip()
    if not PHONE_PATTERN.fullmatch(normalized):
        raise ValueError("Телефон должен быть в формате +79991234567.")
    return normalized


def calculate_age(birth_date: date, today: date | None = None) -> int:
    current_date = today or date.today()
    years = current_date.year - birth_date.year
    birthday_passed = (current_date.month, current_date.day) >= (birth_date.month, birth_date.day)
    return years if birthday_passed else years - 1


def subtract_years(source_date: date, years: int) -> date:
    try:
        return source_date.replace(year=source_date.year - years)
    except ValueError:
        return source_date.replace(month=2, day=28, year=source_date.year - years)
