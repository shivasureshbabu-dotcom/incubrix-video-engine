
from pathlib import Path
import wave


def analyze_audio(file_path: str) -> dict:
    """
    Analyze a WAV audio file and return its duration
    and detected silence intervals.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    if path.suffix.lower() != ".wav":
        raise ValueError("Currently, only WAV files are supported.")

    with wave.open(str(path), "rb") as audio:
        frame_rate = audio.getframerate()
        frame_count = audio.getnframes()
        sample_width = audio.getsampwidth()
        channels = audio.getnchannels()
        frames = audio.readframes(frame_count)

    duration = frame_count / frame_rate

    # This first version supports standard 16-bit PCM WAV files.
    if sample_width != 2:
        raise ValueError("Please use a 16-bit PCM WAV file.")

    silence_threshold = 500
    min_silence_seconds = 0.5
    samples_per_frame = channels
    silence_intervals = []
    silence_start = None

    for i in range(0, len(frames), sample_width * samples_per_frame):
        sample_bytes = frames[i:i + sample_width * samples_per_frame]
        if len(sample_bytes) < sample_width * samples_per_frame:
            break

        # Find the loudest channel in this audio frame.
        amplitudes = [
            abs(int.from_bytes(
                sample_bytes[j:j + sample_width],
                byteorder="little",
                signed=True
            ))
            for j in range(0, len(sample_bytes), sample_width)
        ]

        is_silent = max(amplitudes, default=0) < silence_threshold
        timestamp = i / (sample_width * samples_per_frame * frame_rate)

        if is_silent and silence_start is None:
            silence_start = timestamp
        elif not is_silent and silence_start is not None:
            if timestamp - silence_start >= min_silence_seconds:
                silence_intervals.append({
                    "start": round(silence_start, 2),
                    "end": round(timestamp, 2)
                })
            silence_start = None

    if silence_start is not None:
        if duration - silence_start >= min_silence_seconds:
            silence_intervals.append({
                "start": round(silence_start, 2),
                "end": round(duration, 2)
            })

    return {
        "filename": path.name,
        "duration_seconds": round(duration, 2),
        "silence_intervals": silence_intervals
    }



def detect_emphasis(file_path: str) -> dict:
    """Detect sections that are noticeably louder than the surrounding audio."""
    from array import array
    from pathlib import Path
    import math
    import wave

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    if path.suffix.lower() != ".wav":
        raise ValueError("Currently, only WAV files are supported.")

    with wave.open(str(path), "rb") as audio:
        sample_width = audio.getsampwidth()
        channels = audio.getnchannels()
        frame_rate = audio.getframerate()
        raw_audio = audio.readframes(audio.getnframes())

    if sample_width != 2:
        raise ValueError("Please use a 16-bit PCM WAV file.")

    samples = array("h")
    samples.frombytes(raw_audio)

    # WAV audio is little-endian; convert if this computer uses big-endian.
    if samples.itemsize != 2:
        raise ValueError("Unsupported audio sample format.")

    if __import__("sys").byteorder != "little":
        samples.byteswap()

    frame_size = channels
    samples_per_window = max(frame_rate // 4, 1) * frame_size
    windows = []

    for start in range(0, len(samples), samples_per_window):
        chunk = samples[start:start + samples_per_window]
        if not chunk:
            continue

        rms = math.sqrt(sum(float(s) * s for s in chunk) / len(chunk))
        time_start = start / (frame_rate * frame_size)
        time_end = min(
            (start + len(chunk)) / (frame_rate * frame_size),
            len(samples) / (frame_rate * frame_size),
        )
        windows.append((time_start, time_end, rms))

    non_silent = [rms for _, _, rms in windows if rms > 500]
    if not non_silent:
        return {"emphasis_intervals": []}

    average = sum(non_silent) / len(non_silent)
    threshold = max(average * 1.5, 1000)

    emphasis_intervals = []
    for start, end, rms in windows:
        if rms >= threshold:
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

    # Start with the beginning and end of the audio.
    boundaries = {0.0, float(duration_seconds)}

    # Add boundaries around detected silence intervals.
    for interval in silence_intervals:
        start = float(interval["start"])
        end = float(interval["end"])

        if 0 < start < duration_seconds:
            boundaries.add(start)

        if 0 < end < duration_seconds:
            boundaries.add(end)

    # Add boundaries where louder audio sections begin.
    for interval in emphasis_intervals:
        start = float(interval["start"])

        if 0 < start < duration_seconds:
            boundaries.add(start)

    # Sort the boundaries from beginning to end.
    sorted_boundaries = sorted(boundaries)

    # Build one scene between each pair of boundaries.
    scenes = []

    for start, end in zip(
        sorted_boundaries,
        sorted_boundaries[1:],
    ):
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
