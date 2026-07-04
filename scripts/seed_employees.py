from __future__ import annotations

import asyncio
from datetime import date
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain.employee import Gender
from app.infrastructure.database.models.employee import Employee
from app.infrastructure.database.session import create_engine, create_session_factory, session_scope

EMPLOYEE_COUNT = 40


class EmployeeSeed(TypedDict):
    first_name: str
    last_name: str
    middle_name: str | None
    phone: str
    birth_date: date
    gender: Gender
    photo_path: str | None


EMPLOYEE_NAMES: tuple[tuple[str, str, str | None, Gender], ...] = (
    ("Александр", "Иванов", "Петрович", Gender.male),
    ("Мария", "Петрова", "Сергеевна", Gender.female),
    ("Дмитрий", "Смирнов", "Алексеевич", Gender.male),
    ("Анна", "Кузнецова", "Игоревна", Gender.female),
    ("Сергей", "Попов", "Николаевич", Gender.male),
    ("Елена", "Васильева", "Андреевна", Gender.female),
    ("Андрей", "Соколов", "Викторович", Gender.male),
    ("Ольга", "Михайлова", "Дмитриевна", Gender.female),
    ("Николай", "Новиков", "Павлович", Gender.male),
    ("Наталья", "Федорова", "Михайловна", Gender.female),
    ("Илья", "Морозов", "Олегович", Gender.male),
    ("Татьяна", "Волкова", "Владимировна", Gender.female),
    ("Максим", "Алексеев", "Романович", Gender.male),
    ("Ирина", "Лебедева", "Павловна", Gender.female),
    ("Павел", "Семенов", "Андреевич", Gender.male),
    ("Светлана", "Егорова", "Александровна", Gender.female),
    ("Роман", "Павлов", "Ильич", Gender.male),
    ("Виктория", "Козлова", "Олеговна", Gender.female),
    ("Олег", "Степанов", "Борисович", Gender.male),
    ("Юлия", "Николаева", "Викторовна", Gender.female),
    ("Владимир", "Орлов", "Семенович", Gender.male),
    ("Ксения", "Андреева", "Денисовна", Gender.female),
    ("Евгений", "Макаров", "Васильевич", Gender.male),
    ("Алина", "Захарова", "Романовна", Gender.female),
    ("Артем", "Зайцев", "Евгеньевич", Gender.male),
    ("Дарья", "Соловьева", "Петровна", Gender.female),
    ("Константин", "Борисов", "Максимович", Gender.male),
    ("Полина", "Яковлева", "Ильинична", Gender.female),
    ("Михаил", "Григорьев", "Денисович", Gender.male),
    ("Екатерина", "Романова", "Сергеевна", Gender.female),
    ("Денис", "Воробьев", "Артемович", Gender.male),
    ("Валерия", "Сергеева", "Борисовна", Gender.female),
    ("Георгий", "Кузьмин", "Валерьевич", Gender.male),
    ("Анастасия", "Фролова", "Евгеньевна", Gender.female),
    ("Виктор", "Анисимов", "Георгиевич", Gender.male),
    ("Вероника", "Медведева", "Станиславовна", Gender.female),
    ("Станислав", "Тихонов", "Юрьевич", Gender.male),
    ("Людмила", "Комарова", "Владиславовна", Gender.female),
    ("Руслан", "Белов", "Константинович", Gender.male),
    ("Софья", "Киселева", "Артемовна", Gender.female),
)


def build_seed_employees() -> list[EmployeeSeed]:
    employees: list[EmployeeSeed] = []

    for index, (first_name, last_name, middle_name, gender) in enumerate(EMPLOYEE_NAMES, start=1):
        employees.append(
            {
                "first_name": first_name,
                "last_name": last_name,
                "middle_name": middle_name,
                "phone": f"+7900{index:07d}",
                "birth_date": date(
                    1978 + index % 24,
                    index % 12 + 1,
                    index * 3 % 28 + 1,
                ),
                "gender": gender,
                "photo_path": None,
            }
        )

    return employees


async def get_existing_seed_phones(session: AsyncSession, phones: list[str]) -> set[str]:
    rows = await session.scalars(select(Employee.phone).where(Employee.phone.in_(phones)))
    return set(rows)


async def seed_employees() -> tuple[int, int]:
    settings = get_settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    try:
        async with session_scope(session_factory) as session:
            seed_data = build_seed_employees()
            phones = [employee["phone"] for employee in seed_data]
            existing_phones = await get_existing_seed_phones(session, phones)
            new_employees = [
                Employee(**employee)
                for employee in seed_data
                if employee["phone"] not in existing_phones
            ]

            session.add_all(new_employees)
            return len(new_employees), len(existing_phones)
    finally:
        await engine.dispose()


def main() -> None:
    created_count, skipped_count = asyncio.run(seed_employees())
    print(
        "Готово: "
        f"создано {created_count}, "
        f"пропущено {skipped_count}, "
        f"всего тестовых записей {EMPLOYEE_COUNT}."
    )


if __name__ == "__main__":
    main()
