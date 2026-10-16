
import os

import requests
from dotenv import load_dotenv

load_dotenv()

PIXABAY_API_URL = "https://pixabay.com/api/videos/"


def search_pixabay_videos(query: str, per_page: int = 10) -> list[dict]:
    """Search Pixabay for videos matching a keyword."""

    api_key = os.getenv("PIXABAY_API_KEY")

    if not api_key:
        raise ValueError("PIXABAY_API_KEY is missing from the .env file")

    if not query.strip():
        raise ValueError("Search query cannot be empty")

    if not 3 <= per_page <= 200:
        raise ValueError("per_page must be between 3 and 200")

    response = requests.get(
        PIXABAY_API_URL,
        params={
            "key": api_key,
            "q": query,
            "per_page": per_page,
            "safesearch": "true",
        },
        timeout=20,
    )

    response.raise_for_status()
    data = response.json()

    videos = []

    for item in data.get("hits", []):
        video_files = item.get("videos", {})

        preferred_video = (
            video_files.get("medium")
            or video_files.get("small")
            or video_files.get("large")
            or video_files.get("tiny")
            or {}
        )

        videos.append({
            "clip_id": str(item["id"]),
            "source_name": "Pixabay",
            "source_url": item.get("pageURL", ""),
            "creator": item.get("user", ""),
            "tags": item.get("tags", ""),
            "duration_seconds": item.get("duration"),
            "video_files": video_files,
            "download_url": preferred_video.get("url"),
            "video_width": preferred_video.get("width"),
            "video_height": preferred_video.get("height"),
        })

    return videos
