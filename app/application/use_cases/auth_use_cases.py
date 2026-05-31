from fastapi import HTTPException

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.domain.repositories import AuthRepositoryPort
from app.schemas import LoginIn, RegisterIn

settings = get_settings()


class AuthUseCases:
    """AuthUseCases — authentication and token issuing scenarios.

    Date: 31-05-2026
    Author: Team 4
    """

    def __init__(self, repo: AuthRepositoryPort):
        self.repo = repo

    def register(self, payload: RegisterIn) -> dict:
        if payload.role != "candidate":
            raise HTTPException(status_code=403, detail="Self-registration is allowed for candidates only")
        exists = self.repo.get_by_email(payload.email)
        if exists:
            raise HTTPException(status_code=422, detail="Email already registered")
        user = self.repo.create_user(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        token = create_access_token(user.id, user.role.value)
        return {
            "accessToken": token,
            "tokenType": "Bearer",
            "expiresInSec": settings.jwt_expire_minutes * 60,
            "user": {
                "id": user.id,
                "fullName": user.full_name,
                "email": user.email,
                "role": user.role.value,
            },
        }

    def login(self, payload: LoginIn) -> dict:
        user = self.repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(user.id, user.role.value)
        return {
            "accessToken": token,
            "tokenType": "Bearer",
            "expiresInSec": settings.jwt_expire_minutes * 60,
            "user": {
                "id": user.id,
                "fullName": user.full_name,
                "email": user.email,
                "role": user.role.value,
            },
        }
