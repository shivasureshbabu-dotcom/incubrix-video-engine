
import math
import wave
from array import array
from pathlib import Path

output = Path("data/output/test_narration.wav")
output.parent.mkdir(parents=True, exist_ok=True)

sample_rate = 16000
duration_seconds = 5
frequency = 440

samples = array(
    "h",
    (
        int(5000 * math.sin(2 * math.pi * frequency * i / sample_rate))
        for i in range(sample_rate * duration_seconds)
    ),
)

with wave.open(str(output), "wb") as audio:
    audio.setnchannels(1)
    audio.setsampwidth(2)
    audio.setframerate(sample_rate)
    audio.writeframes(samples.tobytes())

print("Test audio created:", output)
print("Duration:", duration_seconds, "seconds")
