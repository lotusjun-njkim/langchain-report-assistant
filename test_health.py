from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root():
    assert client.get("/").status_code == 200


def test_ask_stub():
    r = client.post("/api/v1/agent/ask", json={"question": "안녕"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "stub"
    assert "안녕" in body["answer"]


def test_ask_empty_question_rejected():
    r = client.post("/api/v1/agent/ask", json={"question": ""})
    assert r.status_code == 422
