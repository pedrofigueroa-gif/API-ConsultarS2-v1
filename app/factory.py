from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import router
from app.core.config import Settings, get_settings
from app.core.problems import ApiProblem
from app.db.segundometro import MySqlSegundometroRepository, SegundometroRepository


def create_app(
    settings: Settings | None = None,
    repository: SegundometroRepository | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    app.state.settings = settings
    app.state.segundometro_repository = repository or MySqlSegundometroRepository(settings)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", "").strip() or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(ApiProblem)
    async def api_problem_handler(request: Request, exc: ApiProblem):
        return _problem_response(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        errors = [{"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]} for error in exc.errors()]
        return _problem_response(request, ApiProblem(422, "VALIDATION_ERROR", "Solicitud inválida", "El id_credito no cumple el contrato.", errors))

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException):
        title = "Recurso no encontrado" if exc.status_code == 404 else "Error HTTP"
        return _problem_response(request, ApiProblem(exc.status_code, "HTTP_ERROR", title, str(exc.detail)))

    @app.exception_handler(Exception)
    async def unexpected_handler(request: Request, exc: Exception):
        return _problem_response(request, ApiProblem(500, "INTERNAL_SERVER_ERROR", "Error interno", "Ocurrió un error no previsto."))

    app.include_router(router)
    return app


def _problem_response(request: Request, exc: ApiProblem) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        media_type="application/problem+json",
        headers={"X-Request-ID": request_id},
        content={
            "type": f"https://api.example.invalid/problems/{exc.code.lower().replace('_', '-')}",
            "title": exc.title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.url.path,
            "code": exc.code,
            "traceId": request_id,
            "errors": exc.errors,
        },
    )
