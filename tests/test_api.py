from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "tabular-automl-studio"


def test_list_and_action():
    r = client.get("/api/runs")
    assert r.status_code == 200
    assert "runs" in r.json()

    r2 = client.post("/api/train_baseline", json={"prompt": "smoke test"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["ok"] is True
    assert "result" in body
