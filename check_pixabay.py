
from pathlib import Path

from app.pixabay_client import search_pixabay_videos
from app.video_downloader import download_video


try:
    videos = search_pixabay_videos("forest", per_page=3)

    if not videos:
        print("No videos found.")
    else:
        video = videos[0]
        print("Selected video:", video["clip_id"])
        print("Creator:", video["creator"])
        print("Downloading video...")

        saved_path = download_video(video["download_url"])

        file_size = Path(saved_path).stat().st_size

        print("Download successful!")
        print("Saved to:", saved_path)
        print("File size:", round(file_size / (1024 * 1024), 2), "MB")

except Exception as error:
    print("Video download failed:", error)
