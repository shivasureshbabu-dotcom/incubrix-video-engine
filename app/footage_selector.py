
def calculate_diversity_score(
    similarity_scores: list[float],
) -> float:
    """Return a diversity score from 0.0 to 1.0.

    Higher similarity means less diversity.
    """

    if not similarity_scores:
        return 1.0

    # Keep similarity values within the valid range.
    scores = [
        max(0.0, min(1.0, float(score)))
        for score in similarity_scores
    ]

    # Compare against the most similar previously selected clip.
    highest_similarity = max(scores)

    # Convert similarity into a diversity score.
    return round(1.0 - highest_similarity, 3)





def calculate_clip_score(
    relevance_score: float,
    diversity_score: float,
    novelty_score: float = 0.5,
) -> float:
    """Calculate an overall score for a candidate video clip."""

    for name, score in [
        ("relevance_score", relevance_score),
        ("diversity_score", diversity_score),
        ("novelty_score", novelty_score),
    ]:
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"{name} must be between 0.0 and 1.0")

    total = (
        0.65 * relevance_score
        + 0.25 * diversity_score
        + 0.10 * novelty_score
    )

    return round(total, 3)




def is_clip_acceptable(
    relevance_score: float,
    minimum_relevance: float = 0.4,
) -> bool:
    """Reject clips that are not relevant enough to the narration."""

    if not 0.0 <= relevance_score <= 1.0:
        raise ValueError("relevance_score must be between 0.0 and 1.0")

    if not 0.0 <= minimum_relevance <= 1.0:
        raise ValueError("minimum_relevance must be between 0.0 and 1.0")

    return relevance_score >= minimum_relevance



def evaluate_clip(
    relevance_score: float,
    diversity_score: float,
    novelty_score: float = 0.5,
    minimum_relevance: float = 0.4,
) -> dict:
    """Score a candidate clip and decide whether it is acceptable."""

    accepted = is_clip_acceptable(
        relevance_score,
        minimum_relevance,
    )

    score = calculate_clip_score(
        relevance_score,
        diversity_score,
        novelty_score,
    )

    return {
        "accepted": accepted,
        "score": score,
        "relevance_score": relevance_score,
        "diversity_score": diversity_score,
        "novelty_score": novelty_score,
    }


def select_best_clip(candidates: list[dict], minimum_relevance: float = 0.4):
    """Select the highest-scoring acceptable candidate clip."""

    evaluated_candidates = []

    for candidate in candidates:
        result = evaluate_clip(
            relevance_score=candidate["relevance_score"],
            diversity_score=candidate["diversity_score"],
            novelty_score=candidate.get("novelty_score", 0.5),
            minimum_relevance=minimum_relevance,
        )

        evaluated_candidates.append({
            **candidate,
            **result,
        })

    acceptable_candidates = [
        clip for clip in evaluated_candidates
        if clip["accepted"]
    ]

    if not acceptable_candidates:
        return None

    return max(
        acceptable_candidates,
        key=lambda clip: clip["score"],
    )

from app.footage_metadata import validate_footage_metadata



def select_best_licensed_clip(
    candidates: list[dict],
    minimum_relevance: float = 0.4,
):
    """Select the best acceptable clip with valid licensing metadata."""

    valid_candidates = []

    for candidate in candidates:
        try:
            validated = validate_footage_metadata(candidate)
        except ValueError:
            continue

        valid_candidates.append(validated)

    if not valid_candidates:
        return None

    return select_best_clip(
        valid_candidates,
        minimum_relevance=minimum_relevance,
    )

