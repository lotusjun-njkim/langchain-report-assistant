"""Agent 실행부.

지금은 LLM 연결 전 단계라서 질문을 그대로 돌려주는 스텁이다.
이후 create_agent + Structured Output 으로 이 함수 내부만 교체하면 되고,
API 계층(app/api/agent.py)은 바뀌지 않는다.
"""
from app.schemas.agent import AskRequest, AskResponse


def run_agent(req: AskRequest) -> AskResponse:
    scope = f" (report_id={req.report_id})" if req.report_id else ""
    return AskResponse(
        answer=f"[stub] 질문을 받았습니다: {req.question}{scope}",
        status="stub",
        sources=[],
    )