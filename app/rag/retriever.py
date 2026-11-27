"""pgvector Top-k 검색 (코사인 거리, 읽기 전용).

report_embeddings.embedding 으로 가까운 보고서를 찾고,
reports.overview(요약 원문)와 카테고리를 함께 돌려준다.
보고서 본문(content, progress 등)은 종류별 테이블에 있으며 db_tool 에서 조회한다.
"""
from functools import lru_cache

from app.core.settings import get_settings
from app.db import repository
from app.db.connection import read_only_cursor
from app.rag.documents import RetrievedChunk
from app.rag.embeddings import embed_query

_SQL = """
SELECT e.report_id::text,
       r.overview,
       1 - (e.embedding <=> %s::vector) AS score,
       c.code,
       c.name,
       r.index_status,
       (e.indexed_revision IS DISTINCT FROM r.revision) AS stale
FROM report_embeddings e
JOIN reports r ON r.report_id = e.report_id
LEFT JOIN report_categories c ON c.category_id = r.category_id
{where}
ORDER BY e.embedding <=> %s::vector
LIMIT %s
"""


class EmbeddingModelMismatch(RuntimeError):
    """질문 임베딩 모델이 DB 벡터를 만든 모델과 다를 때."""


def _short(name: str) -> str:
    return name.split("/")[-1].strip().lower()


@lru_cache
def _check_model(configured: str) -> None:
    models = repository.embedding_models()
    stored = {_short(m) for m, _ in models if m}
    if stored and _short(configured) not in stored:
        raise EmbeddingModelMismatch(
            f"설정된 모델({configured})이 DB에 저장된 벡터의 모델({', '.join(m for m, _ in models)})과 다릅니다. "
            f".env 에 E5_MODEL_NAME=<DB에 저장된 모델 이름> 을 지정하세요"
        )


def search(question: str, top_k: int | None = None, report_id: int | str | None = None) -> list[RetrievedChunk]:
    s = get_settings()
    k = top_k or s.rag_top_k
    _check_model(s.e5_model_name)

    qvec = embed_query(question)
    literal = "[" + ",".join(f"{x:.6f}" for x in qvec) + "]"

    params: list = [literal]
    where = ""
    if report_id is not None:
        where = "WHERE e.report_id = %s"
        params.append(int(report_id))  # 숫자가 아니면 ValueError
    params += [literal, k]

    with read_only_cursor() as cur:
        cur.execute(_SQL.format(where=where), params)
        rows = cur.fetchall()
    return [
        RetrievedChunk(
            id=r[0],
            content=r[1] or "",
            score=round(float(r[2]), 4),
            rank=i,
            metadata={"category_code": r[3], "category_name": r[4], "index_status": r[5], "stale": r[6]},
        )
        for i, r in enumerate(rows, 1)
    ]