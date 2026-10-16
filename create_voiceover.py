
from pathlib import Path
from gtts import gTTS

script = """
Forests are among the most important ecosystems on Earth.
They provide shelter for wildlife, clean the air, and help
maintain the balance of our planet. Protecting forests
helps create a healthier future for everyone.
"""

output = Path("data/output/forest_voiceover.mp3")
output.parent.mkdir(parents=True, exist_ok=True)

tts = gTTS(text=script, lang="en", slow=False)
tts.save(str(output))

print("Voiceover created successfully!")
print("Audio file:", output)
print("Script:", " ".join(script.split()))
