"""SELECT 조회 계약. 모든 DB 읽기는 이 파일의 함수를 거친다."""
from app.db.connection import read_only_cursor


def ping() -> bool:
    with read_only_cursor() as cur:
        cur.execute("SELECT 1")
        return cur.fetchone()[0] == 1


def has_pgvector() -> bool:
    with read_only_cursor() as cur:
        cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        return cur.fetchone() is not None


def list_public_tables() -> list[str]:
    with read_only_cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        return [row[0] for row in cur.fetchall()]