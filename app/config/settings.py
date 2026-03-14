from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    host: str
    port: int = 5432
    user: str
    password: str


class AppSettings(BaseSettings):
    database: DatabaseSettings

    api_port: int
    secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
