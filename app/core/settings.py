"""환경 설정 (.env 로딩). 다른 모듈은 get_settings()만 사용한다."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "langchain-report-assistant"
    app_version: str = "0.1.0"
    app_env: str = "dev"

    # 서버
    host: str = "127.0.0.1"
    port: int = 8000

    # DB (health/ready 에서만 선택적으로 확인)
    database_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()