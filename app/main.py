"""FastAPI 진입점.

실행:  uvicorn app.main:app --reload --port 8000
확인:  GET  /health        -> 서버 생존 확인 (항상 200)
       GET  /health/ready  -> 의존성(DB) 준비 확인 (실패 시 503)
       POST /api/v1/agent/ask -> 질문 접수 (현재는 stub 응답)
       GET  /docs          -> Swagger UI
"""
import time
from datetime import datetime, timezone

from fastapi import FastAPI, Response, status

from app.api.agent import router as agent_router
from app.core.settings import get_settings

settings = get_settings()
START_TIME = time.time()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="LangChain Report Assistant API",
)


app.include_router(agent_router)


@app.get("/", tags=["root"])
def root() -> dict:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["health"])
def health() -> dict:
    """Liveness: 프로세스가 떠 있고 요청에 응답하는지만 확인한다.
    DB 등 외부 의존성은 보지 않으므로 항상 200이다."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "time": datetime.now(timezone.utc).isoformat(),
    }


def _check_database() -> list[dict]:
    """DB 연결, pgvector 확장, 테이블 수를 읽기 전용으로 확인한다."""
    from app.db import repository

    checks = []
    try:
        ok = repository.ping()
        checks.append({"name": "database", "ok": ok, "detail": "SELECT 1 성공" if ok else "SELECT 1 실패"})
    except Exception as exc:
        return [{"name": "database", "ok": False, "detail": f"{type(exc).__name__}: {exc}"}]
    try:
        vec = repository.has_pgvector()
        checks.append({"name": "pgvector", "ok": vec, "detail": "vector 확장 설치됨" if vec else "vector 확장 없음"})
        tables = repository.list_public_tables()
        checks.append({"name": "tables", "ok": True, "detail": f"public 테이블 {len(tables)}개"})
    except Exception as exc:
        checks.append({"name": "pgvector", "ok": False, "detail": f"{type(exc).__name__}: {exc}"})
    return checks


@app.get("/health/ready", tags=["health"])
def ready(response: Response) -> dict:
    """Readiness: 의존성이 준비됐는지 확인한다. 하나라도 실패하면 503."""
    checks = _check_database()
    all_ok = all(c["ok"] for c in checks)
    if not all_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ready" if all_ok else "not_ready", "checks": checks}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)