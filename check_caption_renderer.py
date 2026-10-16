
from app.caption_renderer import burn_captions
from app.video_inspector import inspect_video

output = burn_captions(
    video_path="data/output/forest_final.mp4",
    subtitle_path="data/output/forest_captions.srt",
    output_path="data/output/forest_captioned.mp4",
)

print("Caption rendering successful!")
print("Output file:", output)

metadata = inspect_video(output)
print("Duration:", metadata["duration_seconds"], "seconds")
print("Resolution:", metadata["width"], "x", metadata["height"])
print("Contains audio:", metadata["has_audio"])
