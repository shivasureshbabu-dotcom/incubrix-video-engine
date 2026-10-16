
from app.footage_selector import (
    calculate_diversity_score,
    calculate_clip_score,
    evaluate_clip,
    select_best_clip,
)


def main():
    print("Testing Footage Diversity Guard")
    print("-" * 40)

    # Lower similarity means greater diversity.
    similar_clip_score = calculate_diversity_score([0.95, 0.90])
    different_clip_score = calculate_diversity_score([0.20, 0.35])
    first_clip_score = calculate_diversity_score([])

    print("Highly similar footage:", similar_clip_score)
    print("More diverse footage:", different_clip_score)
    print("First clip diversity:", first_clip_score)

    assert similar_clip_score < different_clip_score
    assert first_clip_score == 1.0

    # Test the weighted clip score.
    score = calculate_clip_score(
        relevance_score=0.90,
        diversity_score=0.80,
        novelty_score=0.70,
    )
    print("Weighted clip score:", score)

    assert score == 0.855

    # A clip below the relevance threshold should be rejected.
    rejected = evaluate_clip(
        relevance_score=0.20,
        diversity_score=1.0,
        novelty_score=1.0,
    )
    print("Low-relevance clip accepted:", rejected["accepted"])

    assert rejected["accepted"] is False

    # The selector should prefer the higher-scoring acceptable clip.
    candidates = [
        {
            "clip_id": "clip_A",
            "relevance_score": 0.90,
            "diversity_score": 0.30,
            "novelty_score": 0.50,
        },
        {
            "clip_id": "clip_B",
            "relevance_score": 0.85,
            "diversity_score": 0.90,
            "novelty_score": 0.80,
        },
        {
            "clip_id": "clip_C",
            "relevance_score": 0.20,
            "diversity_score": 1.00,
            "novelty_score": 1.00,
        },
    ]

    best_clip = select_best_clip(candidates)

    print("Selected clip:", best_clip["clip_id"])
    assert best_clip["clip_id"] == "clip_B"

    print("\nAll diversity guard checks passed!")


if __name__ == "__main__":
    main()
