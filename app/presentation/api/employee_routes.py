from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from pydantic import ValidationError
from starlette.responses import RedirectResponse, Response
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates

from app.application.dto.employee import EmployeeCreate, EmployeeFilterParams, EmployeeUpdate
from app.application.exceptions import ValidationException
from app.application.services.employee_service import EmployeeService
from app.domain.employee import GENDER_LABELS, Gender
from app.presentation.api.dependencies import get_employee_service, get_templates

router = APIRouter()


@router.get("/", include_in_schema=False)
async def index() -> RedirectResponse:
    return RedirectResponse(url="/employees", status_code=HTTP_303_SEE_OTHER)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/employees")
async def list_employees(
    request: Request,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    search: Annotated[str | None, Query(max_length=100)] = None,
    gender: str | None = None,
    age_from: str | None = None,
    age_to: str | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
) -> Response:
    try:
        filters = EmployeeFilterParams(
            search=search,
            gender=_blank_to_none(gender),
            age_from=_blank_to_none(age_from),
            age_to=_blank_to_none(age_to),
            page=page,
        )
    except ValidationError as exc:
        raise ValidationException.from_pydantic(exc, form_data={}) from exc

    employee_page = await service.list_employees(filters)
    return templates.TemplateResponse(
        request,
        "employees/list.html",
        {
            "request": request,
            "employee_page": employee_page,
            "filters": filters,
            "genders": list(Gender),
            "gender_labels": GENDER_LABELS,
        },
    )


@router.get("/employees/create")
async def new_employee(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    return templates.TemplateResponse(
        request,
        "employees/form.html",
        {
            "request": request,
            "employee": {},
            "errors": {},
            "genders": list(Gender),
            "gender_labels": GENDER_LABELS,
            "is_edit": False,
            "employee_id": None,
            "action_url": str(request.url_for("create_employee")),
        },
    )


@router.post("/employees/create")
async def create_employee(
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    last_name: Annotated[str, Form()],
    first_name: Annotated[str, Form()],
    middle_name: Annotated[str | None, Form()] = None,
    phone: Annotated[str, Form()] = "",
    birth_date: Annotated[str, Form()] = "",
    gender: Annotated[str, Form()] = "",
    photo: Annotated[UploadFile | None, File()] = None,
) -> RedirectResponse:
    form_data = _form_payload(last_name, first_name, middle_name, phone, birth_date, gender)
    try:
        employee_data = EmployeeCreate.model_validate(form_data)
    except ValidationError as exc:
        raise ValidationException.from_pydantic(exc, form_data=form_data) from exc

    await service.create_employee(employee_data, photo, form_data=form_data)
    return RedirectResponse(url="/employees", status_code=HTTP_303_SEE_OTHER)


@router.get("/employees/{employee_id}/edit")
async def edit_employee_form(
    request: Request,
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    employee = await service.get_employee(employee_id)
    return templates.TemplateResponse(
        request,
        "employees/form.html",
        {
            "request": request,
            "employee": employee.model_dump(mode="json"),
            "errors": {},
            "genders": list(Gender),
            "gender_labels": GENDER_LABELS,
            "is_edit": True,
            "employee_id": employee_id,
            "action_url": str(request.url_for("update_employee", employee_id=employee_id)),
        },
    )


@router.post("/employees/{employee_id}/edit")
async def update_employee(
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    last_name: Annotated[str, Form()],
    first_name: Annotated[str, Form()],
    middle_name: Annotated[str | None, Form()] = None,
    phone: Annotated[str, Form()] = "",
    birth_date: Annotated[str, Form()] = "",
    gender: Annotated[str, Form()] = "",
    photo: Annotated[UploadFile | None, File()] = None,
) -> RedirectResponse:
    form_data = _form_payload(last_name, first_name, middle_name, phone, birth_date, gender)
    try:
        employee_data = EmployeeUpdate.model_validate(form_data)
    except ValidationError as exc:
        raise ValidationException.from_pydantic(exc, form_data=form_data) from exc

    await service.update_employee(employee_id, employee_data, photo, form_data=form_data)
    return RedirectResponse(url="/employees", status_code=HTTP_303_SEE_OTHER)


@router.post("/employees/{employee_id}/delete")
async def delete_employee(
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> RedirectResponse:
    await service.delete_employee(employee_id)
    return RedirectResponse(url="/employees", status_code=HTTP_303_SEE_OTHER)


def _form_payload(
    last_name: str,
    first_name: str,
    middle_name: str | None,
    phone: str,
    birth_date: str,
    gender: str,
) -> dict[str, Any]:
    return {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "phone": phone,
        "birth_date": birth_date,
        "gender": gender,
    }


def _blank_to_none(value: str | None) -> str | None:
    if value == "":
        return None
    return value
