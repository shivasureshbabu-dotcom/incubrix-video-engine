# Sources, Services, and Attribution

## 1. Stock Footage Provider

**Provider:** Pixabay

- Website: https://pixabay.com/
- Video API documentation: https://pixabay.com/api/docs/
- Content license: https://pixabay.com/service/license/

The prototype uses the Pixabay video API to search for stock footage and download MP4 files.

### Sample Footage Record

The current sample manifest references this clip:

- Clip ID: `287510`
- Creator: `Thamnguyen_TBVN`
- Source page: https://pixabay.com/videos/id-287510/
- License information: https://pixabay.com/service/license/

This is a recorded source reference. Verify the clip's current availability and applicable license terms before redistributing it or using it in a public demonstration.

## 2. Python Libraries

The project uses these external packages:

- FastAPI — https://fastapi.tiangolo.com/
- Uvicorn — https://www.uvicorn.org/
- Requests — https://requests.readthedocs.io/
- python-dotenv — https://saurabh-kumar.com/python-dotenv/
- gTTS — https://gtts.readthedocs.io/
- pytest — https://docs.pytest.org/

Consult each project's documentation for usage details and license terms.

## 3. Video Processing Tools

- FFmpeg: https://ffmpeg.org/
- FFprobe documentation: https://ffmpeg.org/ffprobe.html

FFmpeg is used to render videos, merge narration, and burn subtitles. FFprobe is used to inspect video duration, dimensions, and audio streams.

## 4. API and Framework Documentation

- Python: https://docs.python.org/3/
- FastAPI: https://fastapi.tiangolo.com/
- Pixabay API: https://pixabay.com/api/docs/

## 5. Footage Attribution Policy

For every stock clip included in a final video, retain:

1. Provider name
2. Original source page URL
3. Creator name or account
4. Applicable license name
5. License information URL
6. Local filename or asset identifier

Check the applicable terms for each specific asset. Recording a license name and URL does not itself prove that the asset's use is authorized.

## 6. AI-Assisted Development

AI assistance was used during development for explanations, code drafting, debugging guidance, test ideas, and documentation drafting.

Review and test all generated code before submission. Describe the specific AI tools and the actual assistance used in `AI_USE.md`.
