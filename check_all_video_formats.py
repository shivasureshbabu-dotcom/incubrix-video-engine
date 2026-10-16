
from pathlib import Path

from app.video_renderer import render_video
from app.video_inspector import inspect_video


INPUT_VIDEO = Path("data/videos/287510_medium.mp4")

OUTPUTS = {
    "landscape": "data/output/forest_landscape_test.mp4",
    "portrait": "data/output/forest_portrait_test.mp4",
    "square": "data/output/forest_square_test.mp4",
}

EXPECTED_DIMENSIONS = {
    "landscape": (1920, 1080),
    "portrait": (1080, 1920),
    "square": (1080, 1080),
}


def main():
    if not INPUT_VIDEO.is_file():
        print("Input footage not found:", INPUT_VIDEO)
        print("Update INPUT_VIDEO to an existing MP4 in data/videos.")
        return

    print("Testing all output formats...")
    print("-" * 40)

    for format_name, output_name in OUTPUTS.items():
        print(f"\nRendering {format_name} format...")

        try:
            output_path = render_video(
                input_path=str(INPUT_VIDEO),
                output_path=output_name,
                format_name=format_name,
            )

            info = inspect_video(output_path)
            actual = (info["width"], info["height"])
            expected = EXPECTED_DIMENSIONS[format_name]

            print("Output:", output_path)
            print("Actual dimensions:", actual)
            print("Expected dimensions:", expected)

            if actual == expected:
                print("Result: PASSED")
            else:
                print("Result: FAILED — dimensions do not match")

        except (ValueError, RuntimeError) as error:
            print("Result: FAILED —", error)

    print("\nFormat tests finished.")


if __name__ == "__main__":
    main()
