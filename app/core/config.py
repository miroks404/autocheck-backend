from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings — centralized application configuration service.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - cors_origins() -> list[str]
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="AutoCheckMobile Backend", alias="APP_NAME")
    app_url: str = Field(default="http://localhost:8000", alias="APP_URL")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=120, alias="JWT_EXPIRE_MINUTES")

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")

    ai_api_key: str | None = Field(default=None, alias="AI_API_KEY")
    ai_base_url: str = Field(default="https://api.openai.com", alias="AI_BASE_URL")
    ai_model: str = Field(default="gpt-4o-mini", alias="AI_MODEL")

    checker_storage_volume: str = Field(default="autocheck_submission_storage", alias="CHECKER_STORAGE_VOLUME")
    checker_storage_mount: str = Field(default="/app/storage", alias="CHECKER_STORAGE_MOUNT")

    cors_origins_raw: str = Field(default="http://localhost:3000,http://localhost:5173", alias="CORS_ORIGINS")
    cors_allow_origin_regex: str = Field(
        default=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?$",
        alias="CORS_ALLOW_ORIGIN_REGEX",
    )

    @property
    def cors_origins(self) -> List[str]:
        return [item.strip() for item in self.cors_origins_raw.split(",") if item.strip()]

    @property
    def cors_allow_all(self) -> bool:
        return self.cors_origins_raw.strip() == "*"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
