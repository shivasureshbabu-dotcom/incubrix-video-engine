
import pytest

from unittest.mock import Mock, patch

from app.pixabay_client import search_pixabay_videos


def test_search_pixabay_returns_video_results():
    fake_response = Mock()
    fake_response.json.return_value = {
        "hits": [
            {
                "id": 123,
                "pageURL": "https://pixabay.com/videos/example-123/",
                "user": "ExampleCreator",
                "tags": "nature, forest",
                "duration": 12,
                "videos": {
                    "medium": {
                        "url": "https://example.com/video.mp4"
                    }
                },
            }
        ]
    }
    fake_response.raise_for_status.return_value = None

    with patch("app.pixabay_client.os.getenv", return_value="fake-test-key"):
        with patch("app.pixabay_client.requests.get", return_value=fake_response):
            results = search_pixabay_videos("forest")

    assert len(results) == 1
    assert results[0]["clip_id"] == "123"
    assert results[0]["source_name"] == "Pixabay"
    assert results[0]["creator"] == "ExampleCreator"


def test_search_pixabay_rejects_empty_query():
    with pytest.raises(ValueError, match="Search query"):
        search_pixabay_videos("")


def test_search_pixabay_rejects_invalid_page_size():
    with pytest.raises(ValueError, match="per_page"):
        search_pixabay_videos("forest", per_page=1)


def test_search_pixabay_requires_api_key():
    with patch("app.pixabay_client.os.getenv", return_value=None):
        with pytest.raises(ValueError, match="PIXABAY_API_KEY"):
            search_pixabay_videos("forest")
