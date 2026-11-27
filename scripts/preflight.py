"""GPU / DB 준비 확인.  python scripts/preflight.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.preflight import run_all  # noqa: E402

results = run_all()
for r in results:
    print(f"[{'OK' if r['ok'] else 'FAIL'}] {r['name']}: {r['detail']}")
sys.exit(0 if all(r["ok"] for r in results) else 1)