"""pgvector Top-k 검색 (코사인 거리, 읽기 전용)."""
import re

from psycopg import sql

from app.core.settings import get_settings
from app.db.connection import read_only_cursor
from app.rag.documents import RetrievedChunk
from app.rag.embeddings import embed_query

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _ident(name: str) -> sql.Identifier:
    """테이블·컬럼 이름은 .env 에서 오므로 형식을 검증한 뒤 안전하게 인용한다."""
    parts = name.split(".")
    if not all(_IDENT.match(p) for p in parts):
        raise ValueError(f"허용되지 않는 식별자: {name!r}")
    return sql.Identifier(*parts)


def search(question: str, top_k: int | None = None, report_id: str | None = None) -> list[RetrievedChunk]:
    s = get_settings()
    k = top_k or s.rag_top_k
    qvec = embed_query(question)
    literal = "[" + ",".join(f"{x:.6f}" for x in qvec) + "]"

    use_report = bool(report_id and s.rag_report_col)
    where = (
        sql.SQL("WHERE {}::text = %s").format(_ident(s.rag_report_col))
        if use_report
        else sql.SQL("")
    )
    query = sql.SQL(
        "SELECT {id}::text, {text}, 1 - ({vec} <=> %s::vector) AS score "
        "FROM {table} {where} ORDER BY {vec} <=> %s::vector LIMIT %s"
    ).format(
        id=_ident(s.rag_id_col),
        text=_ident(s.rag_text_col),
        vec=_ident(s.rag_vector_col),
        table=_ident(s.rag_table),
        where=where,
    )
    params: list = [literal]
    if use_report:
        params.append(report_id)
    params += [literal, k]

    with read_only_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
    return [
        RetrievedChunk(id=r[0], content=r[1], score=round(float(r[2]), 4), rank=i)
        for i, r in enumerate(rows, 1)
    ]