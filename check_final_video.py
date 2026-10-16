
from pathlib import Path

from app.video_inspector import inspect_video


VIDEO_PATH = Path("data/output/forest_captioned.mp4")


def check_final_video():
    print("Checking final video...")
    print("-" * 40)

    if not VIDEO_PATH.is_file():
        print("ERROR: Final video file was not found.")
        print("Expected location:", VIDEO_PATH)
        return False

    try:
        info = inspect_video(str(VIDEO_PATH))
    except (ValueError, RuntimeError) as error:
        print("ERROR: Could not inspect video:", error)
        return False

    print("Video:", info["file_path"])
    print("Duration:", info["duration_seconds"], "seconds")
    print(
        "Resolution:",
        f'{info["width"]} x {info["height"]}',
    )
    print("Audio present:", info["has_audio"])
    print("File size:", round(info["size_bytes"] / (1024 * 1024), 2), "MB")

    problems = []

    if not info["has_audio"]:
        problems.append("Audio is missing.")

    if info["width"] != 1920 or info["height"] != 1080:
        problems.append("Video resolution is not 1920 x 1080.")

    if info["duration_seconds"] < 17.0:
        problems.append("Video is shorter than expected.")

    if problems:
        print("\nVALIDATION FAILED")
        for problem in problems:
            print("-", problem)
        return False

    print("\nVALIDATION PASSED")
    print("The final video has audio, the expected resolution,")
    print("and a duration of at least 17 seconds.")

    return True


if __name__ == "__main__":
    check_final_video()

