
import os
import subprocess
from pathlib import Path


def burn_captions(
    video_path: str,
    subtitle_path: str,
    output_path: str,
) -> str:
    """Burn an SRT subtitle file into a video using FFmpeg."""

    video = Path(video_path)
    subtitles = Path(subtitle_path)
    output = Path(output_path)

    if not video.is_file():
        raise ValueError("Video file does not exist")

    if not subtitles.is_file():
        raise ValueError("Subtitle file does not exist")

    if output.resolve() in {video.resolve(), subtitles.resolve()}:
        raise ValueError("Output path must differ from input paths")

    if output.suffix.lower() != ".mp4":
        raise ValueError("Output file must use the .mp4 extension")

    output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")

    # Escape the subtitle path for FFmpeg's subtitles filter on Windows.
    subtitle_filter_path = (
        str(subtitles.resolve())
        .replace("\\", "/")
        .replace(":", r"\:")
        .replace("'", r"\'")
    )

    command = [
        ffmpeg_path,
        "-y",
        "-i", str(video),
        "-vf",
        f"subtitles='{subtitle_filter_path}':"
        "force_style='FontSize=22,Outline=2,Shadow=1,Alignment=2'",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output),
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
        output.unlink(missing_ok=True)
        raise RuntimeError(
            "FFmpeg was not found. Check FFMPEG_PATH."
        ) from error
    except subprocess.CalledProcessError as error:
        output.unlink(missing_ok=True)
        raise RuntimeError(
            f"Caption rendering failed: {error.stderr[-1000:]}"
        ) from error
    except subprocess.TimeoutExpired as error:
        output.unlink(missing_ok=True)
        raise RuntimeError("Caption rendering timed out") from error

    if not output.is_file() or output.stat().st_size == 0:
        output.unlink(missing_ok=True)
        raise RuntimeError("FFmpeg did not produce a valid output file")

    return str(output)
