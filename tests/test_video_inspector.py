
import json
import subprocess
from unittest.mock import patch

import pytest

from app.video_inspector import inspect_video


def test_inspect_video_returns_metadata(tmp_path):
    video_file = tmp_path / "sample.mp4"
    video_file.write_bytes(b"fake video data")

    fake_output = {
        "streams": [
            {
                "codec_type": "video",
                "width": 1920,
                "height": 1080,
            }
        ],
        "format": {"duration": "12.5"},
    }

    completed = subprocess.CompletedProcess(
        args=["ffprobe"],
        returncode=0,
        stdout=json.dumps(fake_output),
        stderr="",
    )

    with patch(
        "app.video_inspector.subprocess.run",
        return_value=completed,
    ):
        result = inspect_video(str(video_file))

    assert result["duration_seconds"] == 12.5
    assert result["width"] == 1920
    assert result["height"] == 1080
    assert result["size_bytes"] == len(b"fake video data")


def test_inspect_video_rejects_missing_file():
    with pytest.raises(ValueError, match="does not exist"):
        inspect_video("missing_video.mp4")


def test_inspect_video_rejects_empty_file(tmp_path):
    video_file = tmp_path / "empty.mp4"
    video_file.write_bytes(b"")

    with pytest.raises(ValueError, match="empty"):
        inspect_video(str(video_file))


def test_inspect_video_rejects_no_video_stream(tmp_path):
    video_file = tmp_path / "audio_only.mp4"
    video_file.write_bytes(b"fake audio data")

    fake_output = {
        "streams": [
            {"codec_type": "audio"}
        ],
        "format": {"duration": "12.5"},
    }

    completed = subprocess.CompletedProcess(
        args=["ffprobe"],
        returncode=0,
        stdout=json.dumps(fake_output),
        stderr="",
    )

    with patch(
        "app.video_inspector.subprocess.run",
        return_value=completed,
    ):
        with pytest.raises(ValueError, match="No video stream"):
            inspect_video(str(video_file))



import json
import subprocess
from unittest.mock import patch

import pytest

from app.video_inspector import inspect_video


def test_inspect_video_detects_audio_stream(tmp_path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake video")

    ffprobe_output = {
        "format": {"duration": "5.0"},
        "streams": [
            {
                "codec_type": "video",
                "width": 1920,
                "height": 1080,
            },
            {
                "codec_type": "audio",
            },
        ],
    }

    completed = subprocess.CompletedProcess(
        args=["ffprobe"],
        returncode=0,
        stdout=json.dumps(ffprobe_output),
        stderr="",
    )

    with patch(
        "app.video_inspector.subprocess.run",
        return_value=completed,
    ):
        result = inspect_video(str(video))

    assert result["has_audio"] is True
    assert result["width"] == 1920
    assert result["height"] == 1080


def test_inspect_video_detects_missing_audio_stream(tmp_path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake video")

    ffprobe_output = {
        "format": {"duration": "5.0"},
        "streams": [
            {
                "codec_type": "video",
                "width": 1920,
                "height": 1080,
            },
        ],
    }

    completed = subprocess.CompletedProcess(
        args=["ffprobe"],
        returncode=0,
        stdout=json.dumps(ffprobe_output),
        stderr="",
    )

    with patch(
        "app.video_inspector.subprocess.run",
        return_value=completed,
    ):
        result = inspect_video(str(video))

    assert result["has_audio"] is False
