
import subprocess
import sys


SCRIPTS = [
    "check_final_video.py",
    "create_video_manifest.py",
    "create_output_report.py",
]


def main():
    print("=" * 50)
    print("INCuBRIX VIDEO ENGINE - FINAL CHECKS")
    print("=" * 50)

    for script in SCRIPTS:
        print(f"\nRunning: {script}")
        print("-" * 40)

        result = subprocess.run(
            [sys.executable, script],
            check=False,
        )

        if result.returncode != 0:
            print(f"\nFAILED: {script}")
            print("Fix this step before continuing.")
            return False

    print("\n" + "=" * 50)
    print("ALL FINAL CHECK SCRIPTS COMPLETED")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
