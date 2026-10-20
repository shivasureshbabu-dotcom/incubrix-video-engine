
from __future__ import annotations

import os
import subprocess
from pathlib import Path


OUTPUT_WIDTH = 854
OUTPUT_HEIGHT = 480
OUTPUT_FPS = 24


def burn_captions(
    video_path: str,
    subtitle_path: str,
    output_path: str,
) -> str:
    """Burn captions into a compressed, low-memory H.264 MP4."""

    video = Path(video_path).resolve()
    subtitles = Path(subtitle_path).resolve()
    output = Path(output_path).resolve()

    if not video.is_file():
        raise ValueError("Video file does not exist")

    if not subtitles.is_file():
        raise ValueError("Subtitle file does not exist")

    if output in {video, subtitles}:
        raise ValueError("Output path must differ from input paths")

    if output.suffix.lower() != ".mp4":
        raise ValueError("Output file must use the .mp4 extension")

    output.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")

    # Escape the subtitle path for FFmpeg's subtitles filter.
    subtitle_filter_path = (
        str(subtitles)
        .replace("\\", "/")
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace(",", r"\,")
        .replace("[", r"\[")
        .replace("]", r"\]")
    )

    # Fit the source into a 480p canvas without stretching it.
    # Portrait and square videos remain centered on a suitable canvas.
    filter_complex = (
        f"scale={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:"
        "force_original_aspect_ratio=decrease,"
        f"pad={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={OUTPUT_FPS},"
        f"subtitles='{subtitle_filter_path}':"
        "force_style='FontSize=20,Outline=2,Shadow=1,Alignment=2'"
    )

    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel", "error",
        "-nostdin",
        "-y",
        "-threads", "1",
        "-i", str(video),
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-threads", "1",
        "-crf", "30",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "96k",
        "-movflags", "+faststart",
        str(output),
    ]

    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True,
            timeout=300,
        )

    except FileNotFoundError as error:
        output.unlink(missing_ok=True)
        raise RuntimeError(
            "FFmpeg was not found. Check FFMPEG_PATH."
        ) from error

    except subprocess.CalledProcessError as error:
        output.unlink(missing_ok=True)

        details = error.stderr
        if isinstance(details, bytes):
            details = details.decode("utf-8", errors="replace")

        details = (details or "")[-1200:]

        raise RuntimeError(
            "Caption rendering failed: "
            f"{details or 'FFmpeg returned an error'}"
        ) from error

    except subprocess.TimeoutExpired as error:
        output.unlink(missing_ok=True)
        raise RuntimeError(
            "Caption rendering timed out"
        ) from error

    if not output.is_file() or output.stat().st_size == 0:
        output.unlink(missing_ok=True)
        raise RuntimeError(
            "FFmpeg did not produce a valid output file"
        )

    return str(output)
