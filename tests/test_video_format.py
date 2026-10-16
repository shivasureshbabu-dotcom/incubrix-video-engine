
import pytest

from app.video_format import detect_aspect_ratio


def test_detects_landscape():
    result = detect_aspect_ratio(1920, 1080)

    assert result["format"] == "landscape"
    assert result["aspect_ratio"] == 1.778


def test_detects_portrait():
    result = detect_aspect_ratio(1080, 1920)

    assert result["format"] == "portrait"
    assert result["aspect_ratio"] == 0.562


def test_detects_square():
    result = detect_aspect_ratio(1080, 1080)

    assert result["format"] == "square"
    assert result["aspect_ratio"] == 1.0


def test_detects_other_ratio():
    result = detect_aspect_ratio(1600, 900)

    assert result["format"] == "landscape"


@pytest.mark.parametrize(
    "width,height",
    [(0, 1080), (1920, 0), (-1, 1080), (1920, -1)],
)
def test_rejects_invalid_dimensions(width, height):
    with pytest.raises(ValueError, match="positive"):
        detect_aspect_ratio(width, height)



from app.video_format import get_target_dimensions


def test_landscape_target_dimensions():
    result = get_target_dimensions("landscape")

    assert result == {
        "format": "landscape",
        "width": 1920,
        "height": 1080,
    }


def test_portrait_target_dimensions():
    result = get_target_dimensions("portrait")

    assert result == {
        "format": "portrait",
        "width": 1080,
        "height": 1920,
    }


def test_square_target_dimensions():
    result = get_target_dimensions("square")

    assert result == {
        "format": "square",
        "width": 1080,
        "height": 1080,
    }


def test_rejects_unsupported_target_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        get_target_dimensions("cinema")
