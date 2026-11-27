"""GPU / DB 준비 확인."""


def check_gpu() -> dict:
    try:
        import torch
    except Exception as exc:
        return {"name": "gpu", "ok": False, "detail": f"torch 불러오기 실패: {type(exc).__name__}: {exc}"}
    if not torch.cuda.is_available():
        return {"name": "gpu", "ok": False,
                "detail": f"CUDA 사용 불가 (torch {torch.__version__}, CUDA 빌드: {torch.version.cuda})"}
    return {"name": "gpu", "ok": True,
            "detail": f"{torch.cuda.get_device_name(0)} (torch {torch.__version__}, CUDA {torch.version.cuda})"}


def check_db() -> dict:
    from app.db import repository

    try:
        ok = repository.ping() and repository.has_pgvector()
        return {"name": "db", "ok": ok, "detail": "연결 및 pgvector 정상" if ok else "pgvector 확장 없음"}
    except Exception as exc:
        return {"name": "db", "ok": False, "detail": f"{type(exc).__name__}: {exc}"}


def run_all() -> list[dict]:
    return [check_gpu(), check_db()]