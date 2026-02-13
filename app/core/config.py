"""Global application configuration powered by Pydantic settings."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized strongly typed configuration state."""

    project_name: str = "Cred Authentication API"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./app.db"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    mysql_host: str = "db"
    mysql_port: int = 3306
    mysql_user: str = "app_user"
    mysql_password: str = "app_password"
    mysql_database: str = "cred_db"
    password_reset_token_expire_minutes: int = 30
    password_reset_base_url: str = "https://example.com/reset-password"

    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_sender: str = "no-reply@example.com"
    smtp_use_tls: bool = True
    smtp_suppress_send: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    @property
    def mysql_connection_uri(self) -> str:
        """Helper that surfaces a RFC-1738 compliant MySQL connection string."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@"
            f"{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so expensive env parsing happens once."""
    return Settings()
