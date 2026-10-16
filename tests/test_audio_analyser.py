
import wave

from app.audio_analyzer import analyze_audio, detect_emphasis


def create_test_wav(path):
    sample_rate = 8000

    # 1 second silence, 1 second tone, 1 second silence.
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)

        silence = b"\x00\x00" * sample_rate
        tone = b"".join(
            int(5000 * __import__("math").sin(
                2 * __import__("math").pi * 440 * i / sample_rate
            )).to_bytes(2, "little", signed=True)
            for i in range(sample_rate)
        )

        audio.writeframes(silence + tone + silence)


def test_analyze_audio_detects_silence(tmp_path):
    audio_file = tmp_path / "sample.wav"
    create_test_wav(audio_file)

    result = analyze_audio(str(audio_file))

    assert result["duration_seconds"] == 3.0
    assert len(result["silence_intervals"]) >= 1




def test_detect_emphasis_finds_louder_audio(tmp_path):
    import math
    import struct
    import wave

    sample_rate = 8000
    samples = []

    # First second: quiet audio.
    for _ in range(sample_rate):
        samples.append(int(1000 * math.sin(2 * math.pi * 440 * _ / sample_rate)))

    # Second second: louder audio.
    for _ in range(sample_rate):
        samples.append(int(10000 * math.sin(2 * math.pi * 440 * _ / sample_rate)))

    audio_path = tmp_path / "emphasis_test.wav"

    with wave.open(str(audio_path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(
            b"".join(struct.pack("<h", sample) for sample in samples)
        )

    result = detect_emphasis(str(audio_path))

    assert len(result["emphasis_intervals"]) >= 1
    assert any(
        interval["start"] >= 1.0
        for interval in result["emphasis_intervals"]
    )




from app.audio_analyzer import create_scene_timing


def test_create_scene_timing_uses_silence_and_emphasis():
    result = create_scene_timing(
        duration_seconds=10,
        silence_intervals=[
            {"start": 4, "end": 5}
        ],
        emphasis_intervals=[
            {"start": 7, "end": 8, "loudness": 3000}
        ],
    )

    assert result["duration_seconds"] == 10
    assert len(result["scenes"]) == 4

    assert result["scenes"][0]["start"] == 0
    assert result["scenes"][0]["end"] == 4

    assert result["scenes"][1]["start"] == 4
    assert result["scenes"][1]["end"] == 5

    assert result["scenes"][2]["start"] == 5
    assert result["scenes"][2]["end"] == 7

    assert result["scenes"][3]["start"] == 7
    assert result["scenes"][3]["end"] == 10
