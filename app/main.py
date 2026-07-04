import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from app.core.config import get_settings
from app.infrastructure.database.session import create_engine, create_session_factory
from app.presentation.api.employee_routes import router as employee_router
from app.presentation.exception_handlers import register_exception_handlers

logger = logging.getLogger(__name__)


def configure_logging(debug: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.debug)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        settings.upload_directory.mkdir(parents=True, exist_ok=True)
        engine = create_engine(settings)
        application.state.engine = engine
        application.state.session_factory = create_session_factory(engine)
        application.state.templates = Jinja2Templates(
            directory=str(settings.template_directory),
        )
        yield
        await engine.dispose()

    application = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    application.mount(
        "/static",
        StaticFiles(directory=str(settings.static_directory)),
        name="static",
    )
    application.include_router(employee_router)
    register_exception_handlers(application)

    @application.middleware("http")
    async def log_requests(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = time.perf_counter()
        logger.info(
            "request_start",
            extra={"method": request.method, "path": request.url.path},
        )
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "request_end",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
            },
        )
        return response

    return application


app = create_app()
