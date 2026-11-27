"""검색기 단독 테스트.  python scripts/try_retrieve.py "질문" [top_k]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.retriever import search  # noqa: E402

question = sys.argv[1] if len(sys.argv) > 1 else "보고서 요약"
k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
print(f"질문: {question}  (top_k={k})")
for c in search(question, top_k=k):
    preview = c.content.replace("\n", " ")[:80]
    print(f"  #{c.rank} score={c.score}  id={c.id}  {preview}")