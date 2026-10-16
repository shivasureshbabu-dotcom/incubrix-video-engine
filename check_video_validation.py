
from app.video_validation import validate_video

result = validate_video("data/videos/287510_medium.mp4")

print("Video valid:", result["valid"])
print("Detected format:", result["detected_format"])
print("Aspect ratio:", result["aspect_ratio"])
print("Recommended output:", result["target_dimensions"]["width"],
      "x", result["target_dimensions"]["height"])
