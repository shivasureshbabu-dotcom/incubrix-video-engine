
from app.video_format import detect_aspect_ratio

video_format = detect_aspect_ratio(2560, 1440)

print("Video format:", video_format["format"])
print("Aspect ratio:", video_format["aspect_ratio"])
