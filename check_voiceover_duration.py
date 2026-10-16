
from app.video_inspector import inspect_video

audio = inspect_video("data/output/forest_final.mp4")
print("Current video duration:", audio["duration_seconds"], "seconds")

import os
import subprocess

ffprobe = os.getenv("FFPROBE_PATH", "ffprobe")

result = subprocess.run(
    [
        ffprobe,
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        "data/output/forest_voiceover.mp3",
    ],
    capture_output=True,
    text=True,
    check=True,
)

print("Voiceover duration:", result.stdout.strip(), "seconds")
