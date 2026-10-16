
from pathlib import Path
from urllib.parse import urlparse

import requests

MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB


def download_video(
    video_url: str,
    output_dir: str = "data/videos",
) -> str:
    """Download an MP4 from Pixabay with a size limit."""

    parsed = urlparse(video_url)

    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Video URL must be a valid HTTPS URL")

    if parsed.hostname != "cdn.pixabay.com":
        raise ValueError("Video URL must use the Pixabay video CDN")

    if not parsed.path.lower().endswith(".mp4"):
        raise ValueError("Video URL must point to an MP4 file")

    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)

    output_path = folder / Path(parsed.path).name

    try:
        with requests.get(
            video_url,
            stream=True,
            timeout=(10, 60),
        ) as response:
            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            if (
                "video/" not in content_type
                and "octet-stream" not in content_type
            ):
                raise ValueError(
                    "The URL did not return video content"
                )

            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_VIDEO_SIZE:
                raise ValueError("Video exceeds the 100 MB size limit")

            total_size = 0

            with output_path.open("wb") as video_file:
                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if not chunk:
                        continue

                    total_size += len(chunk)

                    if total_size > MAX_VIDEO_SIZE:
                        raise ValueError(
                            "Video exceeds the 100 MB size limit"
                        )

                    video_file.write(chunk)

        if total_size == 0:
            raise ValueError("Downloaded video file is empty")

        return str(output_path)

    except Exception:
        output_path.unlink(missing_ok=True)
        raise
