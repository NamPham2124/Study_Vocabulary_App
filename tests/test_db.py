"""Unit tests for SQLite database transactions, foreign keys, and repository operations."""

import sqlite3
import pytest
from vocabmaster.db.connection import get_db, DatabaseManager
from vocabmaster.db import repository
from vocabmaster.auth.security import hash_password


def test_database_initialization_and_schema(temp_db_path):
    with get_db(temp_db_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {r["name"] for r in tables}

        expected = {
            "schema_migrations",
            "users",
            "decks",
            "vocabulary_items",
            "srs_cards",
            "learning_sessions",
            "session_card_logs",
            "import_batches",
        }
        assert expected.issubset(table_names)


def test_foreign_key_enforcement(temp_db_path):
    with get_db(temp_db_path) as conn:
        # Attempting to insert a deck with non-existent user_id should fail
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO decks (id, user_id, name) VALUES ('deck-1', 'nonexistent-user', 'Test')"
            )


def test_transaction_rollback_on_error(temp_db_path):
    manager = DatabaseManager(temp_db_path)
    with pytest.raises(RuntimeError):
        with manager.transaction() as conn:
            pwd_hash, salt = hash_password("pass123")
            repository.create_user(
                conn, "rollback-user", "rollbacker", "rollback@test.com", pwd_hash, salt
            )
            # Intentionally raise to test rollback
            raise RuntimeError("Forced error")

    with manager.transaction() as conn:
        assert repository.get_user_by_id(conn, "rollback-user") is None
