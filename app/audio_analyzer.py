
from pathlib import Path
import math
import sys
import wave
from array import array


def _read_wav(file_path: str):
    """Read a 16-bit PCM WAV file and return its audio data and metadata."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    if path.suffix.lower() != ".wav":
        raise ValueError("Currently, only WAV files are supported.")

    with wave.open(str(path), "rb") as audio:
        sample_width = audio.getsampwidth()
        channels = audio.getnchannels()
        frame_rate = audio.getframerate()
        frame_count = audio.getnframes()
        raw_audio = audio.readframes(frame_count)
        compression = audio.getcomptype()

    if sample_width != 2:
        raise ValueError("Please use a 16-bit PCM WAV file.")

    if compression != "NONE":
        raise ValueError("Please use an uncompressed PCM WAV file.")

    if channels < 1 or frame_rate < 1:
        raise ValueError("Invalid WAV audio format.")

    samples = array("h")
    samples.frombytes(raw_audio)

    if sys.byteorder != "little":
        samples.byteswap()

    # Each WAV frame contains one sample per channel.
    frame_count = len(samples) // channels
    duration = frame_count / frame_rate

    return path, samples, channels, frame_rate, duration


def _rms_windows(samples, channels, frame_rate, window_seconds=0.05):
    """Return (start, end, RMS) for short audio windows."""
    frames_per_window = max(1, int(frame_rate * window_seconds))
    samples_per_window = frames_per_window * channels
    total_frames = len(samples) // channels

    windows = []

    for frame_start in range(0, total_frames, frames_per_window):
        frame_end = min(frame_start + frames_per_window, total_frames)
        sample_start = frame_start * channels
        sample_end = frame_end * channels
        chunk = samples[sample_start:sample_end]

        if not chunk:
            continue

        rms = math.sqrt(
            sum(float(sample) ** 2 for sample in chunk) / len(chunk)
        )

        windows.append((
            frame_start / frame_rate,
            frame_end / frame_rate,
            rms,
        ))

    return windows


def analyze_audio(file_path: str) -> dict:
    """
    Return the WAV duration and detected silence intervals.

    Silence is estimated using 50 ms RMS windows. The threshold adapts
    to the recording's overall loudness, with a configurable noise floor.
    """
    path, samples, channels, frame_rate, duration = _read_wav(file_path)

    if duration <= 0:
        return {
            "filename": path.name,
            "duration_seconds": 0.0,
            "silence_intervals": [],
        }

    windows = _rms_windows(samples, channels, frame_rate)

    # RMS values from each window, including quiet portions.
    rms_values = [rms for _, _, rms in windows]

    # Estimate typical loudness from the louder windows so pauses do not
    # pull the reference level down too much.
    louder_values = [
        rms for rms in rms_values
        if rms > 0
    ]

    if not louder_values:
        return {
            "filename": path.name,
            "duration_seconds": round(duration, 2),
            "silence_intervals": [{
                "start": 0.0,
                "end": round(duration, 2),
            }] if duration >= 0.5 else [],
        }

    louder_values.sort()
    reference = louder_values[int(0.70 * (len(louder_values) - 1))]

    # Keep a minimum threshold for low-level digital noise, while adapting
    # to quiet or loud recordings. Adjust these values if needed.
    silence_threshold = max(80.0, reference * 0.08)
    min_silence_seconds = 0.30

    silence_intervals = []
    silence_start = None

    for start, end, rms in windows:
        is_silent = rms < silence_threshold

        if is_silent and silence_start is None:
            silence_start = start

        elif not is_silent and silence_start is not None:
            if start - silence_start >= min_silence_seconds:
                silence_intervals.append({
                    "start": round(silence_start, 2),
                    "end": round(start, 2),
                })
            silence_start = None

    # Include silence that continues through the end of the recording.
    if silence_start is not None:
        if duration - silence_start >= min_silence_seconds:
            silence_intervals.append({
                "start": round(silence_start, 2),
                "end": round(duration, 2),
            })

    return {
        "filename": path.name,
        "duration_seconds": round(duration, 2),
        "silence_intervals": silence_intervals,
    }


def detect_emphasis(file_path: str) -> dict:
    """Detect audio windows that are louder than the recording's baseline."""
    path, samples, channels, frame_rate, _ = _read_wav(file_path)

    # Quarter-second windows make the results easier to interpret.
    windows = _rms_windows(
        samples,
        channels,
        frame_rate,
        window_seconds=0.25,
    )

    non_silent = [
        rms for _, _, rms in windows
        if rms > 80
    ]

    if not non_silent:
        return {"emphasis_intervals": []}

    non_silent.sort()
    baseline = non_silent[len(non_silent) // 2]

    # A window must be clearly louder than typical speech to count.
    threshold = max(500.0, baseline * 1.5)

    emphasis_intervals = []

    for start, end, rms in windows:
        if rms >= threshold and rms > baseline * 1.5:
            emphasis_intervals.append({
                "start": round(start, 2),
                "end": round(end, 2),
                "loudness": round(rms, 1),
            })

    return {"emphasis_intervals": emphasis_intervals}


def create_scene_timing(
    duration_seconds: float,
    silence_intervals: list[dict],
    emphasis_intervals: list[dict],
) -> dict:
    """Create scene boundaries using silence and emphasis timestamps."""
    if duration_seconds <= 0:
        raise ValueError("Duration must be greater than zero.")

    boundaries = {0.0, float(duration_seconds)}

    for interval in silence_intervals:
        start = float(interval["start"])
        end = float(interval["end"])

        if 0 < start < duration_seconds:
            boundaries.add(start)

        if 0 < end < duration_seconds:
            boundaries.add(end)

    for interval in emphasis_intervals:
        start = float(interval["start"])

        if 0 < start < duration_seconds:
            boundaries.add(start)

    sorted_boundaries = sorted(boundaries)
    scenes = []

    for start, end in zip(sorted_boundaries, sorted_boundaries[1:]):
        if end <= start:
            continue

        scenes.append({
            "scene_number": len(scenes) + 1,
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": round(end - start, 2),
        })

    return {
        "duration_seconds": round(duration_seconds, 2),
        "scenes": scenes,
    }
