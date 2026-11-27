"""DB 구조 점검 (읽기 전용). 테이블, 컬럼, vector 차원, 행 수를 출력한다.
사용: python scripts/inspect_db.py   (프로젝트 루트에서 실행)
비밀번호 등 접속 정보는 출력하지 않는다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.connection import read_only_cursor  # noqa: E402


def main() -> None:
    with read_only_cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY 1"
        )
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            cur.execute(f'SELECT count(*) FROM "{t}"')
            n = cur.fetchone()[0]
            print(f"\n[{t}]  행 수: {n}")
            cur.execute(
                """
                SELECT a.attname, format_type(a.atttypid, a.atttypmod)
                FROM pg_attribute a
                WHERE a.attrelid = %s::regclass AND a.attnum > 0 AND NOT a.attisdropped
                ORDER BY a.attnum
                """,
                (f'public."{t}"',),
            )
            for name, typ in cur.fetchall():
                mark = "   <- 벡터 컬럼" if typ.startswith("vector") else ""
                print(f"    {name:<24} {typ}{mark}")


if __name__ == "__main__":
    main()