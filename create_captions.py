
from pathlib import Path


# Sentences to display as subtitles.
sentences = [
    "Forests are among the most important ecosystems on Earth.",
    "They provide shelter for wildlife, clean the air, and help",
    "maintain the balance of our planet.",
    "Protecting forests helps create a healthier future for everyone.",
]

# Estimated caption timings for the 17.184-second voiceover.
# These are approximate and can be adjusted after watching the video.
timings = [
    (0.0, 4.2),
    (4.2, 8.3),
    (8.3, 11.2),
    (11.2, 17.184),
]


def srt_timestamp(seconds: float) -> str:
    """Convert seconds to the SRT timestamp format."""
    milliseconds = round(seconds * 1000)

    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds_part, milliseconds = divmod(milliseconds, 1000)

    return (
        f"{hours:02}:{minutes:02}:"
        f"{seconds_part:02},{milliseconds:03}"
    )


def create_captions() -> str:
    """Create an SRT subtitle file for the forest voiceover."""

    if len(sentences) != len(timings):
        raise ValueError(
            "Each caption sentence must have a timing entry."
        )

    blocks = []
    previous_end = 0.0

    for index, (sentence, timing) in enumerate(
        zip(sentences, timings),
        start=1,
    ):
        start, end = timing

        if not sentence.strip():
            raise ValueError(
                f"Caption {index} cannot be empty."
            )

        if start < previous_end or end <= start:
            raise ValueError(
                f"Caption {index} has invalid timing."
            )

        blocks.append(
            f"{index}\n"
            f"{srt_timestamp(start)} --> "
            f"{srt_timestamp(end)}\n"
            f"{sentence}\n"
        )

        previous_end = end

    output_path = Path("data/output/forest_captions.srt")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        "\n".join(blocks),
        encoding="utf-8",
    )

    return str(output_path)


if __name__ == "__main__":
    try:
        caption_file = create_captions()

        print("Captions created successfully!")
        print("Output file:", caption_file)
        print("Number of captions:", len(sentences))
        print("Final caption ends at 17.184 seconds.")

    except (ValueError, OSError) as error:
        print("Could not create captions:", error)
