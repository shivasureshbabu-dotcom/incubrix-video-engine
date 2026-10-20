
import math
import tempfile
import wave
from pathlib import Path

from app.audio_analyzer import analyze_audio


def write_test_wav(path: Path):
    sample_rate = 16000
    amplitude = 8000

    def tone(seconds):
        count = int(sample_rate * seconds)
        return b"".join(
            int(amplitude * math.sin(
                2 * math.pi * 440 * i / sample_rate
            )).to_bytes(2, "little", signed=True)
            for i in range(count)
        )

    silence = b"\x00\x00" * sample_rate

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(tone(1.0) + silence + tone(1.0))


def main():
    with tempfile.TemporaryDirectory() as folder:
        test_path = Path(folder) / "known_silence.wav"
        write_test_wav(test_path)

        result = analyze_audio(str(test_path))
        print("Duration:", result["duration_seconds"])
        print("Detected silence:", result["silence_intervals"])

        assert result["duration_seconds"] == 3.0
        assert result["silence_intervals"], (
            "FAIL: the detector did not find the known silent gap."
        )

        found_gap = any(
            interval["start"] <= 1.1 and interval["end"] >= 1.9
            for interval in result["silence_intervals"]
        )
        assert found_gap, "FAIL: detected silence does not cover the gap."

        print("PASS: known one-second silent gap was detected.")


if __name__ == "__main__":
    main()
