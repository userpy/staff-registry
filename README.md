# Employee Registry

FastAPI-приложение для управления сотрудниками с PostgreSQL, async SQLAlchemy, Alembic, Jinja2, Tailwind CSS и vanilla JavaScript.

## Быстрый старт

1. Создайте файл `.env` из примера:

```bash
cp .env.example .env
```

2. Выполните команду:

```bash
docker compose up -d db
```

3. Примените миграции:

```bash
docker compose run --rm --build app alembic upgrade head
```

4.  Добавте демонстрационные данные:
Скрипт добавляет 40 тестовых сотрудников в таблицу `employees`. Повторный запуск
пропускает уже созданные тестовые записи по номеру телефона.

Через Docker:

```bash
docker compose run --rm --build app python -m scripts.seed_employees
```

4. Запустите приложение:

```bash
docker compose up --build app
```

5. Перейдите по адресу `http://localhost:8000`.

## Тестовые данные

Скрипт добавляет 40 тестовых сотрудников в таблицу `employees`. Повторный запуск
пропускает уже созданные тестовые записи по номеру телефона.

Через Docker:

```bash
docker compose run --rm --build app python -m scripts.seed_employees
```

Локально, после запуска PostgreSQL и применения миграций:

```bash
python -m scripts.seed_employees
```

## Стек

- Python 3.13
- FastAPI
- SQLAlchemy 2.0 Async ORM
- Alembic
- Pydantic v2
- PostgreSQL
- Jinja2-шаблоны
- Tailwind CSS из локальных статических файлов
- Vanilla JavaScript
- Docker Compose

## Архитектура

Приложение построено по принципам чистой архитектуры. Зависимости направлены внутрь:
`presentation` и `infrastructure` зависят от `application` и `domain`, а
`domain` не зависит от фреймворков.

```text
app/
  domain/          Бизнес-перечисления и чистые доменные сущности.
  application/     DTO, сценарии использования, порты и исключения приложения.
  infrastructure/  Модели SQLAlchemy, репозитории, DB-сессия, хранение файлов.
  presentation/    Роуты FastAPI, настройка зависимостей, обработчики HTTP-ошибок.
  core/            Runtime-конфигурация.
```

## Настройка

```bash
cp .env.example .env
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск через Docker

```bash
cp .env.example .env
docker compose up -d db
docker compose run --rm --build app alembic upgrade head
docker compose up --build app
```

Откройте `http://localhost:8000`.

Миграции Alembic нужно применить перед первым запуском приложения.
Для Docker используется хост базы `db`, а для локального запуска в `.env.example` указан `localhost`.

## Локальная разработка

Запустите PostgreSQL:

```bash
docker compose up -d db
```

Для локального запуска приложения оставьте `POSTGRES_HOST=localhost`, как указано в `.env.example`.

Примените миграции:

```bash
alembic upgrade head
```

Запустите приложение:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Миграции

Создать ревизию:

```bash
alembic revision --autogenerate -m "init"
```

Применить миграции:

```bash
alembic upgrade head
```

## Проверки качества

```bash
ruff check .
black --check .
pytest
```

Docker-образ использует Python 3.13. Для локальных проверок создайте виртуальное окружение на Python 3.13 перед установкой `requirements.txt`.

## Роуты

- `GET /health`
- `GET /employees`
- `GET /employees/create`
- `POST /employees/create`
- `GET /employees/{id}/edit`
- `POST /employees/{id}/edit`
- `POST /employees/{id}/delete`

## Переменные окружения

Необходимые переменные описаны в `.env.example`.
`DATABASE_URL` можно не указывать: приложение сформирует его из настроек PostgreSQL.
Если `DATABASE_URL` задан вручную, он будет использован вместо собранного значения.

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `SECRET_KEY`
- `DEBUG`
