
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from gtts import gTTS

from app.pixabay_client import search_pixabay_videos
from app.video_downloader import download_video
from app.video_renderer import render_video
from app.audio_video_merger import merge_audio_with_video
from app.caption_renderer import burn_captions
from app.video_validation import validate_video


STOP_WORDS = {
    "the", "and", "for", "that", "this", "with", "from", "are",
    "was", "were", "will", "would", "could", "should", "have",
    "has", "had", "you", "your", "they", "them", "their", "our",
    "but", "not", "into", "about", "when", "what", "why", "how",
    "its", "it's", "is", "of", "to", "in", "on", "at", "as",
    "by", "an", "a", "be", "or", "we", "it", "he", "she",
    "his", "her", "who", "which", "while", "than", "then",
    "there", "here", "all", "can", "just", "more", "most",
}


def split_script(script: str) -> list[str]:
    """Split a script into sentence-sized footage search segments."""
    sentences = re.split(r"(?<=[.!?])\s+", script.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def make_search_query(sentence: str) -> str:
    """Create a Pixabay search query from meaningful sentence words."""
    words = re.findall(r"[a-z][a-z'-]{2,}", sentence.lower())
    useful = [word for word in words if word not in STOP_WORDS]
    return " ".join(useful[:5]) or "nature landscape"


def score_footage_match(sentence: str, clip: dict) -> int:
    """Rank a Pixabay clip by overlap between sentence words and its tags."""
    sentence_words = set(
        re.findall(r"[a-z][a-z'-]{2,}", sentence.lower())
    )
    sentence_words -= STOP_WORDS

    tag_words = set(
        re.findall(r"[a-z][a-z'-]{2,}", str(clip.get("tags", "")).lower())
    )
    tag_words -= STOP_WORDS

    score = len(sentence_words & tag_words) * 10

    # A valid HTTPS URL is required, and gets a small tie-breaking bonus.
    if str(clip.get("download_url", "")).startswith("https://"):
        score += 2

    return score


def select_best_footage(
    sentence: str,
    results: list[dict],
) -> dict | None:
    """Choose the best-ranked result with a downloadable HTTPS URL."""
    usable = [
        clip for clip in results
        if str(clip.get("download_url", "")).startswith("https://")
    ]

    if not usable:
        return None

    # max() keeps the first result if multiple clips have equal scores.
    return max(
        usable,
        key=lambda clip: score_footage_match(sentence, clip),
    )


def write_srt(
    script: str,
    duration_seconds: float,
    output_path: Path,
) -> None:
    """Create approximate sentence captions across narration duration."""
    sentences = split_script(script)

    if not sentences:
        raise ValueError("The script has no captionable sentences")

    if duration_seconds <= 0:
        raise ValueError("Caption duration must be greater than zero")

    total_words = sum(
        max(1, len(sentence.split())) for sentence in sentences
    )
    cursor = 0.0
    entries = []

    def timestamp(seconds: float) -> str:
        milliseconds = max(0, int(round(seconds * 1000)))
        hours, remainder = divmod(milliseconds, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        seconds_part, milliseconds_part = divmod(remainder, 1000)

        return (
            f"{hours:02}:{minutes:02}:"
            f"{seconds_part:02},{milliseconds_part:03}"
        )

    for index, sentence in enumerate(sentences, start=1):
        weight = max(1, len(sentence.split())) / total_words

        if index == len(sentences):
            end = duration_seconds
        else:
            end = cursor + duration_seconds * weight

        end = min(max(end, cursor), duration_seconds)

        entries.append(
            f"{index}\n"
            f"{timestamp(cursor)} --> {timestamp(end)}\n"
            f"{sentence}\n"
        )
        cursor = end

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(entries), encoding="utf-8")


def get_audio_duration(audio_path: Path) -> float:
    """Read narration duration using FFprobe."""
    ffprobe_path = os.getenv("FFPROBE_PATH", "ffprobe")

    result = subprocess.run(
        [
            ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )

    try:
        duration = float(result.stdout.strip())
    except ValueError as error:
        raise RuntimeError(
            "FFprobe returned an invalid audio duration"
        ) from error

    if duration <= 0:
        raise RuntimeError("Generated narration has an invalid duration")

    return duration


def run_video_pipeline(
    script: str,
    aspect_ratio: str,
    job_id: str,
    output_dir: str | Path,
    progress_callback=None,
) -> dict:
    """
    Generate narration, select and render Pixabay footage, add captions,
    and validate the final MP4.
    """
    if not script or not script.strip():
        raise ValueError("Script cannot be empty")

    output_root = Path(output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    work_dir = output_root / f"work_{job_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    def progress(percent: int, message: str) -> None:
        if progress_callback:
            progress_callback(percent, message)

    format_map = {
        "16:9": "landscape",
        "9:16": "portrait",
        "1:1": "square",
    }

    if aspect_ratio not in format_map:
        raise ValueError(
            "Unsupported aspect ratio. Use 16:9, 9:16, or 1:1."
        )

    sentences = split_script(script)

    if not sentences:
        raise ValueError("Script contains no usable sentences")

    # 1. Generate narration.
    progress(10, "Generating narration")

    audio_path = work_dir / "narration.mp3"
    gTTS(text=script.strip(), lang="en").save(str(audio_path))

    if not audio_path.is_file() or audio_path.stat().st_size == 0:
        raise RuntimeError(
            "Narration generation did not produce an audio file"
        )

    # 2. Search Pixabay and rank footage for each scene.
    progress(20, "Searching and matching Pixabay footage")

    clip_paths = []

    for index, sentence in enumerate(sentences, start=1):
        query = make_search_query(sentence)
        progress(
            min(20 + index * 5, 55),
            f"Finding footage for scene {index} of {len(sentences)}",
        )

        results = search_pixabay_videos(query, per_page=10)
        clip = select_best_footage(sentence, results)

        if clip is None:
            raise RuntimeError(
                f"Pixabay returned no downloadable footage for scene {index}"
            )

        source_path = download_video(
            clip["download_url"],
            output_dir=str(work_dir / "downloads"),
        )

        normalized_path = work_dir / f"scene_{index:03}.mp4"

        render_video(
            source_path,
            str(normalized_path),
            format_name=format_map[aspect_ratio],
        )

        if (
            not normalized_path.is_file()
            or normalized_path.stat().st_size == 0
        ):
            raise RuntimeError(
                f"Rendering did not produce footage for scene {index}"
            )

        clip_paths.append(normalized_path)

    # 3. Combine normalized footage into one silent video.
    progress(65, "Combining selected footage")

    concat_file = work_dir / "concat.txt"

    concat_file.write_text(
        "".join(
            f"file '{path.resolve().as_posix()}'\n"
            for path in clip_paths
        ),
        encoding="utf-8",
    )

    combined_path = work_dir / "combined.mp4"
    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")

    subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-an",
            "-movflags", "+faststart",
            str(combined_path),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=600,
    )

    if not combined_path.is_file() or combined_path.stat().st_size == 0:
        raise RuntimeError("Combining footage did not produce a video")

    # 4. Add narration.
    progress(75, "Adding narration")

    narrated_path = work_dir / "narrated.mp4"

    merge_audio_with_video(
        str(combined_path),
        str(audio_path),
        str(narrated_path),
    )

    # 5. Generate and burn captions.
    progress(85, "Adding captions")

    duration = get_audio_duration(audio_path)
    subtitles_path = work_dir / "captions.srt"

    write_srt(
        script,
        duration,
        subtitles_path,
    )

    final_path = output_root / f"{job_id}.mp4"

    burn_captions(
        str(narrated_path),
        str(subtitles_path),
        str(final_path),
    )

    # 6. Validate the final MP4.
    progress(95, "Validating final video")

    if not final_path.is_file() or final_path.stat().st_size == 0:
        raise RuntimeError("Final MP4 was not created")

    validation = validate_video(str(final_path))

    if not validation.get("valid"):
        raise RuntimeError("Final video did not pass validation")

    progress(100, "Video generated successfully")

    return {
        "video_path": str(final_path),
        "video_filename": final_path.name,
        "validation": validation,
        "scene_count": len(clip_paths),
        "narration_path": str(audio_path),
    }
