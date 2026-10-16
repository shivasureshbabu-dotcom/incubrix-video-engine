
import json
from pathlib import Path

from app.video_inspector import inspect_video


VIDEO_PATH = Path("data/output/forest_captioned.mp4")
MANIFEST_PATH = Path("data/output/video_manifest.json")


def create_video_manifest():
    if not VIDEO_PATH.is_file():
        raise FileNotFoundError(
            f"Final video not found: {VIDEO_PATH}"
        )

    video_info = inspect_video(str(VIDEO_PATH))

    manifest = {
        "project_name": "IncuBrix Video Engine",
        "status": "completed",
        "output_video": {
            "file_path": str(VIDEO_PATH),
            "duration_seconds": video_info["duration_seconds"],
            "width": video_info["width"],
            "height": video_info["height"],
            "has_audio": video_info["has_audio"],
            "size_bytes": video_info["size_bytes"],
        },
        "captions": {
            "file_path": "data/output/forest_captions.srt",
            "timing_method": "estimated",
        },
        "clips": [
            {
                "clip_id": "287510",
                "source_name": "Pixabay",
                "source_url": "https://pixabay.com/videos/id-287510/",
                "creator": "Thamnguyen_TBVN",
                "license_name": "Pixabay Content License",
                "license_url": "https://pixabay.com/service/license/",
                "downloaded_file": "data/videos/287510_medium.mp4",
                "license_verified": False,
            }
        ],
    }

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=4),
        encoding="utf-8",
    )

    print("Video manifest created successfully!")
    print("Manifest:", MANIFEST_PATH)
    print("Output video:", VIDEO_PATH)
    print("Duration:", video_info["duration_seconds"], "seconds")
    print("Footage entries:", len(manifest["clips"]))
    print("License verified:", False)


if __name__ == "__main__":
    try:
        create_video_manifest()
    except (OSError, ValueError, RuntimeError) as error:
        print("Could not create manifest:", error)
