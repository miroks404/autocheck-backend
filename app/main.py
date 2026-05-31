from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.assignments import router as assignments_router
from app.api.auth import router as auth_router
from app.api.candidates import router as candidates_router
from app.api.reports import router as reports_router
from app.api.submissions import router as submissions_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.request_context import set_request_id
from app.core.response import fail

settings = get_settings()
configure_logging()
logger = get_logger("API")

openapi_tags = [
    {"name": "auth", "description": "Регистрация, логин, профиль и выход пользователя."},
    {"name": "assignments", "description": "CRUD операций с тестовыми заданиями."},
    {"name": "submissions", "description": "Загрузка решений, статусы проверки, результаты, вердикты, SSE и AI-review."},
    {"name": "candidates", "description": "Работа со списком кандидатов и карточкой кандидата."},
    {"name": "reports", "description": "Агрегированная статистика и рейтинг кандидатов."},
]

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "REST API AutoCheckMobile. "
        "Все ответы отдаются в формате `{data, error, meta}`. "
        "Все эндпоинты требуют Bearer Token, кроме `/auth/login` и `/auth/register`."
    ),
    contact={"name": "AutoCheckMobile Team"},
    openapi_tags=openapi_tags,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.cors_allow_all else settings.cors_origins,
    allow_origin_regex=None if settings.cors_allow_all else settings.cors_allow_origin_regex,
    # JWT uses Authorization header, so cookies are not required.
    allow_credentials=False if settings.cors_allow_all else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    set_request_id(request_id)
    logger.info("Начало запроса — method=%s path=%s requestId=%s", request.method, request.url.path, request_id)
    response = await call_next(request)
    logger.debug("Успешный ответ — method=%s path=%s status=%s", request.method, request.url.path, response.status_code)
    response.headers["X-Request-Id"] = request_id
    return response


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(request: Request, exc: StarletteHTTPException):  # noqa: ARG001
    logger.error("Ошибка HTTP — method=%s path=%s status=%s detail=%s", request.method, request.url.path, exc.status_code, exc.detail)
    return fail(
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        details=None,
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request: Request, exc: RequestValidationError):  # noqa: ARG001
    logger.error("Ошибка валидации — method=%s path=%s details=%s", request.method, request.url.path, exc.errors())
    return fail(
        code="VALIDATION_ERROR",
        message="Validation failed",
        details=exc.errors(),
        status_code=422,
    )


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception):  # noqa: ARG001
    logger.error("Необработанная ошибка — method=%s path=%s error=%s", request.method, request.url.path, str(exc))
    return fail(
        code="INTERNAL_ERROR",
        message="Internal server error",
        details=str(exc),
        status_code=500,
    )


api_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(assignments_router, prefix=api_prefix)
app.include_router(submissions_router, prefix=api_prefix)
app.include_router(candidates_router, prefix=api_prefix)
app.include_router(reports_router, prefix=api_prefix)


@app.get("/health")
def health():
    return {"status": "ok"}
