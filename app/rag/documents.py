"""검색 결과 Document · Metadata."""
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class RetrievedChunk:
    id: str  # report_id
    content: str  # reports.overview (임베딩의 원문)
    score: float  # 코사인 유사도 (클수록 비슷함)
    rank: int
    metadata: dict = field(default_factory=dict)  # category_code, category_name, index_status, stale

    def to_dict(self) -> dict:
        return asdict(self)