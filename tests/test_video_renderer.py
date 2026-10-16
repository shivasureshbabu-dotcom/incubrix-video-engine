
import subprocess
from unittest.mock import patch

import pytest

from app.video_renderer import render_video


def test_render_video_creates_output(tmp_path):
    source = tmp_path / "input.mp4"
    output = tmp_path / "output" / "rendered.mp4"
    source.write_bytes(b"fake video")

    def fake_run(command, **kwargs):
        output.write_bytes(b"rendered video")
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    with patch(
        "app.video_renderer.subprocess.run",
        side_effect=fake_run,
    ):
        result = render_video(str(source), str(output))

    assert result == str(output)
    assert output.read_bytes() == b"rendered video"


def test_render_video_rejects_missing_input(tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        render_video(
            str(tmp_path / "missing.mp4"),
            str(tmp_path / "output.mp4"),
        )


def test_render_video_rejects_same_input_and_output(tmp_path):
    source = tmp_path / "same.mp4"
    source.write_bytes(b"fake video")

    with pytest.raises(ValueError, match="different"):
        render_video(str(source), str(source))


def test_render_video_rejects_unsupported_format(tmp_path):
    source = tmp_path / "input.mp4"
    source.write_bytes(b"fake video")

    with pytest.raises(ValueError, match="Unsupported format"):
        render_video(
            str(source),
            str(tmp_path / "output.mp4"),
            format_name="cinema",
        )


def test_render_video_cleans_up_after_ffmpeg_failure(tmp_path):
    source = tmp_path / "input.mp4"
    output = tmp_path / "output.mp4"
    source.write_bytes(b"fake video")

    def fake_run(command, **kwargs):
        output.write_bytes(b"partial output")
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=command,
            stderr="Simulated FFmpeg failure",
        )

    with patch(
        "app.video_renderer.subprocess.run",
        side_effect=fake_run,
    ):
        with pytest.raises(RuntimeError, match="rendering failed"):
            render_video(str(source), str(output))

    assert not output.exists()
