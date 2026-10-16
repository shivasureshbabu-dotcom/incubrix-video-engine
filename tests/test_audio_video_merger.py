
import subprocess
from unittest.mock import patch

import pytest

from app.audio_video_merger import merge_audio_with_video


def test_merge_audio_with_video_creates_output(tmp_path):
    video = tmp_path / "video.mp4"
    audio = tmp_path / "voice.wav"
    output = tmp_path / "output" / "final.mp4"

    video.write_bytes(b"fake video")
    audio.write_bytes(b"fake audio")

    def fake_run(command, **kwargs):
        output.write_bytes(b"combined video and audio")
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    with patch(
        "app.audio_video_merger.subprocess.run",
        side_effect=fake_run,
    ):
        result = merge_audio_with_video(
            str(video), str(audio), str(output)
        )

    assert result == str(output)
    assert output.read_bytes() == b"combined video and audio"


def test_merge_rejects_missing_video(tmp_path):
    audio = tmp_path / "voice.wav"
    audio.write_bytes(b"fake audio")

    with pytest.raises(ValueError, match="Video file does not exist"):
        merge_audio_with_video(
            str(tmp_path / "missing.mp4"),
            str(audio),
            str(tmp_path / "output.mp4"),
        )


def test_merge_rejects_missing_audio(tmp_path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake video")

    with pytest.raises(ValueError, match="Audio file does not exist"):
        merge_audio_with_video(
            str(video),
            str(tmp_path / "missing.wav"),
            str(tmp_path / "output.mp4"),
        )


def test_merge_rejects_output_same_as_input(tmp_path):
    video = tmp_path / "video.mp4"
    audio = tmp_path / "voice.wav"
    video.write_bytes(b"fake video")
    audio.write_bytes(b"fake audio")

    with pytest.raises(ValueError, match="Output path must differ"):
        merge_audio_with_video(
            str(video), str(audio), str(video)
        )


def test_merge_cleans_up_after_ffmpeg_failure(tmp_path):
    video = tmp_path / "video.mp4"
    audio = tmp_path / "voice.wav"
    output = tmp_path / "output.mp4"

    video.write_bytes(b"fake video")
    audio.write_bytes(b"fake audio")

    def fake_run(command, **kwargs):
        output.write_bytes(b"partial output")
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=command,
            stderr="Simulated FFmpeg failure",
        )

    with patch(
        "app.audio_video_merger.subprocess.run",
        side_effect=fake_run,
    ):
        with pytest.raises(RuntimeError, match="merging failed"):
            merge_audio_with_video(
                str(video), str(audio), str(output)
            )

    assert not output.exists()
