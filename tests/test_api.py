from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_rejects_short_script():
    response = client.post("/api/v1/jobs", json={"script": "tiny"})
    assert response.status_code == 422


def test_rejects_bad_aspect_ratio():
    response = client.post("/api/v1/jobs", json={
        "script": "This is a sufficiently long test script.",
        "aspect_ratio": "4:3",
    })
    assert response.status_code == 422


def test_job_creation_and_idempotency():
    headers = {"Idempotency-Key": "test-key-stage-one"}
    payload = {
        "script": "A small team works together to build a useful new product.",
        "aspect_ratio": "16:9",
        "style": "documentary",
    }
    first = client.post("/api/v1/jobs", json=payload, headers=headers)
    second = client.post("/api/v1/jobs", json=payload, headers=headers)
    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["job"]["job_id"] == second.json()["job"]["job_id"]
    assert second.json()["idempotent_replay"] is True


def test_capabilities_explains_stage():
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert "Footage Diversity Guard" in body["planned"]
    assert "silence and emphasis detection" in body["planned"]
