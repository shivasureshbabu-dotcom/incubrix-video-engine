
from pathlib import Path

from app.pixabay_client import search_pixabay_videos
from app.video_downloader import download_video


def run_footage_workflow(query: str) -> str:
    print("Starting footage workflow...")
    print("Search query:", query)
    print("-" * 40)

    # Step 1: Search Pixabay for video footage.
    videos = search_pixabay_videos(query, per_page=10)

    if not videos:
        raise RuntimeError(
            f"No Pixabay videos found for query: {query}"
        )

    print("Videos found:", len(videos))

    # Step 2: Choose the first result that has a download URL.
    selected_video = next(
        (
            video
            for video in videos
            if video.get("download_url")
        ),
        None,
    )

    if selected_video is None:
        raise RuntimeError(
            "Search results contained no downloadable videos."
        )

    print("Selected clip ID:", selected_video["clip_id"])
    print("Creator:", selected_video["creator"])
    print("Source:", selected_video["source_url"])

    # Step 3: Download the selected video.
    downloaded_path = download_video(
        selected_video["download_url"],
        output_dir="data/videos",
    )

    if not Path(downloaded_path).is_file():
        raise RuntimeError("The downloaded video file was not found.")

    print("-" * 40)
    print("Footage workflow completed!")
    print("Downloaded video:", downloaded_path)

    return downloaded_path


if __name__ == "__main__":
    try:
        run_footage_workflow("forest")
    except (ValueError, RuntimeError, OSError) as error:
        print("Footage workflow failed:", error)
    except Exception as error:
        print("Unexpected error:", error)
