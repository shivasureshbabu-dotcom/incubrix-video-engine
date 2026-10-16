
from app.video_renderer import render_video
from app.video_inspector import inspect_video

output = render_video(
    input_path="data/videos/287510_medium.mp4",
    output_path="data/output/forest_landscape.mp4",
    format_name="landscape",
)

print("Rendering successful!")
print("Output file:", output)

metadata = inspect_video(output)
print("Duration:", metadata["duration_seconds"], "seconds")
print(
    "Resolution:",
    metadata["width"],
    "x",
    metadata["height"],
)
