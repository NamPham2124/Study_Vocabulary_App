"""Unit tests for recoverable daily learning sessions and crash resilience."""

import pytest
from vocabmaster.db.connection import get_db
from vocabmaster.db import repository
from vocabmaster.importer.processor import import_vocabulary_file
from vocabmaster.session import manager as session_manager


def setup_sample_deck_and_cards(conn, user_id, count=5):
    deck = repository.create_deck(conn, "deck-sess-1", user_id, "Session Test Deck")
    csv_rows = ["term,definition"]
    for i in range(1, count + 1):
        csv_rows.append(f"word{i},meaning{i}")
    csv_content = "\n".join(csv_rows).encode("utf-8")
    import_vocabulary_file(conn, user_id, "deck-sess-1", csv_content, "words.csv")
    return deck


def test_session_creation_and_step_progression(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        setup_sample_deck_and_cards(conn, test_user["id"], count=3)
        res = session_manager.start_or_resume_session(conn, test_user["id"], "deck-sess-1")

        assert res["recovered"] is False
        session = res["session"]
        assert session["total_cards"] == 3
        assert session["current_index"] == 0
        assert session["status"] == "ACTIVE"

        card1 = session_manager.get_current_card(conn, session["id"], test_user["id"])
        assert card1 is not None
        assert card1["term"] == "word1"

        # Answer card 1 with Good (rating 4)
        ans1 = session_manager.submit_card_answer(
            conn, session["id"], test_user["id"], rating=4, time_spent_seconds=3.5
        )
        assert ans1["completed_cards"] == 1
        assert ans1["correct_count"] == 1
        assert ans1["is_completed"] is False

        # Verify next card is word2
        card2 = session_manager.get_current_card(conn, session["id"], test_user["id"])
        assert card2 is not None
        assert card2["term"] == "word2"


def test_session_recovery_after_simulated_crash(temp_db_path, test_user):
    session_id = None
    with get_db(temp_db_path) as conn:
        setup_sample_deck_and_cards(conn, test_user["id"], count=4)
        init_res = session_manager.start_or_resume_session(conn, test_user["id"], "deck-sess-1")
        session_id = init_res["session"]["id"]

        # User studies 2 cards
        session_manager.submit_card_answer(conn, session_id, test_user["id"], rating=4)
        session_manager.submit_card_answer(conn, session_id, test_user["id"], rating=5)

    # SIMULATE APP CRASH / PROCESS RESTART (New database connection context)
    with get_db(temp_db_path) as conn_recovered:
        # User opens the app again and clicks start or resume session
        resume_res = session_manager.start_or_resume_session(
            conn_recovered, test_user["id"], "deck-sess-1"
        )

        assert resume_res["recovered"] is True
        recovered_sess = resume_res["session"]
        assert recovered_sess["id"] == session_id
        assert recovered_sess["current_index"] == 2
        assert recovered_sess["completed_cards"] == 2
        assert recovered_sess["correct_count"] == 2

        # Current card should be card 3 (0-indexed 2)
        curr_card = resume_res["current_card"]
        assert curr_card is not None
        assert curr_card["current_index"] == 2
        assert curr_card["term"] == "word3"

        # Continue studying remaining cards to completion
        session_manager.submit_card_answer(conn_recovered, session_id, test_user["id"], rating=4)
        final_ans = session_manager.submit_card_answer(
            conn_recovered, session_id, test_user["id"], rating=4
        )

        assert final_ans["is_completed"] is True
        summary = session_manager.get_session_summary(conn_recovered, session_id, test_user["id"])
        assert summary["status"] == "COMPLETED"
        assert summary["completed_cards"] == 4
        assert summary["accuracy_percentage"] == 100.0


def test_failed_card_requeuing_in_session(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        setup_sample_deck_and_cards(conn, test_user["id"], count=2)
        init_res = session_manager.start_or_resume_session(conn, test_user["id"], "deck-sess-1")
        session_id = init_res["session"]["id"]

        # Answer card 1 with rating 1 (Failure)
        res1 = session_manager.submit_card_answer(
            conn, session_id, test_user["id"], rating=1, requeue_failed_cards=True
        )

        # Card was re-queued at the end of queue, so total_cards became 3
        assert res1["total_cards"] == 3
        assert res1["incorrect_count"] == 1

        # Next card is card 2
        card2 = session_manager.get_current_card(conn, session_id, test_user["id"])
        assert card2["term"] == "word2"
        session_manager.submit_card_answer(conn, session_id, test_user["id"], rating=4)

        # Third card is the re-queued card 1!
        card1_retry = session_manager.get_current_card(conn, session_id, test_user["id"])
        assert card1_retry["term"] == "word1"

        final_res = session_manager.submit_card_answer(conn, session_id, test_user["id"], rating=4)
        assert final_res["is_completed"] is True
