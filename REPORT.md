# IncuBrix Video Engine — Technical Report

## 1. Project Summary

The IncuBrix Script and Voiceover to B-roll Video Engine is a Python prototype that processes audio, searches for stock footage, renders videos, adds captions, and records output metadata.

The current implementation provides separate modules and scripts for several core video-processing operations. Full end-to-end orchestration and some assessment requirements remain in progress.

## 2. Architecture

The project is organized into these main components:

| Component | Responsibility |
|---|---|
| FastAPI application | Exposes API endpoints for supported operations |
| Audio analyzer | Analyzes WAV audio and detects quiet intervals |
| Emphasis detector | Identifies louder-than-average audio windows |
| Scene timing | Builds scene intervals from audio analysis results |
| Pixabay client | Searches stock footage through the Pixabay API |
| Video downloader | Downloads MP4 files from the Pixabay CDN |
| Footage selector | Scores candidates using relevance, diversity, and novelty values |
| Footage metadata | Checks required attribution fields and URL structure |
| Video inspector | Uses FFprobe to inspect video duration, streams, and dimensions |
| Video renderer | Uses FFmpeg to create landscape, portrait, and square output |
| Audio-video merger | Combines video footage and narration |
| Caption renderer | Burns SRT captions into a video |
| Output reporting | Generates JSON manifest and output reports |

## 3. Implemented Features

### Audio Processing
- WAV file analysis
- Basic silence detection
- Loudness-based emphasis detection
- Scene timing generation

### Stock Footage
- Pixabay video search
- MP4 download with URL and file-size restrictions
- Required metadata-field validation
- Relevance, diversity, and novelty scoring helpers

### Video Processing
- Video inspection through FFprobe
- Landscape output at 1920 × 1080
- Portrait output at 1080 × 1920
- Square output at 1080 × 1080
- Narration merging
- SRT caption rendering

### Validation and Reporting
- Automated unit tests
- Final video property validation
- JSON manifest creation
- Output video report generation

## 4. Custom Features

### Footage Diversity Guard

The selector calculates a diversity score using supplied similarity values:

`diversity = 1 - highest_similarity`

The clip score combines relevance, diversity, and novelty:

`score = 0.65 × relevance + 0.25 × diversity + 0.10 × novelty`

A relevance threshold prevents low-relevance candidates from being accepted by the selector.

These are initial scoring weights. Similarity and relevance are currently supplied as values rather than calculated automatically from video content and narration.

### Silence and Emphasis Detector

The audio analyzer detects quiet intervals in supported WAV files. The emphasis detector identifies short windows with higher-than-average loudness.

This is a signal-level heuristic. It does not understand the meaning of speech or reliably identify emotional emphasis.

## 5. Testing

The project previously completed **77 automated tests successfully**. Additional manual checks have also been run for:

- Audio-video merging
- Caption rendering
- Final video validation
- Pixabay footage download
- Landscape, portrait, and square rendering
- Footage diversity scoring
- Audio feature detection
- Output manifest and report generation

Before submission, rerun the full test suite and replace the earlier test count with the latest result.

## 6. Sample Output

The prototype generated a captioned forest video with these reported properties:

- Duration: 17.184 seconds
- Resolution: 1920 × 1080
- Audio stream: present

The caption timings are estimated and need more accurate speech alignment.

## 7. Licensing and Attribution

The manifest records footage source URLs, creator names, license names, and license URLs.

The current implementation validates required metadata fields and URL structure. It does not independently establish the actual rights for each clip. License terms and permissions must be checked for every asset before redistribution.

## 8. Known Limitations

1. Caption timestamps are manually estimated.
2. Semantic matching between narration and footage is not fully implemented.
3. Actual visual similarity analysis is not integrated into the diversity guard.
4. Audio emphasis detection uses loudness rather than semantic speech analysis.
5. The manifest currently uses a manually supplied footage entry rather than tracing all clips used in the rendered video.
6. Background job management, robust recovery, and idempotency need further implementation.
7. Docker Compose, a complete OpenAPI 3.1 deliverable, and a full end-to-end demo still need verification.

## 9. Future Improvements

- Integrate speech transcription and word-level alignment.
- Calculate footage relevance from narration and video content.
- Calculate visual similarity from sampled frames or embeddings.
- Track all selected clips through rendering and generate manifests automatically.
- Add background jobs, progress reporting, and idempotency.
- Add deployment configuration and complete integration tests.
- Prepare a demonstration showing the complete workflow.

## 10. Conclusion

The prototype demonstrates working components for audio analysis, stock footage retrieval, video rendering, narration merging, captions, and output validation. Further integration, semantic matching, licensing verification, and deployment work is needed to meet all assessment requirements.
