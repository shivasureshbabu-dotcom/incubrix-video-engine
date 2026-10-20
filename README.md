# IncuBrix Script and Voiceover to B-roll Video Engine

## 1. Project Overview

The IncuBrix Video Engine is a Python-based application for processing narration, preparing captions, selecting stock footage, and generating videos in standard aspect ratios.

The project includes a FastAPI backend and a React + Vite frontend. The backend handles video processing and API requests, while the frontend provides the user interface for submitting scripts, monitoring jobs, previewing videos, and downloading completed MP4 files.

The current prototype includes audio analysis, basic silence and emphasis detection, Pixabay footage search and download, video inspection, video rendering, audio merging, subtitle rendering, and output metadata reports.

Some features remain prototypes. Semantic footage matching, precise speech-to-caption alignment, complete automated orchestration, and production deployment require further development.

## 2. Main Features

- Audio analysis for WAV files
- Basic silence and loudness-based emphasis detection
- Scene timing generation
- Pixabay stock video search and download
- Footage metadata validation
- Footage diversity and relevance scoring helpers
- Video inspection using FFprobe
- Landscape (16:9), portrait (9:16), and square (1:1) video rendering
- Voiceover merging using FFmpeg
- Subtitle generation and burning
- JSON video manifest and output report
- FastAPI backend with interactive API documentation
- React + Vite frontend
- Script editor with character and word counts
- Creative direction and aspect ratio selection
- Video job submission and progress tracking
- Recent job list and job status reopening
- Video preview and MP4 download
- Optional WAV voiceover analysis
- Automated tests using pytest

## 3. Technology Stack

- Python
- FastAPI
- Uvicorn
- React
- Vite
- Node.js and npm
- FFmpeg and FFprobe
- Pixabay API
- gTTS
- pytest

## 4. Requirements

Install the following before running the application:

- Python compatible with the project's dependencies
- Node.js 20.19+ or 22.12+
- npm
- FFmpeg, including FFprobe
- A Pixabay API key for stock footage search
- Git, if you are cloning the project from a repository

Check that Python and Node.js are installed:

```powershell
python --version
node --version
npm --version
```

Check FFmpeg and FFprobe:

```powershell
ffmpeg -version
ffprobe -version
```

If these commands are not recognized, install the missing software or configure its location in your system PATH.

## 5. Project Structure

The expected local folder structure is:

```text
incubrix_video_engine_stage1/
├── .venv/
└── incubrix_video_engine/
    ├── app/
    ├── tests/
    ├── data/
    │   ├── videos/
    │   └── output/
    ├── frontend/
    │   ├── src/
    │   ├── package.json
    │   └── vite.config.js
    ├── requirements.txt
    ├── .env
    └── README.md
```

Your actual project may contain additional files and folders.

## 6. Backend Setup

### Step 1: Open the backend project folder

Open PowerShell and run:

```powershell
cd "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\incubrix_video_engine"
```

### Step 2: Create the Python virtual environment if needed

The existing project setup uses a virtual environment in the parent `incubrix_video_engine_stage1` folder.

If that environment already exists, skip this step.

Otherwise, create it from the parent folder:

```powershell
cd "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1"
python -m venv .venv
```

### Step 3: Install backend dependencies

Return to the backend project folder:

```powershell
cd "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\incubrix_video_engine"
```

Install the dependencies using the project's virtual environment:

```powershell
& "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

### Step 4: Configure the Pixabay API key

Create or update the `.env` file in the backend project root:

```text
PIXABAY_API_KEY=your_pixabay_api_key
```

Replace the placeholder with your actual API key.

Do not commit `.env` to version control, publish your key, or expose it in frontend code.

### Step 5: Configure FFmpeg paths if necessary

If FFmpeg and FFprobe are not available through your system PATH, set their locations in the current PowerShell session:

```powershell
$env:FFMPEG_PATH = "C:\path\to\ffmpeg.exe"
$env:FFPROBE_PATH = "C:\path\to\ffprobe.exe"
```

Replace the example paths with the actual executable locations. These variables apply to the current terminal session.

### Step 6: Start the backend API

From the backend project root, run:

```powershell
& "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload
```

Keep this terminal open while using the application.

The backend should be available at:

- API base URL: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Readiness check, if implemented: http://127.0.0.1:8000/ready

The available routes and response formats can be inspected through `/docs`.

## 7. Frontend Setup

The frontend is a React application powered by Vite.

### Step 1: Open a second PowerShell terminal

Do not close the backend terminal. Open a separate terminal for the frontend.

Navigate to the frontend folder:

```powershell
cd "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\incubrix_video_engine\frontend"
```

**Important:** Run the npm commands from this `frontend` folder, where `package.json` is located.

### Step 2: Install frontend dependencies

```powershell
npm install
```

### Step 3: Start the frontend development server

```powershell
npm run dev
```

Vite will print the local URL in the terminal. It is usually:

http://127.0.0.1:5173

Open that URL in your browser.

Keep both the backend and frontend terminals open while using the application.

## 8. Run the Full Application

Follow these steps whenever you want to run IncuBrix locally.

### Terminal 1 — Backend

```powershell
cd "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\incubrix_video_engine"
& "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload
```

### Terminal 2 — Frontend

```powershell
cd "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\incubrix_video_engine\frontend"
npm run dev
```

### Browser

Open:

http://127.0.0.1:5173

Check the backend API separately at:

http://127.0.0.1:8000/docs

The frontend's Vite development configuration is expected to proxy `/api`, `/health`, and `/ready` requests to the backend at `http://127.0.0.1:8000`. If the frontend cannot connect, check `frontend/vite.config.js` and the backend routes.

## 9. Useful Backend Scripts

Run these commands from the backend project root, using the project's virtual environment.

### Run automated tests

```powershell
& "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\.venv\Scripts\python.exe" -m pytest -v
```

### Search for and download stock footage

```powershell
python run_footage_workflow.py
```

### Check downloaded footage

```powershell
python check_downloaded_footage.py
```

### Generate captions

```powershell
python create_captions.py
```

### Merge narration with video

```powershell
python check_real_voiceover.py
```

### Render captions

```powershell
python check_caption_renderer.py
```

### Validate the final video

```powershell
python check_final_video.py
```

### Create the video manifest

```powershell
python create_video_manifest.py
```

### Generate the output report

```powershell
python create_output_report.py
```

### Run the final check scripts

```powershell
python run_final_checks.py
```

These commands assume the listed scripts exist in the project root. If a script is missing or has a different location, check the actual project files before running it. Use the virtual environment's Python executable when running scripts to ensure the correct dependencies are available.

## 10. Frontend Features

The frontend provides:

- Script entry and editing
- Character and word counts
- Landscape, portrait, and square output options
- Creative direction selection
- Job submission and progress updates
- Recent job history
- Job status reopening
- Video preview and MP4 download
- Optional WAV voiceover analysis
- Backend health information and error messages

The frontend communicates with the backend API. Video generation and processing are handled by the backend rather than directly by the browser.

## 11. API Endpoints

The frontend is expected to use the following endpoints, subject to the routes implemented by the current backend:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check backend health |
| POST | `/api/v1/jobs` | Submit a video-generation job |
| GET | `/api/v1/jobs?limit=6` | Retrieve recent jobs |
| GET | `/api/v1/jobs/{job_id}` | Retrieve job status and details |
| GET | `/api/v1/jobs/{job_id}/video` | Retrieve the completed MP4 |
| POST | `/api/v1/audio/analyze` | Analyze an uploaded WAV file |

For exact request bodies, parameters, and response formats, use the running backend's `/docs` page.

## 12. Output Files

Generated files are expected under `data/output/`, including:

- `forest_final.mp4`
- `forest_captioned.mp4`
- `forest_captions.srt`
- `video_manifest.json`
- `output_report.json`

Downloaded stock footage is expected under `data/videos/`.

The actual filenames and locations depend on the scripts and configuration used for each run.

## 13. Troubleshooting

### Error: `ModuleNotFoundError: No module named 'app'`

Make sure PowerShell is in the backend project root:

```powershell
cd "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\incubrix_video_engine"
```

Then start Uvicorn using:

```powershell
& "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload
```

### Error: `npm` cannot find `package.json`

Navigate to the frontend folder before running npm:

```powershell
cd "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\incubrix_video_engine\frontend"
npm install
npm run dev
```

### Frontend says the backend is unavailable

1. Confirm the backend terminal is still running.
2. Open `http://127.0.0.1:8000/health`.
3. Check the frontend proxy configuration in `frontend/vite.config.js`.
4. Check the backend logs for errors.

### FFmpeg or FFprobe is not recognized

Install FFmpeg and ensure the executables are available through PATH, or set the appropriate paths for the current session.

### Pixabay footage search fails

Confirm that the API key is valid, the `.env` file is in the expected backend location, and the backend loads the key correctly.

### Tests fail

Run the tests with verbose output:

```powershell
& "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\.venv\Scripts\python.exe" -m pytest -v
```

Review the failing test and error message before changing the application code. Record the latest test results in the project report.

## 14. Current Limitations

- Caption timings are estimates and are not yet precisely aligned to spoken words.
- Emphasis detection is based on audio loudness, not semantic understanding.
- Diversity scoring uses supplied similarity values; actual visual similarity analysis is not yet integrated.
- Footage selection does not yet perform complete semantic matching against narration.
- Metadata validation checks required fields and URL structure, not actual license permissions.
- The current prototype does not yet implement all production job-queue, idempotency, recovery, and deployment requirements.

## 15. Testing

Run the backend test suite from the backend project root:

```powershell
& "$env:USERPROFILE\Downloads\incubrix_video_engine_stage1\.venv\Scripts\python.exe" -m pytest -v
```

Before submission:

1. Confirm the backend starts without errors.
2. Confirm the API documentation is accessible.
3. Confirm the frontend starts without errors.
4. Confirm the frontend can communicate with the backend.
5. Test video job submission, status updates, preview, and download.
6. Run the automated tests and record the actual results.
7. Check that required output files are generated.

Do not report tests as passing unless they have completed successfully.

## 16. License and Attribution

Follow the applicable stock footage license terms. Retain each clip's source URL, creator, license name, and license URL. Verify permissions for the specific assets before distributing the finished video.

## 17. Security Notes

- Never commit API keys, tokens, passwords, or private environment files.
- Keep third-party API keys in the backend environment.
- Do not expose private keys in frontend code or public repositories.
- Configure CORS appropriately before deploying the backend.
- Use secure production configuration before making the API publicly accessible.

## 18. Local Development URLs

| Component | URL |
|---|---|
| Frontend | http://127.0.0.1:5173 |
| Backend API | http://127.0.0.1:8000 |
| API documentation | http://127.0.0.1:8000/docs |
| Backend health | http://127.0.0.1:8000/health |
