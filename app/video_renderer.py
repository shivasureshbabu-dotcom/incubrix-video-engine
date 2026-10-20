
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from app.video_format import get_target_dimensions


def render_video(
    input_path: str,
    output_path: str,
    format_name: str = "landscape",
) -> str:
    """Resize and encode a video using low-memory FFmpeg settings."""

    source = Path(input_path).resolve()
    destination = Path(output_path).resolve()

    if not source.is_file():
        raise ValueError("Input video file does not exist")

    if source == destination:
        raise ValueError("Input and output paths must be different")

    target = get_target_dimensions(format_name)

    # Preserve the requested aspect ratio, but cap the output canvas
    # to dimensions suitable for a low-memory demo.
    max_dimensions = {
        "landscape": (854, 480),
        "portrait": (480, 854),
        "square": (480, 480),
    }

    if format_name not in max_dimensions:
        raise ValueError(
            "Unsupported video format. Use landscape, portrait, or square."
        )

    max_width, max_height = max_dimensions[format_name]

    try:
        target_width = int(target["width"])
        target_height = int(target["height"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Invalid target video dimensions") from error

    # Do not upscale beyond the low-memory target canvas.
    width = min(target_width, max_width)
    height = min(target_height, max_height)

    # H.264 yuv420p requires even dimensions.
    width -= width % 2
    height -= height % 2

    if width < 2 or height < 2:
        raise ValueError("Target dimensions must be at least 2x2")

    destination.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")

    video_filter = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        "fps=24"
    )

    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel", "error",
        "-nostdin",
        "-y",
        "-threads", "1",
        "-i", str(source),
        "-map", "0:v:0",
        "-vf", video_filter,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-threads", "1",
        "-crf", "30",
        "-pix_fmt", "yuv420p",
        "-an",
        "-movflags", "+faststart",
        str(destination),
    ]

    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True,
            timeout=180,
        )

    except FileNotFoundError as error:
        destination.unlink(missing_ok=True)
        raise RuntimeError(
            "FFmpeg was not found. Check the FFMPEG_PATH environment variable."
        ) from error

    except subprocess.CalledProcessError as error:
        destination.unlink(missing_ok=True)

        details = error.stderr
        if isinstance(details, bytes):
            details = details.decode("utf-8", errors="replace")

        details = (details or "")[-1200:]

        raise RuntimeError(
            "FFmpeg rendering failed: "
            f"{details or 'No error details available'}"
        ) from error

    except subprocess.TimeoutExpired as error:
        destination.unlink(missing_ok=True)
        raise RuntimeError("Video rendering timed out") from error

    if not destination.is_file() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise RuntimeError(
            "FFmpeg did not produce a valid output file"
        )

    return str(destination)
