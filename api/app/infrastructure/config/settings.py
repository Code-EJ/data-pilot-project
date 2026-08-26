from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://projetopiloto:projetopiloto@db:5432/projetopiloto"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    jwt_secret: str = Field(
        default="local-development-only-change-this-secret-key",
        min_length=32,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def reject_default_jwt_secret_in_production(self) -> "Settings":
        if self.app_env == "production" and self.jwt_secret.startswith("local-development-only"):
            raise ValueError("JWT_SECRET precisa ser definido em produção.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
