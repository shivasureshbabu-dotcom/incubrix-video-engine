
from app.video_format import get_target_dimensions

for video_format in ["landscape", "portrait", "square"]:
    result = get_target_dimensions(video_format)
    print(result)
