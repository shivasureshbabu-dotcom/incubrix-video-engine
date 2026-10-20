from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app import main as main_module
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
    response = client.post(
        "/api/v1/jobs",
        json={"script": "tiny"},
    )

    assert response.status_code == 422


def test_rejects_bad_aspect_ratio():
    response = client.post(
        "/api/v1/jobs",
        json={
            "script": "This is a sufficiently long test script.",
            "aspect_ratio": "4:3",
        },
    )

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


def test_video_download_unknown_job(monkeypatch):
    monkeypatch.setattr(main_module, "read_job", lambda job_id: None)

    response = client.get("/api/v1/jobs/unknown-job/video")

    assert response.status_code == 404


def test_video_download_processing_job(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "read_job",
        lambda job_id: {
            "job_id": job_id,
            "status": "processing",
        },
    )

    response = client.get("/api/v1/jobs/processing-job/video")

    assert response.status_code == 409


def test_video_download_completed_job(monkeypatch, tmp_path):
    video_path = tmp_path / "sample.mp4"
    video_bytes = b"test-video-content"
    video_path.write_bytes(video_bytes)

    monkeypatch.setattr(main_module, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(
        main_module,
        "read_job",
        lambda job_id: {
            "job_id": job_id,
            "status": "completed",
            "result": {"video_filename": "sample.mp4"},
        },
    )

    response = client.get("/api/v1/jobs/completed-job/video")

    assert response.status_code == 200
    assert response.headers["content-type"] == "video/mp4"
    assert response.content == video_bytes


def test_video_download_rejects_unsafe_filename(monkeypatch, tmp_path):
    monkeypatch.setattr(main_module, "OUTPUTS_DIR", tmp_path)
    monkeypatch.setattr(
        main_module,
        "read_job",
        lambda job_id: {
            "job_id": job_id,
            "status": "completed",
            "result": {"video_filename": "../outside.mp4"},
        },
    )

    response = client.get("/api/v1/jobs/completed-job/video")

    assert response.status_code == 404


def test_get_job_returns_job_details(monkeypatch):
    expected_job = {
        "job_id": "test-job-123",
        "status": "processing",
        "progress": 50,
        "message": "Combining selected footage",
        "result": None,
        "error": None,
    }

    monkeypatch.setattr(
        main_module,
        "read_job",
        lambda job_id: expected_job if job_id == "test-job-123" else None,
    )

    response = client.get("/api/v1/jobs/test-job-123")

    assert response.status_code == 200
    assert response.json()["job"] == expected_job


def test_get_unknown_job_returns_404(monkeypatch):
    monkeypatch.setattr(main_module, "read_job", lambda job_id: None)

    response = client.get("/api/v1/jobs/does-not-exist")

    assert response.status_code == 404
    body = response.json()["detail"]
    assert body["code"] == "JOB_NOT_FOUND"


def test_rejects_idempotency_key_over_200_characters():
    headers = {"Idempotency-Key": "k" * 201}
    payload = {
        "script": "A small team works together to build a useful new product.",
        "aspect_ratio": "16:9",
        "style": "documentary",
    }

    response = client.post("/api/v1/jobs", json=payload, headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_IDEMPOTENCY_KEY"


def test_rejects_blank_idempotency_key():
    headers = {"Idempotency-Key": "   "}
    payload = {
        "script": "A small team works together to build a useful new product.",
        "aspect_ratio": "16:9",
        "style": "documentary",
    }

    response = client.post("/api/v1/jobs", json=payload, headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_IDEMPOTENCY_KEY"


def test_concurrent_requests_with_same_idempotency_key(monkeypatch):
    created_jobs = {}
    created_jobs_lock = Lock()
    thread_start_count = {"value": 0}

    def fake_read_job(job_id):
        with created_jobs_lock:
            job = created_jobs.get(job_id)
            return job.copy() if job is not None else None

    def fake_write_job(job):
        with created_jobs_lock:
            created_jobs[job["job_id"]] = job.copy()

    class FakeThread:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            thread_start_count["value"] += 1

    monkeypatch.setattr(main_module, "read_job", fake_read_job)
    monkeypatch.setattr(main_module, "write_job", fake_write_job)

    # Replace the backend's threading reference only.
    # Do not modify threading.Thread globally, because
    # ThreadPoolExecutor needs real threads to run this test.
    monkeypatch.setattr(
        main_module,
        "threading",
        SimpleNamespace(Thread=FakeThread),
    )

    key = "concurrency-test-key"
    payload = {
        "script": "A small team works together to build a useful new product.",
        "aspect_ratio": "16:9",
        "style": "documentary",
    }

    def submit_job():
        return client.post(
            "/api/v1/jobs",
            json=payload,
            headers={"Idempotency-Key": key},
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: submit_job(), range(2)))

    assert all(response.status_code == 202 for response in responses)

    job_ids = [
        response.json()["job"]["job_id"]
        for response in responses
    ]

    assert job_ids[0] == job_ids[1]

    assert sum(
        response.json()["idempotent_replay"] is False
        for response in responses
    ) == 1

    assert thread_start_count["value"] == 1