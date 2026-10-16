
import json
import os
import subprocess
from pathlib import Path


def inspect_video(file_path: str) -> dict:
    """Inspect a video using FFprobe."""

    video_path = Path(file_path)

    if not video_path.is_file():
        raise ValueError("Video file does not exist")

    if video_path.stat().st_size == 0:
        raise ValueError("Video file is empty")

    ffprobe_path = os.getenv("FFPROBE_PATH", "ffprobe")

    command = [
        ffprobe_path,
        "-v", "error",
        "-show_entries",
        "format=duration:stream=codec_type,width,height",
        "-of", "json",
        str(video_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        data = json.loads(result.stdout)

    except FileNotFoundError as error:
        raise RuntimeError(
            "FFprobe was not found. Set the FFPROBE_PATH environment variable."
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError("FFprobe could not inspect the video") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Video inspection timed out") from error
    except json.JSONDecodeError as error:
        raise RuntimeError("FFprobe returned invalid JSON") from error

    streams = data.get("streams", [])

    video_stream = next(
        (
            stream for stream in streams
            if stream.get("codec_type") == "video"
        ),
        None,
    )

    audio_stream = next(
        (
            stream for stream in streams
            if stream.get("codec_type") == "audio"
        ),
        None,
    )

    if video_stream is None:
        raise ValueError("No video stream found")

    try:
        duration = float(data["format"]["duration"])
        width = int(video_stream["width"])
        height = int(video_stream["height"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Video metadata is incomplete or invalid") from error

    if duration <= 0 or width <= 0 or height <= 0:
        raise ValueError("Video duration and dimensions must be positive")

    return {
        "file_path": str(video_path),
        "duration_seconds": round(duration, 3),
        "width": width,
        "height": height,
        "size_bytes": video_path.stat().st_size,
        "has_audio": audio_stream is not None,
    }
