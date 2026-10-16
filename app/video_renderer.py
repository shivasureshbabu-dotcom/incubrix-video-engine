
import os
import subprocess
from pathlib import Path

from app.video_format import get_target_dimensions


def render_video(
    input_path: str,
    output_path: str,
    format_name: str = "landscape",
) -> str:
    """Resize and render a video to a standard MP4 format."""

    source = Path(input_path)
    destination = Path(output_path)

    if not source.is_file():
        raise ValueError("Input video file does not exist")

    if source.resolve() == destination.resolve():
        raise ValueError("Input and output paths must be different")

    target = get_target_dimensions(format_name)

    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")

    destination.parent.mkdir(parents=True, exist_ok=True)

    command = [
        ffmpeg_path,
        "-y",
        "-i", str(source),
        "-vf",
        (
            f"scale={target['width']}:{target['height']}:"
            "force_original_aspect_ratio=increase,"
            f"crop={target['width']}:{target['height']}"
        ),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-an",
        "-movflags", "+faststart",
        str(destination),
    ]

    try:
        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=300,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "FFmpeg was not found. Set the FFMPEG_PATH environment variable."
        ) from error
    except subprocess.CalledProcessError as error:
        destination.unlink(missing_ok=True)
        raise RuntimeError(
            f"FFmpeg rendering failed: {error.stderr[-1000:]}"
        ) from error
    except subprocess.TimeoutExpired as error:
        destination.unlink(missing_ok=True)
        raise RuntimeError("Video rendering timed out") from error

    if not destination.is_file() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise RuntimeError("FFmpeg did not produce a valid output file")

    return str(destination)
