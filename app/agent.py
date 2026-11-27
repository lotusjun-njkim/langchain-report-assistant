"""POST /api/v1/agent/ask 의 요청·응답 계약."""
from typing import Literal

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="사용자 질문")
    report_id: str | None = Field(default=None, description="특정 보고서로 한정할 때 사용")


class AskResponse(BaseModel):
    answer: str
    status: Literal["ok", "stub", "error"] = "ok"
    sources: list[str] = Field(default_factory=list, description="근거로 사용한 chunk id")
