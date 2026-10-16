
from app.video_format import (
    detect_aspect_ratio,
    get_target_dimensions,
)
from app.video_inspector import inspect_video


def validate_video(file_path: str) -> dict:
    """Inspect a video and recommend a matching output format."""

    metadata = inspect_video(file_path)

    detected_format = detect_aspect_ratio(
        metadata["width"],
        metadata["height"],
    )

    target = get_target_dimensions(detected_format["format"])

    return {
        "video": metadata,
        "detected_format": detected_format["format"],
        "aspect_ratio": detected_format["aspect_ratio"],
        "target_dimensions": target,
        "valid": True,
    }
