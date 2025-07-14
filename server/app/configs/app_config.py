from typing import Literal
from pydantic import (
    AnyUrl,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    PROJECT_NAME: str = "THAI TRAVEL CO PAY"
    API_STR: str = "/api"

    REFRESH_SECRET_KEY: str = "refresh_secret_key"
    REFRESH_TOKEN_EXPIRE: int = 10080
    ACCESS_SECRET_KEY: str = "access_secret_key"
    ACCESS_TOKEN_EXPIRE: int = 10080
    ALGORITHM: str = "HS256"

    FRONTEND_URL: str = ""
    BACKEND_URL: list[AnyUrl] | str = []

    SQLITE_DATABASE_PATH: str = "instance.db"

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        if isinstance(self.BACKEND_URL, str):
            return self.BACKEND_URL.split(",") + [self.FRONTEND_URL]
        return [str(origin) for origin in self.BACKEND_URL] + [self.FRONTEND_URL]

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        uri = f"sqlite+aiosqlite:///{self.SQLITE_DATABASE_PATH}"
        return uri


app_config = AppConfig()
