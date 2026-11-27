"""CUDA E5 query 임베딩.

E5 모델은 질문에는 "query: ", 저장 문서에는 "passage: " 접두어를 붙여야 성능이 나온다.
여기서는 질문(query)만 만든다. GPU가 없으면 조용히 CPU로 넘어가지 않고 오류를 낸다.
"""
from functools import lru_cache

from app.core.settings import get_settings


class CudaNotAvailable(RuntimeError):
    """CUDA GPU를 쓸 수 없을 때."""


@lru_cache
def _load_model():
    import torch

    if not torch.cuda.is_available():
        raise CudaNotAvailable(
            "CUDA GPU를 찾을 수 없습니다. NVIDIA 드라이버와 CUDA 버전 PyTorch 설치를 확인하세요 "
            "(python scripts/preflight.py)"
        )
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(get_settings().e5_model_name, device="cuda")


def embed_query(text: str) -> list[float]:
    text = text.strip()
    if not text:
        raise ValueError("빈 질문은 임베딩할 수 없습니다")
    if not text.lower().startswith("query:"):
        text = f"query: {text}"
    vec = _load_model().encode(text, normalize_embeddings=True, convert_to_numpy=True)
    return vec.tolist()