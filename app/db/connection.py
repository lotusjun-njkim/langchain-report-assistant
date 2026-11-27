"""읽기 전용 Transaction.

이 서비스는 조회만 한다. 연결 자체를 READ ONLY로 열어 두면
실수로 INSERT/UPDATE가 들어가도 DB가 거부한다.
"""
from contextlib import contextmanager
from typing import Iterator

import psycopg

from app.core.settings import get_settings


class DatabaseNotConfigured(RuntimeError):
    """DB 접속 정보가 .env에 없을 때."""


@contextmanager
def read_only_cursor(timeout: int = 3) -> Iterator[psycopg.Cursor]:
    dsn = get_settings().dsn
    if not dsn:
        raise DatabaseNotConfigured(
            "DB 접속 정보 없음: .env에 DATABASE_URL 또는 DB_HOST/DB_NAME/DB_USER를 설정하세요"
        )
    with psycopg.connect(dsn, connect_timeout=timeout) as conn:
        conn.read_only = True
        with conn.cursor() as cur:
            yield cur