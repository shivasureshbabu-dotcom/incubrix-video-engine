
from __future__ import annotations

from fastapi.responses import FileResponse, JSONResponse
from app.video_pipeline import run_video_pipeline
import json
import os
import threading
import tempfile
import uuid
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Header, HTTPException, UploadFile, File
from app.audio_analyzer import (
    analyze_audio,
    detect_emphasis,
    create_scene_timing,
)
from pydantic import BaseModel, Field, field_validator

APP_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", APP_ROOT / "data"))
JOBS_DIR = DATA_DIR / "jobs"
OUTPUTS_DIR = DATA_DIR / "outputs"
UPLOADS_DIR = DATA_DIR / "uploads"

for directory in (JOBS_DIR, OUTPUTS_DIR, UPLOADS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="IncuBrix Script-to-B-Roll Engine",
    version="0.1.0",
    description=(
        "Stage 1 backend foundation. Audio analysis, footage ranking, "
        "and rendering come in later stages."
    ),
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://incubrix-video-engine.vercel.app",
    ],
    allow_origin_regex=r"https://[a-zA-Z0-9-]+\.vercel\.app",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_idempotency_lock = threading.Lock()
_idempotency: dict[str, str] = {}


class CreateJobRequest(BaseModel):
    script: str = Field(min_length=10, max_length=12000)
    aspect_ratio: str = "16:9"
    style: str = Field(default="documentary", max_length=80)

    @field_validator("script")
    @classmethod
    def script_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("script must not be blank")
        return value.strip()

    @field_validator("aspect_ratio")
    @classmethod
    def valid_aspect_ratio(cls, value: str) -> str:
        if value not in {"16:9", "9:16", "1:1"}:
            raise ValueError("aspect_ratio must be 16:9, 9:16, or 1:1")
        return value


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def job_path(job_id: str) -> Path:
    return JOBS_DIR / f"{job_id}.json"


def read_job(job_id: str) -> dict[str, Any] | None:
    path = job_path(job_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_job(job: dict[str, Any]) -> None:
    path = job_path(job["job_id"])
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(job, indent=2), encoding="utf-8")
    temporary.replace(path)


def run_demo_job(job_id: str) -> None:
    """Run video generation and complete only when a valid MP4 exists."""
    job = read_job(job_id)
    if job is None:
        return

    try:
        job.update(
            status="processing",
            progress=5,
            message="Starting video generation",
            updated_at=now_iso(),
        )
        write_job(job)

        payload = job.get("input", {})

        def update_progress(percent: int, message: str) -> None:
            current = read_job(job_id)
            if current is None:
                return

            current.update(
                status="processing",
                progress=min(99, max(0, percent)),
                message=message,
                updated_at=now_iso(),
            )
            write_job(current)

        result = run_video_pipeline(
            script=payload["script"],
            aspect_ratio=payload.get("aspect_ratio", "16:9"),
            job_id=job_id,
            output_dir=OUTPUTS_DIR,
            progress_callback=update_progress,
        )

        video_path = Path(result["video_path"]).resolve()
        output_root = OUTPUTS_DIR.resolve()

        if (
            not video_path.is_relative_to(output_root)
            or video_path.suffix.lower() != ".mp4"
            or not video_path.is_file()
            or video_path.stat().st_size == 0
        ):
            raise RuntimeError(
                "Video generation did not produce a valid MP4"
            )

        validation = result.get("validation")
        if not isinstance(validation, dict) or validation.get("valid") is not True:
            raise RuntimeError("Generated video failed validation")

        job = read_job(job_id)
        if job is None:
            return

        job.update(
            status="completed",
            progress=100,
            message="Video generated successfully",
            result={
                "video_filename": video_path.name,
                "video_url": f"/api/v1/jobs/{job_id}/video",
                "scene_count": result.get("scene_count"),
                "validation": validation,
            },
            error=None,
            updated_at=now_iso(),
        )
        write_job(job)

    except Exception as exc:
        job = read_job(job_id)
        if job is None:
            return

        job.update(
            status="failed",
            progress=0,
            message="Video generation failed",
            error=str(exc),
            result=None,
            updated_at=now_iso(),
        )
        write_job(job)


@app.get("/")
def root():
    return {
        "name": "IncuBrix Script-to-B-Roll Engine",
        "version": "0.1.0",
        "stage": 1,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": now_iso()}


@app.get("/ready")
def ready():
    checks = {
        "job_storage": JOBS_DIR.exists() and JOBS_DIR.is_dir(),
        "output_storage": OUTPUTS_DIR.exists() and OUTPUTS_DIR.is_dir(),
    }
    return JSONResponse(
        status_code=200 if all(checks.values()) else 503,
        content={"ready": all(checks.values()), "checks": checks},
    )


@app.post("/api/v1/jobs", status_code=202)
def create_job(
    payload: CreateJobRequest,
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
    ),
):
    if idempotency_key is not None:
        if not idempotency_key.strip() or len(idempotency_key) > 200:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_IDEMPOTENCY_KEY",
                    "message": (
                        "Idempotency-Key must be non-empty and "
                        "200 characters or fewer."
                    ),
                },
            )

    with _idempotency_lock:
        if idempotency_key is not None:
            old_id = _idempotency.get(idempotency_key)
            old_job = read_job(old_id) if old_id else None

            if old_job is not None:
                return {"job": old_job, "idempotent_replay": True}

        job_id = str(uuid.uuid4())
        job = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "message": "Job queued for video generation.",
            "input": payload.model_dump(),
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "result": None,
            "error": None,
        }

        write_job(job)

        if idempotency_key is not None:
            _idempotency[idempotency_key] = job_id

    threading.Thread(
        target=run_demo_job,
        args=(job["job_id"],),
        daemon=True,
    ).start()

    return {"job": job, "idempotent_replay": False}


@app.get("/api/v1/jobs/{job_id}")
def get_job(job_id: str):
    job = read_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "JOB_NOT_FOUND",
                "message": f"No job found with id {job_id}.",
            },
        )
    return {"job": job}


@app.get("/api/v1/jobs/{job_id}/video")
def download_generated_video(job_id: str):
    job = read_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "JOB_NOT_FOUND", "message": "Job not found."},
        )

    if job.get("status") != "completed":
        raise HTTPException(
            status_code=409,
            detail={
                "code": "VIDEO_NOT_READY",
                "message": "The video is not ready for download.",
            },
        )

    filename = (job.get("result") or {}).get("video_filename")
    if not filename or Path(filename).name != filename:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "VIDEO_NOT_FOUND",
                "message": "Video not found.",
            },
        )

    output_root = OUTPUTS_DIR.resolve()
    video_path = (output_root / filename).resolve()

    if (
        not video_path.is_relative_to(output_root)
        or video_path.suffix.lower() != ".mp4"
        or not video_path.is_file()
    ):
        raise HTTPException(
            status_code=404,
            detail={
                "code": "VIDEO_NOT_FOUND",
                "message": "Video file not found.",
            },
        )

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=video_path.name,
    )


@app.get("/api/v1/jobs")
def list_jobs(limit: int = 20):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_LIMIT",
                "message": "limit must be between 1 and 100.",
            },
        )

    jobs = []
    for path in JOBS_DIR.glob("*.json"):
        try:
            jobs.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue

    jobs.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True,
    )
    return {"jobs": jobs[:limit], "count": min(len(jobs), limit)}


@app.get("/api/v1/capabilities")
def capabilities():
    return {
        "stage": 1,
        "implemented": [
            "script input validation",
            "background demo jobs",
            "job status and progress",
            "Idempotency-Key support",
            "health and readiness endpoints",
            "persistent JSON job records",
        ],
        "planned": [
            "voiceover upload and transcription",
            "silence and emphasis detection",
            "semantic footage retrieval",
            "Footage Diversity Guard",
            "caption and scene timing",
            "FFmpeg rendering",
            "licensing manifest and output validation",
        ],
    }


@app.post("/api/v1/audio/analyze")
def analyze_uploaded_audio(file: UploadFile = File(...)):
    if not file.filename or Path(file.filename).suffix.lower() != ".wav":
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_AUDIO_FORMAT",
                "message": "Please upload a WAV audio file.",
            },
        )

    upload_path = UPLOADS_DIR / f"{uuid.uuid4()}.wav"

    try:
        size = 0
        max_size = 50 * 1024 * 1024

        with upload_path.open("wb") as destination:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break

                size += len(chunk)
                if size > max_size:
                    raise HTTPException(
                        status_code=413,
                        detail={
                            "code": "AUDIO_TOO_LARGE",
                            "message": "Audio file must be 50 MB or smaller.",
                        },
                    )

                destination.write(chunk)

        result = analyze_audio(str(upload_path))
        return {"status": "success", "analysis": result}

    except (ValueError, wave.Error) as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_AUDIO_FILE",
                "message": str(exc),
            },
        ) from exc

    finally:
        upload_path.unlink(missing_ok=True)
        file.file.close()


@app.post("/api/v1/audio/emphasis")
def analyze_audio_emphasis(file: UploadFile = File(...)):
    if not file.filename or Path(file.filename).suffix.lower() != ".wav":
        raise HTTPException(
            status_code=400,
            detail="Please upload a WAV audio file.",
        )

    upload_path = UPLOADS_DIR / f"{uuid.uuid4()}.wav"

    try:
        size = 0
        max_size = 50 * 1024 * 1024

        with upload_path.open("wb") as destination:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break

                size += len(chunk)
                if size > 50 * 1024 * 1024:
                    raise HTTPException(
                        status_code=413,
                        detail="File is too large. Maximum size is 50 MB.",
                    )

                destination.write(chunk)

        result = detect_emphasis(str(upload_path))
        return {"status": "success", "analysis": result}

    except (ValueError, wave.Error) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        upload_path.unlink(missing_ok=True)
        file.file.close()


class SceneTimingRequest(BaseModel):
    duration_seconds: float = Field(gt=0)
    silence_intervals: list[dict] = Field(default_factory=list)
    emphasis_intervals: list[dict] = Field(default_factory=list)


@app.post("/api/v1/audio/scenes")
def create_audio_scenes(request: SceneTimingRequest):
    try:
        result = create_scene_timing(
            duration_seconds=request.duration_seconds,
            silence_intervals=request.silence_intervals,
            emphasis_intervals=request.emphasis_intervals,
        )
        return {"status": "success", "analysis": result}

    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/audio/analyze-and-scenes")
async def analyze_audio_and_create_scenes(file: UploadFile = File(...)):
    """Analyze WAV audio and automatically create scene timings."""

    if not file.filename or not file.filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=400,
            detail="Only WAV files are supported.",
        )

    contents = await file.read()

    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 50 MB limit.",
        )

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    saved_path = None

    try:
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            dir=UPLOADS_DIR,
            delete=False,
        ) as temp_file:
            temp_file.write(contents)
            saved_path = Path(temp_file.name)

        audio_analysis = analyze_audio(str(saved_path))
        emphasis_analysis = detect_emphasis(str(saved_path))

        scene_analysis = create_scene_timing(
            duration_seconds=audio_analysis["duration_seconds"],
            silence_intervals=audio_analysis["silence_intervals"],
            emphasis_intervals=emphasis_analysis["emphasis_intervals"],
        )

        return {
            "status": "success",
            "audio_analysis": audio_analysis,
            "emphasis_analysis": emphasis_analysis,
            "scene_analysis": scene_analysis,
        }

    except (ValueError, wave.Error) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        if saved_path is not None:
            saved_path.unlink(missing_ok=True)
