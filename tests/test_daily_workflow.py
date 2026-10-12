"""Unit and integration tests for the structured 20-minute daily learning workflow,
phase transitions, streak calculations, and practice submissions.
"""

from datetime import datetime, timezone, timedelta
import pytest
from vocabmaster.db.connection import get_db
from vocabmaster.db import repository
from vocabmaster.importer.processor import import_vocabulary_file
from vocabmaster.session import manager as session_manager


def test_daily_20min_workflow_phase_transitions(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-daily-1", test_user["id"], "Daily Deck", target_language="en")

        # Import 2 words
        csv_data = "term,definition\nluminous,emitting light\neffervescent,vivacious and enthusiastic\n".encode("utf-8")
        import_vocabulary_file(conn, test_user["id"], "deck-daily-1", csv_data, "words.csv")

        # Start daily 20-minute session
        init = session_manager.start_or_resume_session(
            conn,
            user_id=test_user["id"],
            deck_id="deck-daily-1",
            session_type="daily_20min",
        )
        session = init["session"]
        assert session["session_type"] == "daily_20min"
        # Since cards are new, initial phase is new_words
        assert session["current_phase"] in ("new_words", "review")
        session_id = session["id"]

        # Study all cards in the initial phase
        ans1 = session_manager.submit_card_answer(conn, session_id, test_user["id"], rating=4)
        assert ans1["is_completed"] is False

        ans2 = session_manager.submit_card_answer(conn, session_id, test_user["id"], rating=5)
        # Finishing phase should trigger phase transition
        assert ans2["phase_transitioned"] is True
        # Next phase should be recall_test
        assert ans2["session"]["current_phase"] == "recall_test"

        # Advance through remaining phases
        adv_res = session_manager.advance_phase(conn, session_id, test_user["id"])
        # Should either advance to practice or complete
        assert adv_res["session"]["current_phase"] in ("practice", "completed")

        if not adv_res["is_completed"]:
            adv_final = session_manager.advance_phase(conn, session_id, test_user["id"])
            assert adv_final["is_completed"] is True
            assert adv_final["session"]["status"] == "COMPLETED"


def test_streak_calculation(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        today = datetime.now(timezone.utc).date()
        day1 = (today - timedelta(days=2)).isoformat()
        day2 = (today - timedelta(days=1)).isoformat()
        day3 = today.isoformat()

        # Record study logs for 3 consecutive days
        repository.record_study_activity(conn, test_user["id"], day1, "en", 600, 15, 5)
        repository.record_study_activity(conn, test_user["id"], day2, "en", 750, 20, 5)
        repository.record_study_activity(conn, test_user["id"], day3, "en", 900, 25, 5)

        streak = repository.get_user_streak(conn, test_user["id"], "en")
        assert streak["current_streak"] == 3
        assert streak["longest_streak"] == 3
        assert streak["active_days_count"] == 3


def test_practice_submission_and_history(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-prac-1", test_user["id"], "Practice Deck", target_language="en")
        csv_data = "term,definition\nserendipity,finding good things by chance\n".encode("utf-8")
        import_vocabulary_file(conn, test_user["id"], "deck-prac-1", csv_data, "words.csv")

        items = repository.list_vocab_items(conn, deck_id="deck-prac-1", user_id=test_user["id"])
        vocab_id = items[0]["id"]

        # Record writing practice submission
        sub_id = "sub-123"
        submission = repository.create_practice_submission(
            conn=conn,
            sub_id=sub_id,
            user_id=test_user["id"],
            vocab_id=vocab_id,
            practice_type="sentence_writing",
            prompt="Make a sentence with 'serendipity'",
            user_text="Finding this book was sheer serendipity.",
            model_answer="It was serendipity that brought us together.",
            self_assessment_score=5,
        )

        assert submission["id"] == sub_id
        assert submission["user_text"] == "Finding this book was sheer serendipity."
        assert submission["self_assessment_score"] == 5

        # List submissions
        history = repository.list_practice_submissions(conn, test_user["id"])
        assert len(history) == 1
        assert history[0]["vocab_term"] == "serendipity"
        assert history[0]["practice_type"] == "sentence_writing"
