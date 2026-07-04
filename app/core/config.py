from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(
        default="",
        alias="DATABASE_URL",
    )
    postgres_user: str = Field(default="employee_user", alias="POSTGRES_USER")
    postgres_password: str = Field(default="employee_password", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="employee_registry", alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    debug: bool = Field(default=False, alias="DEBUG")

    app_name: str = "Реестр сотрудников"
    template_directory: Path = Path("app/templates")
    static_directory: Path = Path("app/static")
    upload_directory: Path = Path("app/static/uploads")
    upload_url_prefix: str = "/static/uploads"
    max_upload_size_bytes: int = 200 * 1024
    allowed_photo_extensions: frozenset[str] = frozenset({"jpg", "jpeg", "png"})

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if not self.database_url:
            self.database_url = (
                "postgresql+asyncpg://"
                f"{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
