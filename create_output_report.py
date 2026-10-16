
import json
from pathlib import Path

from app.video_inspector import inspect_video


OUTPUT_FOLDER = Path("data/output")
REPORT_PATH = OUTPUT_FOLDER / "output_report.json"


def create_output_report():
    if not OUTPUT_FOLDER.is_dir():
        raise FileNotFoundError(
            f"Output folder not found: {OUTPUT_FOLDER}"
        )

    video_files = sorted(
        path
        for path in OUTPUT_FOLDER.glob("*.mp4")
        if path.is_file()
    )

    if not video_files:
        raise ValueError("No MP4 output videos were found.")

    report = {
        "project": "IncuBrix Video Engine",
        "video_count": len(video_files),
        "videos": [],
    }

    for video_path in video_files:
        try:
            info = inspect_video(str(video_path))

            report["videos"].append({
                "file_name": video_path.name,
                "file_path": str(video_path),
                "duration_seconds": info["duration_seconds"],
                "width": info["width"],
                "height": info["height"],
                "has_audio": info["has_audio"],
                "size_mb": round(
                    info["size_bytes"] / (1024 * 1024), 2
                ),
                "inspection_status": "passed",
            })

        except (ValueError, RuntimeError) as error:
            report["videos"].append({
                "file_name": video_path.name,
                "file_path": str(video_path),
                "inspection_status": "failed",
                "error": str(error),
            })

    passed_count = sum(
        item["inspection_status"] == "passed"
        for item in report["videos"]
    )

    report["valid_video_count"] = passed_count
    report["failed_video_count"] = len(video_files) - passed_count

    REPORT_PATH.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8",
    )

    print("Output report created!")
    print("Report:", REPORT_PATH)
    print("Videos found:", len(video_files))
    print("Successfully inspected:", passed_count)
    print("Failed inspections:", len(video_files) - passed_count)


if __name__ == "__main__":
    try:
        create_output_report()
    except (OSError, ValueError, RuntimeError) as error:
        print("Could not create output report:", error)
