
from unittest.mock import patch

from app.video_validation import validate_video


def test_validate_video_returns_landscape_recommendation():
    fake_metadata = {
        "file_path": "sample.mp4",
        "duration_seconds": 12.5,
        "width": 2560,
        "height": 1440,
        "size_bytes": 1000,
    }

    with patch(
        "app.video_validation.inspect_video",
        return_value=fake_metadata,
    ):
        result = validate_video("sample.mp4")

    assert result["valid"] is True
    assert result["detected_format"] == "landscape"
    assert result["aspect_ratio"] == 1.778
    assert result["target_dimensions"]["width"] == 1920
    assert result["target_dimensions"]["height"] == 1080


def test_validate_video_returns_portrait_recommendation():
    fake_metadata = {
        "file_path": "portrait.mp4",
        "duration_seconds": 10.0,
        "width": 1080,
        "height": 1920,
        "size_bytes": 1000,
    }

    with patch(
        "app.video_validation.inspect_video",
        return_value=fake_metadata,
    ):
        result = validate_video("portrait.mp4")

    assert result["detected_format"] == "portrait"
    assert result["target_dimensions"]["width"] == 1080
    assert result["target_dimensions"]["height"] == 1920


def test_validate_video_propagates_inspection_error():
    with patch(
        "app.video_validation.inspect_video",
        side_effect=ValueError("Video file does not exist"),
    ):
        try:
            validate_video("missing.mp4")
        except ValueError as error:
            assert "does not exist" in str(error)
        else:
            raise AssertionError("Expected ValueError")
