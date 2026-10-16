
from unittest.mock import Mock, patch

import pytest

from app.video_downloader import download_video


def test_download_video_saves_mp4(tmp_path):
    fake_response = Mock()
    fake_response.headers = {"Content-Type": "video/mp4"}
    fake_response.iter_content.return_value = [b"fake", b"-video"]
    fake_response.raise_for_status.return_value = None
    fake_response.__enter__ = Mock(return_value=fake_response)
    fake_response.__exit__ = Mock(return_value=False)

    with patch(
        "app.video_downloader.requests.get",
        return_value=fake_response,
    ):
        result = download_video(
            "https://cdn.pixabay.com/video/example.mp4",
            output_dir=str(tmp_path),
        )

    with open(result, "rb") as downloaded_file:
        assert downloaded_file.read() == b"fake-video"


def test_download_video_rejects_non_https_url():
    with pytest.raises(ValueError, match="HTTPS"):
        download_video("http://cdn.pixabay.com/video/example.mp4")


def test_download_video_rejects_other_hosts():
    with pytest.raises(ValueError, match="Pixabay video CDN"):
        download_video("https://example.com/video.mp4")


def test_download_video_rejects_non_mp4_url():
    with pytest.raises(ValueError, match="MP4"):
        download_video("https://cdn.pixabay.com/video/example.jpg")
