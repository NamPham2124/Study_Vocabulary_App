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


def test_vocab_study_history_and_srs_distribution(temp_db_path, test_user):
    from vocabmaster.db.connection import get_db
    from vocabmaster.db import repository
    from vocabmaster.srs.scheduler import review_card
    import uuid

    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck_hist_1", test_user["id"], "History Test Deck")
        vocab = repository.create_vocab_item(
            conn,
            {
                "id": "v_hist_1",
                "deck_id": "deck_hist_1",
                "user_id": test_user["id"],
                "language": "en",
                "term": "ubiquitous",
                "definition": "phổ biến, có mặt khắp nơi",
                "ipa": "/juːˈbɪk.wɪ.təs/",
            },
        )
        card = repository.create_srs_card(
            conn,
            {
                "id": "c_hist_1",
                "vocab_id": "v_hist_1",
                "deck_id": "deck_hist_1",
                "user_id": test_user["id"],
                "state": "NEW",
            },
        )

        # Create session
        sess = repository.create_session(
            conn,
            {
                "id": "sess_hist_1",
                "user_id": test_user["id"],
                "title": "History Session",
                "card_ids_queue": ["c_hist_1"],
            },
        )

        # Log 1: Incorrect attempt (Chưa thuộc, rating = 1)
        review_card(conn, "c_hist_1", test_user["id"], rating=1)
        repository.record_card_log(
            conn,
            {
                "id": str(uuid.uuid4()),
                "session_id": "sess_hist_1",
                "card_id": "c_hist_1",
                "user_id": test_user["id"],
                "rating": 1,
                "exercise_type": "quiz_hide_term",
                "user_response": "ubiqitous",
                "is_correct": False,
                "scheduled_next_interval": 0.005,
            },
        )

        # Log 2: Correct attempt (Thuộc, rating = 4)
        review_card(conn, "c_hist_1", test_user["id"], rating=4)
        repository.record_card_log(
            conn,
            {
                "id": str(uuid.uuid4()),
                "session_id": "sess_hist_1",
                "card_id": "c_hist_1",
                "user_id": test_user["id"],
                "rating": 4,
                "exercise_type": "quiz_hide_meaning",
                "user_response": "phổ biến",
                "is_correct": True,
                "scheduled_next_interval": 1.0,
            },
        )

        # Query history
        hist = repository.get_vocab_study_history(conn, "v_hist_1", test_user["id"])
        assert hist["vocab_id"] == "v_hist_1"
        assert hist["term"] == "ubiquitous"
        assert hist["total_attempts"] == 2
        assert hist["correct_count"] == 1
        assert hist["incorrect_count"] == 1
        assert hist["retention_rate"] == 50.0
        assert len(hist["history"]) == 2

        # Query SRS distribution
        dist = repository.get_srs_distribution(conn, test_user["id"], learning_language="en")
        assert dist["total_cards"] >= 1
        assert dist["box_1_day"] >= 1
        assert dist["lapsed_count"] >= 1


def test_lapsed_and_reinforcement_cards_query(temp_db_path, test_user):
    from vocabmaster.db.connection import get_db
    from vocabmaster.db import repository
    from vocabmaster.srs.scheduler import review_card

    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck_reinf_1", test_user["id"], "Reinforce Test Deck")
        vocab = repository.create_vocab_item(
            conn,
            {
                "id": "v_reinf_1",
                "deck_id": "deck_reinf_1",
                "user_id": test_user["id"],
                "language": "en",
                "term": "ephemeral",
                "definition": "phù du",
                "ipa": "/ɪˈfem.ər.əl/",
            },
        )
        card = repository.create_srs_card(
            conn,
            {
                "id": "c_reinf_1",
                "vocab_id": "v_reinf_1",
                "deck_id": "deck_reinf_1",
                "user_id": test_user["id"],
                "state": "REVIEW",
                "interval_days": 10.0,
                "due_date": "2099-01-01T00:00:00Z",  # In the future!
            },
        )

        # Fail card to create lapse
        review_card(conn, "c_reinf_1", test_user["id"], rating=1)

        lapsed = repository.get_lapsed_or_weak_cards(conn, test_user["id"], learning_language="en")
        assert len(lapsed) >= 1
        assert lapsed[0]["id"] == "c_reinf_1"

        reinf = repository.get_reinforcement_cards(conn, test_user["id"], deck_id="deck_reinf_1")
        assert len(reinf) >= 1
        assert reinf[0]["id"] == "c_reinf_1"
