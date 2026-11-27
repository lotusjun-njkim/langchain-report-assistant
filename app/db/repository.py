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


def embedding_models() -> list[tuple[str, int]]:
    """report_embeddings 에 저장된 벡터를 만든 모델 이름과 건수."""
    with read_only_cursor() as cur:
        cur.execute(
            "SELECT model_name, count(*) FROM report_embeddings GROUP BY model_name ORDER BY 2 DESC"
        )
        return [(r[0], r[1]) for r in cur.fetchall()]