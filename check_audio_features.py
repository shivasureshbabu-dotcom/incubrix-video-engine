
import wave
from pathlib import Path

from app.audio_analyzer import analyze_audio, detect_emphasis


AUDIO_PATH = Path("data/output/test_narration.wav")


def main():
    print("Testing Silence & Emphasis Detector")
    print("-" * 40)

    if not AUDIO_PATH.is_file():
        print("Test audio not found:", AUDIO_PATH)
        print("Run your audio test-generation script first.")
        return

    # Test audio analysis and silence detection.
    analysis = analyze_audio(str(AUDIO_PATH))
    print("Audio duration:", analysis["duration_seconds"], "seconds")
    print("Silence intervals:", analysis["silence_intervals"])

    # Test louder-than-average audio detection.
    emphasis = detect_emphasis(str(AUDIO_PATH))
    intervals = emphasis["emphasis_intervals"]

    print("Emphasis intervals detected:", len(intervals))

    for interval in intervals[:5]:
        print(
            "Start:", interval["start"],
            "| End:", interval["end"],
            "| Loudness:", interval["loudness"],
        )

    # Verify that the detector returned the expected structure.
    assert isinstance(analysis["silence_intervals"], list)
    assert isinstance(intervals, list)

    print("\nAudio feature checks passed!")
    print(
        "Note: a steady test tone may not contain meaningful "
        "silences or emphasis."
    )


if __name__ == "__main__":
    main()
