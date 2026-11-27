"""검색 결과 Document."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    content: str
    score: float  # 코사인 유사도 (클수록 비슷함)
    rank: int

    def to_dict(self) -> dict:
        return asdict(self)