from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates

from app.application.services.employee_service import EmployeeService
from app.core.config import Settings, get_settings
from app.infrastructure.database.session import get_session_factory, session_scope
from app.infrastructure.repositories.employee_repository import EmployeeRepository
from app.infrastructure.storage.file_storage import FileStorage


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory = get_session_factory(request.app.state)
    async with session_scope(session_factory) as session:
        yield session


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


def get_employee_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EmployeeRepository:
    return EmployeeRepository(session)


def get_file_storage(settings: Annotated[Settings, Depends(get_settings)]) -> FileStorage:
    return FileStorage(
        upload_directory=settings.upload_directory,
        upload_url_prefix=settings.upload_url_prefix,
        allowed_extensions=settings.allowed_photo_extensions,
        max_size_bytes=settings.max_upload_size_bytes,
    )


def get_employee_service(
    repository: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    file_storage: Annotated[FileStorage, Depends(get_file_storage)],
) -> EmployeeService:
    return EmployeeService(repository=repository, file_storage=file_storage)
