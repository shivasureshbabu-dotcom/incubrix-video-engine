
def detect_aspect_ratio(width: int, height: int) -> dict:
    """Identify a video's orientation and approximate aspect ratio."""

    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive numbers")

    ratio = width / height

    if abs(ratio - (16 / 9)) < 0.03:
        format_name = "landscape"
    elif abs(ratio - (9 / 16)) < 0.03:
        format_name = "portrait"
    elif abs(ratio - 1.0) < 0.03:
        format_name = "square"
    else:
        format_name = "other"

    return {
        "width": width,
        "height": height,
        "aspect_ratio": round(ratio, 3),
        "format": format_name,
    }



def get_target_dimensions(format_name: str) -> dict:
    """Return standard output dimensions for a video format."""

    dimensions = {
        "landscape": {"width": 1920, "height": 1080},
        "portrait": {"width": 1080, "height": 1920},
        "square": {"width": 1080, "height": 1080},
    }

    if format_name not in dimensions:
        raise ValueError(
            "Unsupported format. Use landscape, portrait, or square."
        )

    return {
        "format": format_name,
        **dimensions[format_name],
    }
