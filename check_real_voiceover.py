
from app.audio_video_merger import merge_audio_with_video
from app.video_inspector import inspect_video

output = merge_audio_with_video(
    video_path="data/output/forest_landscape.mp4",
    audio_path="data/output/forest_voiceover.mp3",
    output_path="data/output/forest_final.mp4",
)

print("Real voiceover merged successfully!")
print("Output file:", output)

metadata = inspect_video(output)

print("Duration:", metadata["duration_seconds"], "seconds")
print("Resolution:", metadata["width"], "x", metadata["height"])
print("Contains audio:", metadata["has_audio"])
