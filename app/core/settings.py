"""환경 설정 (.env 로딩). 다른 모듈은 get_settings()만 사용한다.

DB 접속은 두 방식 중 하나만 있으면 된다.
  1) DATABASE_URL=postgresql://user:password@host:5432/dbname
  2) DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD  (POSTGRES_*, PG* 이름도 허용)
"""
from functools import lru_cache
from urllib.parse import quote

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8-sig", extra="ignore"
    )

    app_name: str = "langchain-report-assistant"
    app_version: str = "0.1.0"
    app_env: str = "dev"
    host: str = "127.0.0.1"
    port: int = 8000

    database_url: str = ""
    db_host: str = Field("", validation_alias=AliasChoices("DB_HOST", "POSTGRES_HOST", "PGHOST"))
    db_port: int = Field(5432, validation_alias=AliasChoices("DB_PORT", "POSTGRES_PORT", "PGPORT"))
    db_name: str = Field("", validation_alias=AliasChoices("DB_NAME", "POSTGRES_DB", "PGDATABASE"))
    db_user: str = Field("", validation_alias=AliasChoices("DB_USER", "POSTGRES_USER", "PGUSER"))
    db_password: str = Field("", validation_alias=AliasChoices("DB_PASSWORD", "POSTGRES_PASSWORD", "PGPASSWORD"))

    @property
    def dsn(self) -> str:
        """DATABASE_URL이 있으면 그대로, 없으면 개별 값으로 조립. 둘 다 없으면 빈 문자열."""
        if self.database_url:
            return self.database_url
        if self.db_host and self.db_name and self.db_user:
            pw = f":{quote(self.db_password, safe='')}" if self.db_password else ""
            return f"postgresql://{quote(self.db_user, safe='')}{pw}@{self.db_host}:{self.db_port}/{self.db_name}"
        return ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
