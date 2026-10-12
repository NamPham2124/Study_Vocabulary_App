"""Unit tests for the SM-2+ Spaced Repetition System algorithm."""

from datetime import datetime, timezone
import pytest
from vocabmaster.srs.algorithm import CardState, compute_srs_update


def test_srs_new_card_failure():
    # Failing a new card (rating 1)
    res = compute_srs_update(
        state=CardState.NEW,
        step_index=0,
        repetition_count=0,
        interval_days=0.0,
        ease_factor=2.5,
        rating=1,
    )
    assert res.state == CardState.LEARNING
    assert res.repetition_count == 0
    assert res.interval_days < 1.0
    assert res.ease_factor == 2.3  # Penalty of 0.20


def test_srs_new_card_graduation():
    # Good recall on a new card (rating 4) graduates directly
    res = compute_srs_update(
        state=CardState.NEW,
        step_index=0,
        repetition_count=0,
        interval_days=0.0,
        ease_factor=2.5,
        rating=4,
    )
    assert res.state == CardState.REVIEW
    assert res.repetition_count == 1
    assert res.interval_days == 1.0


def test_srs_review_card_progression():
    # Repetition 1 -> Repetition 2
    res2 = compute_srs_update(
        state=CardState.REVIEW,
        step_index=0,
        repetition_count=1,
        interval_days=1.0,
        ease_factor=2.5,
        rating=4,
    )
    assert res2.repetition_count == 2
    assert res2.interval_days == 6.0

    # Repetition 2 -> Repetition 3 (interval = 6.0 * EF)
    res3 = compute_srs_update(
        state=CardState.REVIEW,
        step_index=0,
        repetition_count=2,
        interval_days=6.0,
        ease_factor=2.5,
        rating=4,
    )
    assert res3.repetition_count == 3
    assert res3.interval_days == 15.0  # 6 * 2.5


def test_srs_review_card_lapse():
    # Mature review card failed (rating 0)
    res = compute_srs_update(
        state=CardState.REVIEW,
        step_index=0,
        repetition_count=5,
        interval_days=30.0,
        ease_factor=2.5,
        rating=0,
    )
    assert res.state == CardState.RELEARNING
    assert res.repetition_count == 0
    assert res.interval_days < 1.0
    assert res.ease_factor == 2.3


def test_srs_minimum_ease_factor_boundary():
    # Repeated failures cannot drop ease factor below min (1.3)
    ef = 1.4
    res = compute_srs_update(
        state=CardState.REVIEW,
        step_index=0,
        repetition_count=1,
        interval_days=1.0,
        ease_factor=ef,
        rating=0,
    )
    assert res.ease_factor == 1.3  # clamped to minimum


def test_srs_invalid_rating():
    with pytest.raises(ValueError, match="Rating must be between 0 and 5"):
        compute_srs_update(
            state=CardState.REVIEW,
            step_index=0,
            repetition_count=1,
            interval_days=1.0,
            ease_factor=2.5,
            rating=6,
        )
