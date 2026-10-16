
from pathlib import Path

from app.video_inspector import inspect_video


VIDEO_FOLDER = Path("data/videos")


def check_downloaded_footage():
    if not VIDEO_FOLDER.is_dir():
        print("Video folder not found:", VIDEO_FOLDER)
        return False

    video_files = list(VIDEO_FOLDER.glob("*.mp4"))

    if not video_files:
        print("No MP4 footage found in:", VIDEO_FOLDER)
        return False

    print("Checking downloaded footage...")
    print("-" * 40)

    valid_count = 0

    for video_path in video_files:
        print("\nFile:", video_path.name)

        try:
            info = inspect_video(str(video_path))
        except (ValueError, RuntimeError) as error:
            print("INVALID:", error)
            continue

        print("Duration:", info["duration_seconds"], "seconds")
        print(
            "Resolution:",
            f'{info["width"]} x {info["height"]}',
        )
        print("Audio present:", info["has_audio"])
        print("Size:", round(info["size_bytes"] / (1024 * 1024), 2), "MB")

        if (
            info["duration_seconds"] > 0
            and info["width"] > 0
            and info["height"] > 0
        ):
            print("Status: VALID")
            valid_count += 1
        else:
            print("Status: INVALID")

    print("\n" + "-" * 40)
    print(f"Valid videos: {valid_count} of {len(video_files)}")

    return valid_count > 0


if __name__ == "__main__":
    check_downloaded_footage()
