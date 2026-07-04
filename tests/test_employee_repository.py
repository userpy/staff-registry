from sqlalchemy import and_
from sqlalchemy.dialects import postgresql

from app.application.dto.employee import EmployeeFilterParams
from app.domain.employee import Gender
from app.infrastructure.repositories.employee_repository import EmployeeRepository


def compile_filter_sql(filters: EmployeeFilterParams) -> str:
    repository = EmployeeRepository(session=None)  # type: ignore[arg-type]
    condition = and_(*repository._build_conditions(filters))
    return str(
        condition.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_employee_search_uses_like_for_full_name_phone_and_age() -> None:
    sql = compile_filter_sql(EmployeeFilterParams(search="Палкин 25"))

    assert "concat(employees.last_name" in sql
    assert "employees.phone ILIKE '%%Палкин 25%%'" in sql
    assert "date_part('year'" in sql
    assert sql.count("ILIKE '%%Палкин 25%%'") == 3


def test_employee_filters_use_exact_gender_and_age_between() -> None:
    sql = compile_filter_sql(
        EmployeeFilterParams(
            gender=Gender.male,
            age_from=20,
            age_to=30,
        )
    )

    assert "employees.gender = 'male'" in sql
    assert " BETWEEN 20 AND 30" in sql
