"""POST /api/v1/agent/ask"""
from fastapi import APIRouter, HTTPException

from app.agent import run_agent
from app.schemas.agent import AskRequest, AskResponse

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    try:
        return run_agent(req)
    except Exception as exc:  # 이후 services/errors.py 의 예외 체계로 교체
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")