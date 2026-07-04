import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.application.exceptions import (
    EmployeeNotFound,
    FileUploadException,
    ValidationException,
)
from app.domain.employee import GENDER_LABELS, Gender

logger = logging.getLogger(__name__)


def register_exception_handlers(app: object) -> None:
    app.add_exception_handler(ValidationException, _validation_exception_handler)
    app.add_exception_handler(FileUploadException, _validation_exception_handler)
    app.add_exception_handler(EmployeeNotFound, _employee_not_found_handler)
    app.add_exception_handler(RequestValidationError, _request_validation_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)


async def _validation_exception_handler(request: Request, exc: ValidationException) -> Response:
    if _wants_html(request):
        return await _render_form_with_errors(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "errors": exc.errors},
    )


async def _employee_not_found_handler(request: Request, exc: EmployeeNotFound) -> Response:
    if _wants_html(request):
        return HTMLResponse(content=f"<h1>{exc.message}</h1>", status_code=HTTP_404_NOT_FOUND)
    return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"detail": exc.message})


async def _request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> Response:
    logger.warning("request_validation_error", extra={"errors": exc.errors()})
    if _wants_html(request):
        return HTMLResponse(
            content="<h1>Некорректный запрос.</h1>",
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


async def _unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    logger.exception("unhandled_error", exc_info=exc)
    if _wants_html(request):
        return HTMLResponse(
            content="<h1>Внутренняя ошибка сервера.</h1>",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера."},
    )


async def _render_form_with_errors(request: Request, exc: ValidationException) -> Response:
    templates = request.app.state.templates
    employee_id = request.path_params.get("employee_id")
    is_edit = employee_id is not None
    return templates.TemplateResponse(
        request,
        "employees/form.html",
        {
            "request": request,
            "employee": exc.form_data,
            "errors": exc.errors,
            "genders": list(Gender),
            "gender_labels": GENDER_LABELS,
            "is_edit": is_edit,
            "employee_id": employee_id,
            "action_url": str(request.url),
        },
        status_code=exc.status_code,
    )


def _wants_html(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept or "*/*" in accept
