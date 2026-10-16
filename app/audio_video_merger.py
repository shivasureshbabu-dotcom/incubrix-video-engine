
import os
import subprocess
from pathlib import Path


def merge_audio_with_video(
    video_path: str,
    audio_path: str,
    output_path: str,
) -> str:
    """Merge a video and narration, preserving the full audio."""

    video = Path(video_path)
    audio = Path(audio_path)
    output = Path(output_path)

    if not video.is_file():
        raise ValueError("Video file does not exist")

    if not audio.is_file():
        raise ValueError("Audio file does not exist")

    if output.resolve() in {video.resolve(), audio.resolve()}:
        raise ValueError("Output path must differ from input paths")

    output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")

    command = [
        ffmpeg_path,
        "-y",
        "-i", str(video),
        "-i", str(audio),
        "-filter_complex",
        "[0:v]tpad=stop_mode=clone:stop_duration=3[v]",
        "-map", "[v]",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
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
            f"Audio-video merging failed: {error.stderr[-1000:]}"
        ) from error
    except subprocess.TimeoutExpired as error:
        output.unlink(missing_ok=True)
        raise RuntimeError("Audio-video merging timed out") from error

    if not output.is_file() or output.stat().st_size == 0:
        output.unlink(missing_ok=True)
        raise RuntimeError("FFmpeg did not produce a valid output file")

    return str(output)
