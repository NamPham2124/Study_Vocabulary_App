"""Unit and integration tests for Learning Paths management."""

import pytest
from vocabmaster.db.connection import get_db
from vocabmaster.db import repository
from vocabmaster.importer.processor import import_vocabulary_file


def test_learning_path_crud(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        # Create deck
        deck = repository.create_deck(conn, "deck-en-1", test_user["id"], "TOEIC Basic", target_language="en")

        # Create Path
        path = repository.create_learning_path(
            conn=conn,
            path_id="path-en-1",
            user_id=test_user["id"],
            name="TOEIC 800+ Journey",
            description="Intensive business English vocabulary",
            learning_language="en",
            objective="Score 850 in 3 months",
            daily_new_target=10,
            daily_time_goal=25,
            deck_ids=["deck-en-1"],
        )

        assert path["id"] == "path-en-1"
        assert path["name"] == "TOEIC 800+ Journey"
        assert path["learning_language"] == "en"
        assert path["daily_new_target"] == 10
        assert "deck-en-1" in path["linked_deck_ids"]

        # List paths
        paths = repository.list_learning_paths_for_user(conn, test_user["id"], learning_language="en")
        assert len(paths) == 1
        assert paths[0]["id"] == "path-en-1"

        # Update Path
        updated = repository.update_learning_path(
            conn, "path-en-1", test_user["id"], name="TOEIC 900+ Master", daily_new_target=15
        )
        assert updated["name"] == "TOEIC 900+ Master"
        assert updated["daily_new_target"] == 15

        # Delete Path
        deleted = repository.delete_learning_path(conn, "path-en-1", test_user["id"])
        assert deleted is True

        # Ensure deleted
        assert repository.get_learning_path_by_id(conn, "path-en-1", test_user["id"]) is None


def test_learning_path_language_compatibility(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        # Create English deck and Chinese deck
        deck_en = repository.create_deck(conn, "deck-en-2", test_user["id"], "English Deck", target_language="en")
        deck_zh = repository.create_deck(conn, "deck-zh-1", test_user["id"], "Chinese HSK 1", target_language="zh")

        # Create English path linking English deck (should succeed)
        path = repository.create_learning_path(
            conn,
            path_id="path-en-2",
            user_id=test_user["id"],
            name="English Path",
            learning_language="en",
            deck_ids=["deck-en-2"],
        )
        assert "deck-en-2" in path["linked_deck_ids"]

        # Attempt to link Chinese deck to English path (should fail)
        with pytest.raises(ValueError, match="Cannot link deck with language 'zh' to path with language 'en'"):
            repository.link_deck_to_path(conn, "path-en-2", "deck-zh-1")


def test_learning_path_vocabulary_count_aggregation(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        # Create 2 English decks
        repository.create_deck(conn, "deck-en-a", test_user["id"], "Deck A", target_language="en")
        repository.create_deck(conn, "deck-en-b", test_user["id"], "Deck B", target_language="en")

        # Import 2 words into Deck A and 3 words into Deck B
        csv_a = "term,definition\napple,qua tao\nbanana,qua chuoi\n".encode("utf-8")
        import_vocabulary_file(conn, test_user["id"], "deck-en-a", csv_a, "a.csv")

        csv_b = "term,definition\ncat,con meo\ndog,con cho\nfish,con ca\n".encode("utf-8")
        import_vocabulary_file(conn, test_user["id"], "deck-en-b", csv_b, "b.csv")

        # Create path linking both decks
        path = repository.create_learning_path(
            conn,
            path_id="path-en-multi",
            user_id=test_user["id"],
            name="English Combined",
            learning_language="en",
            deck_ids=["deck-en-a", "deck-en-b"],
        )

        assert len(path["linked_deck_ids"]) == 2
        assert path["total_vocabulary_count"] == 5
