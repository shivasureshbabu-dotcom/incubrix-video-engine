
from unittest.mock import patch

from app.footage_pipeline import find_best_pixabay_clip


def test_pipeline_selects_best_acceptable_video():
    fake_videos = [
        {
            "clip_id": "101",
            "source_name": "Pixabay",
            "source_url": "https://example.com/video/101",
            "creator": "Creator A",
            "relevance_score": 0.7,
            "diversity_score": 0.6,
            "novelty_score": 0.5,
        },
        {
            "clip_id": "202",
            "source_name": "Pixabay",
            "source_url": "https://example.com/video/202",
            "creator": "Creator B",
            "relevance_score": 0.9,
            "diversity_score": 0.9,
            "novelty_score": 0.8,
        },
    ]

    with patch(
        "app.footage_pipeline.search_pixabay_videos",
        return_value=fake_videos,
    ):
        result = find_best_pixabay_clip(
            query="forest",
            relevance_score=0.9,
            diversity_score=0.8,
        )

    assert result is not None
    assert result["source_name"] == "Pixabay"
    assert result["license_name"] == "Pixabay Content License"
    assert result["metadata_valid"] is True


def test_pipeline_returns_none_when_no_videos_found():
    with patch(
        "app.footage_pipeline.search_pixabay_videos",
        return_value=[],
    ):
        result = find_best_pixabay_clip(
            query="forest",
            relevance_score=0.9,
            diversity_score=0.8,
        )

    assert result is None
