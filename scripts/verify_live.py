"""서버가 떠 있는 상태에서 API 접속과 /health를 확인한다.

사용:  python scripts/verify_live.py [base_url]
"""
import json
import sys
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")


def get(path: str, payload: dict | None = None):
    try:
        req = urllib.request.Request(BASE + path)
        if payload is not None:
            req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:  # 503 등
        return e.code, json.loads(e.read().decode() or "{}")
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def main() -> int:
    code, body = get("/health")
    print(f"[/health] {code}\n{json.dumps(body, ensure_ascii=False, indent=2) if isinstance(body, dict) else body}")
    if code != 200 or body.get("status") != "ok":
        print("FAIL: 서버 접속 또는 /health 실패 (uvicorn이 실행 중인지, 포트가 맞는지 확인)")
        return 1
    print("PASS: /health OK")

    code, body = get("/health/ready")
    print(f"[/health/ready] {code}\n{json.dumps(body, ensure_ascii=False, indent=2)}")
    print("INFO: ready 실패는 DB 설정 문제이며 서버 자체 문제와는 별개")

    code, body = get("/api/v1/agent/ask", {"question": "연결 테스트"})
    print(f"[POST /api/v1/agent/ask] {code}\n{json.dumps(body, ensure_ascii=False, indent=2) if isinstance(body, dict) else body}")
    print("PASS: ask OK" if code == 200 else "FAIL: ask 실패")
    return 0 if code == 200 else 1


if __name__ == "__main__":
    sys.exit(main())