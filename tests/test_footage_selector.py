from app.footage_selector import (
    calculate_diversity_score,
    calculate_clip_score,
    is_clip_acceptable,
    evaluate_clip,
    select_best_clip,
    select_best_licensed_clip,
)



def test_no_similar_clips_returns_full_diversity():
    assert calculate_diversity_score([]) == 1.0


def test_unrelated_clip_has_high_diversity():
    assert calculate_diversity_score([0.1]) == 0.9


def test_very_similar_clip_has_low_diversity():
    assert calculate_diversity_score([0.95]) == 0.05


def test_uses_highest_similarity():
    assert calculate_diversity_score([0.2, 0.8, 0.4]) == 0.2


def test_similarity_is_clamped_to_valid_range():
    assert calculate_diversity_score([1.5]) == 0.0
    assert calculate_diversity_score([-0.5]) == 1.0


def test_calculate_clip_score():
    score = calculate_clip_score(0.9, 0.8, 0.7)
    assert score == 0.855


def test_calculate_clip_score_uses_default_novelty():
    score = calculate_clip_score(1.0, 1.0)
    assert score == 0.95


def test_calculate_clip_score_rejects_invalid_values():
    import pytest

    with pytest.raises(ValueError):
        calculate_clip_score(1.2, 0.5, 0.5)


def test_relevant_clip_is_accepted():
    assert is_clip_acceptable(0.8) is True


def test_irrelevant_clip_is_rejected():
    assert is_clip_acceptable(0.2) is False


def test_clip_at_minimum_threshold_is_accepted():
    assert is_clip_acceptable(0.4) is True


def test_invalid_relevance_is_rejected():
    import pytest

    with pytest.raises(ValueError):
        is_clip_acceptable(1.5)

def test_evaluate_clip_accepts_relevant_clip():
    result = evaluate_clip(0.9, 0.8, 0.7)

    assert result["accepted"] is True
    assert result["score"] == 0.855


def test_evaluate_clip_rejects_irrelevant_clip():
    result = evaluate_clip(0.2, 0.8, 0.7)

    assert result["accepted"] is False


def test_evaluate_clip_returns_all_scores():
    result = evaluate_clip(0.9, 0.8, 0.7)

    assert result["relevance_score"] == 0.9
    assert result["diversity_score"] == 0.8
    assert result["novelty_score"] == 0.7

    
def test_evaluate_clip_rejects_low_relevance_even_with_high_diversity():
    result = evaluate_clip(
        relevance_score=0.3,
        diversity_score=1.0,
        novelty_score=1.0,
        minimum_relevance=0.4,
    )

    assert result["accepted"] is False
    assert result["score"] > 0.5


def test_select_best_clip_returns_highest_scoring_acceptable_clip():
    candidates = [
        {
            "clip_id": "clip_A",
            "relevance_score": 0.8,
            "diversity_score": 0.7,
            "novelty_score": 0.5,
        },
        {
            "clip_id": "clip_B",
            "relevance_score": 0.9,
            "diversity_score": 0.9,
            "novelty_score": 0.8,
        },
    ]

    result = select_best_clip(candidates)

    assert result["clip_id"] == "clip_B"
    assert result["accepted"] is True


def test_select_best_clip_ignores_irrelevant_candidates():
    candidates = [
        {
            "clip_id": "irrelevant",
            "relevance_score": 0.2,
            "diversity_score": 1.0,
            "novelty_score": 1.0,
        },
        {
            "clip_id": "relevant",
            "relevance_score": 0.7,
            "diversity_score": 0.6,
            "novelty_score": 0.5,
        },
    ]

    result = select_best_clip(candidates)

    assert result["clip_id"] == "relevant"


def test_select_best_clip_returns_none_when_all_are_irrelevant():
    candidates = [
        {
            "clip_id": "clip_A",
            "relevance_score": 0.1,
            "diversity_score": 0.9,
        },
        {
            "clip_id": "clip_B",
            "relevance_score": 0.3,
            "diversity_score": 0.8,
        },
    ]

    result = select_best_clip(candidates)

    assert result is None


def test_select_best_licensed_clip_returns_valid_clip():
    candidates = [
        {
            "clip_id": "clip_licensed",
            "source_name": "Example Provider",
            "source_url": "https://example.com/video/1",
            "license_name": "Example License",
            "license_url": "https://example.com/license",
            "creator": "Example Creator",
            "relevance_score": 0.9,
            "diversity_score": 0.8,
            "novelty_score": 0.7,
        }
    ]

    result = select_best_licensed_clip(candidates)

    assert result["clip_id"] == "clip_licensed"
    assert result["accepted"] is True
    assert result["metadata_valid"] is True


def test_select_best_licensed_clip_skips_missing_license():
    candidates = [
        {
            "clip_id": "clip_missing_license",
            "source_name": "Example Provider",
            "source_url": "https://example.com/video/1",
            "creator": "Example Creator",
            "relevance_score": 0.9,
            "diversity_score": 0.8,
        }
    ]

    result = select_best_licensed_clip(candidates)

    assert result is None


def test_select_best_licensed_clip_skips_irrelevant_clip():
    candidates = [
        {
            "clip_id": "clip_irrelevant",
            "source_name": "Example Provider",
            "source_url": "https://example.com/video/1",
            "license_name": "Example License",
            "license_url": "https://example.com/license",
            "creator": "Example Creator",
            "relevance_score": 0.2,
            "diversity_score": 0.9,
            "novelty_score": 1.0,
        }
    ]

    result = select_best_licensed_clip(candidates)

    assert result is None


def test_select_best_licensed_clip_chooses_highest_score():
    candidates = [
        {
            "clip_id": "clip_A",
            "source_name": "Example Provider",
            "source_url": "https://example.com/video/a",
            "license_name": "Example License",
            "license_url": "https://example.com/license",
            "creator": "Creator A",
            "relevance_score": 0.7,
            "diversity_score": 0.6,
            "novelty_score": 0.5,
        },
        {
            "clip_id": "clip_B",
            "source_name": "Example Provider",
            "source_url": "https://example.com/video/b",
            "license_name": "Example License",
            "license_url": "https://example.com/license",
            "creator": "Creator B",
            "relevance_score": 0.95,
            "diversity_score": 0.9,
            "novelty_score": 0.8,
        },
    ]

    result = select_best_licensed_clip(candidates)

    assert result["clip_id"] == "clip_B"
    assert result["accepted"] is True
    assert result["metadata_valid"] is True
