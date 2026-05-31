from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.use_cases.auth_use_cases import AuthUseCases
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.response import ok
from app.deps import get_current_user
from app.infrastructure.repositories import SqlAlchemyAuthRepository
from app.models import User
from app.schemas import LoginIn, RegisterIn

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger("AuthController")


@router.post("/register", summary="Регистрация пользователя")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    logger.info("Критическое действие — регистрация email=%s", payload.email)
    use_case = AuthUseCases(SqlAlchemyAuthRepository(db))
    data = use_case.register(payload)
    return ok(data, status_code=201)


@router.post("/login", summary="Авторизация пользователя")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    logger.info("Критическое действие — логин email=%s", payload.email)
    use_case = AuthUseCases(SqlAlchemyAuthRepository(db))
    return ok(use_case.login(payload))


@router.post("/logout", summary="Выход пользователя")
def logout(user: User = Depends(get_current_user)):
    logger.info("Критическое действие — выход userId=%s", user.id)
    return ok({"message": "Logged out", "userId": user.id})


@router.get("/profile", summary="Профиль текущего пользователя")
def profile(user: User = Depends(get_current_user)):
    logger.info("Профиль запрошен — userId=%s", user.id)
    return ok({"id": user.id, "email": user.email, "fullName": user.full_name, "role": user.role.value})
