
from app.pixabay_client import search_pixabay_videos
from app.footage_selector import select_best_licensed_clip


def find_best_pixabay_clip(
    query: str,
    relevance_score: float,
    diversity_score: float,
    novelty_score: float = 0.5,
):
    """Search Pixabay and select the best candidate with valid metadata."""

    videos = search_pixabay_videos(query)

    candidates = []

    for video in videos:
        candidates.append({
            **video,
            "license_name": "Pixabay Content License",
            "license_url": "https://pixabay.com/service/license/",
            "relevance_score": relevance_score,
            "diversity_score": diversity_score,
            "novelty_score": novelty_score,
        })

    return select_best_licensed_clip(candidates)
