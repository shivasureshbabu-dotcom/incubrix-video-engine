
from app.video_inspector import inspect_video

video = inspect_video("data/videos/287510_medium.mp4")

print("Video inspection successful!")
print("Duration:", video["duration_seconds"], "seconds")
print("Resolution:", video["width"], "x", video["height"])
print("File size:", round(video["size_bytes"] / (1024 * 1024), 2), "MB")
