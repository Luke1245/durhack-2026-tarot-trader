import re

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

    database_url: str = "postgresql+asyncpg://localhost:5432/tarot"
    cors_origins: list[str] = ["http://localhost:5173"]
    finnhub_api_key: str = ""
    gemini_api_key: str = ""

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_scheme(cls, v: str) -> str:
        # Providers (TigerData, Heroku, ...) often ship `postgres://` URLs,
        # which SQLAlchemy doesn't register; coerce to the asyncpg dialect.
        if v.startswith("postgres://"):
            v = "postgresql+asyncpg://" + v.removeprefix("postgres://")
        # asyncpg handles TLS via connect_args, not URL query params, and its
        # default (ssl=prefer) already negotiates SSL — which hosted providers
        # require. Strip psycopg-style sslmode/ssl params rather than translate.
        v = re.sub(r"[?&](sslmode|ssl)=[^&\s]+", "", v)
        v = re.sub(r"\?$", "", v)
        return v


def get_settings() -> Settings:
    return Settings()
