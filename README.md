# IncuBrix Script and Voiceover to B-roll Video Engine

## 1. Project Overview

The IncuBrix Video Engine is a Python-based project for processing narration, preparing captions, selecting stock footage, and creating videos in standard aspect ratios.

The current prototype includes audio analysis, basic silence and emphasis detection, Pixabay footage search and download, video inspection, video rendering, audio merging, subtitle rendering, and output metadata reports.

Some features are still prototypes. Semantic footage matching, precise speech-to-caption alignment, complete automated orchestration, and production deployment require further development.

## 2. Main Features

- Audio analysis for WAV files
- Basic silence and loudness-based emphasis detection
- Scene timing generation
- Pixabay stock video search and download
- Footage metadata validation
- Footage diversity and relevance scoring helpers
- Video inspection using FFprobe
- Landscape, portrait, and square video rendering
- Voiceover merging using FFmpeg
- Subtitle generation and burning
- JSON video manifest and output report
- Automated tests using pytest

## 3. Technology Stack

- Python
- FastAPI
- FFmpeg and FFprobe
- Pixabay API
- gTTS
- pytest

## 4. Requirements

Install the following before running the project:

- Python
- FFmpeg, including FFprobe
- A Pixabay API key for stock footage search

## 5. Setup

Open a terminal in the project root.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root containing:

```text
PIXABAY_API_KEY=your_pixabay_api_key
```

Replace the placeholder with your own API key. Do not commit `.env` or expose your key.

If FFmpeg is not on your system PATH, set the paths in your current PowerShell session:

```powershell
$env:FFMPEG_PATH = "C:\path\to\ffmpeg.exe"
$env:FFPROBE_PATH = "C:\path\to\ffprobe.exe"
```

Replace those example paths with the actual locations on your computer.

## 6. Run the API

From the project root, run:

```powershell
python -m uvicorn app.main:app --reload
```

Open the API documentation at:

http://127.0.0.1:8000/docs

Check the health endpoint at:

http://127.0.0.1:8000/health

## 7. Useful Scripts

Run the automated tests:

```powershell
python -m pytest -v
```

Search for and download stock footage:

```powershell
python run_footage_workflow.py
```

Check downloaded footage:

```powershell
python check_downloaded_footage.py
```

Generate captions:

```powershell
python create_captions.py
```

Merge narration with video:

```powershell
python check_real_voiceover.py
```

Render captions:

```powershell
python check_caption_renderer.py
```

Validate the final video:

```powershell
python check_final_video.py
```

Create the video manifest:

```powershell
python create_video_manifest.py
```

Generate the output report:

```powershell
python create_output_report.py
```

Run the final check scripts:

```powershell
python run_final_checks.py
```

## 8. Output Files

Generated files are stored under `data/output/`, including:

- `forest_final.mp4`
- `forest_captioned.mp4`
- `forest_captions.srt`
- `video_manifest.json`
- `output_report.json`

Downloaded stock footage is stored under `data/videos/`.

## 9. Current Limitations

- Caption timings are estimates and are not yet precisely aligned to spoken words.
- Emphasis detection is based on audio loudness, not semantic understanding.
- Diversity scoring uses supplied similarity values; actual visual similarity analysis is not yet integrated.
- Footage selection does not yet perform complete semantic matching against narration.
- Metadata validation checks required fields and URL structure, not actual license permissions.
- The current prototype does not yet implement the full production job queue, idempotency, recovery, and deployment requirements.

## 10. Testing

Run:

```powershell
python -m pytest -v
```

Record the latest test results in the project report before submission.

## 11. License and Attribution

Follow the applicable stock footage license terms. Retain each clip's source URL, creator, license name, and license URL. Verify permissions for the specific assets before distributing the finished video.
