from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Buddy API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./storage/app.db"
    proof_storage_dir: str = "storage/proofs"
    default_timezone: str = "Asia/Shanghai"
    dev_token_prefix: str = "dev"
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.proof_storage_dir).mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()

