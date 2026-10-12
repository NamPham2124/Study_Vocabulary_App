"""Database initialization and schema migration management."""

import sqlite3
from typing import Optional, Union, Set
from pathlib import Path
from vocabmaster.db.connection import DatabaseManager
from vocabmaster.db.schema import CREATE_TABLES_SQL, CREATE_INDEXES_SQL, SCHEMA_VERSION


def _get_existing_columns(conn: sqlite3.Connection, table_name: str) -> Set[str]:
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return {row["name"] for row in cursor.fetchall()}


def _safe_add_column(
    conn: sqlite3.Connection, table: str, column_name: str, col_type: str, default: str = ""
):
    existing = _get_existing_columns(conn, table)
    if column_name not in existing:
        default_clause = f" DEFAULT {default}" if default else ""
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {col_type}{default_clause}")


def init_db(
    db_path: Optional[Union[str, Path]] = None,
    database_url: Optional[str] = None,
) -> None:
    """Initialize or migrate the database schema."""
    manager = DatabaseManager(db_path=db_path, database_url=database_url)
    conn = manager.get_connection()
    try:
        if manager.is_postgres:
            conn.executescript(CREATE_TABLES_SQL)
            conn.executescript(CREATE_INDEXES_SQL)
            cursor = conn.execute("SELECT version FROM schema_migrations WHERE version = ?", (SCHEMA_VERSION,))
            if not cursor.fetchone():
                conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (SCHEMA_VERSION,))
            conn.commit()
            return

        # SQLite migration branch
        conn.executescript(CREATE_TABLES_SQL)

        # Apply column migrations for tables created in earlier versions
        _safe_add_column(conn, "users", "interface_language", "TEXT", "'vi'")
        _safe_add_column(conn, "users", "active_learning_language", "TEXT", "'en'")
        _safe_add_column(conn, "users", "has_selected_language", "INTEGER", "0")
        _safe_add_column(conn, "users", "english_voice_preference", "TEXT", "'en-US'")
        _safe_add_column(conn, "users", "chinese_voice_preference", "TEXT", "'zh-CN'")
        _safe_add_column(conn, "users", "script_preference", "TEXT", "'hans'")
        _safe_add_column(conn, "users", "timezone", "TEXT", "'Asia/Ho_Chi_Minh'")
        _safe_add_column(conn, "users", "daily_new_target", "INTEGER", "10")
        _safe_add_column(conn, "users", "daily_review_target", "INTEGER", "50")
        _safe_add_column(conn, "users", "daily_time_goal", "INTEGER", "20")

        _safe_add_column(conn, "decks", "tags", "TEXT", "'[]'")
        _safe_add_column(conn, "decks", "max_new_cards_per_day", "INTEGER", "10")
        _safe_add_column(conn, "decks", "max_reviews_per_day", "INTEGER", "50")
        _safe_add_column(conn, "decks", "daily_goal", "INTEGER", "20")
        _safe_add_column(conn, "decks", "preferred_duration", "INTEGER", "20")
        _safe_add_column(conn, "decks", "status", "TEXT", "'ACTIVE'")
        _safe_add_column(conn, "decks", "icon", "TEXT", "'fa-folder'")
        _safe_add_column(conn, "decks", "color", "TEXT", "'#3b82f6'")

        _safe_add_column(conn, "vocabulary_items", "root_word", "TEXT", "''")
        _safe_add_column(conn, "vocabulary_items", "root_word_id", "TEXT", "NULL")
        _safe_add_column(conn, "vocabulary_items", "vietnamese_meanings", "TEXT", "'[]'")
        _safe_add_column(conn, "vocabulary_items", "english_definitions", "TEXT", "'[]'")
        _safe_add_column(conn, "vocabulary_items", "mnemonics", "TEXT", "''")
        _safe_add_column(conn, "vocabulary_items", "audio_url", "TEXT", "''")
        _safe_add_column(conn, "vocabulary_items", "is_favorite", "INTEGER", "0")

        _safe_add_column(conn, "srs_cards", "lapses", "INTEGER", "0")
        _safe_add_column(conn, "srs_cards", "history_count", "INTEGER", "0")
        _safe_add_column(conn, "srs_cards", "difficulty", "REAL", "0.3")

        _safe_add_column(conn, "learning_sessions", "path_id", "TEXT", "NULL")
        _safe_add_column(conn, "learning_sessions", "learning_language", "TEXT", "'en'")
        _safe_add_column(conn, "learning_sessions", "session_type", "TEXT", "'daily_20min'")
        _safe_add_column(conn, "learning_sessions", "current_phase", "TEXT", "'review'")
        _safe_add_column(conn, "learning_sessions", "phase_durations", "TEXT", "'{}'")
        _safe_add_column(conn, "learning_sessions", "phase_data", "TEXT", "'{}'")
        _safe_add_column(conn, "learning_sessions", "phase_target_seconds", "INTEGER", "1200")

        _safe_add_column(conn, "session_card_logs", "exercise_type", "TEXT", "'flashcard'")
        _safe_add_column(conn, "session_card_logs", "user_response", "TEXT", "''")
        _safe_add_column(conn, "session_card_logs", "is_correct", "INTEGER", "1")
        _safe_add_column(conn, "session_card_logs", "was_new_card", "INTEGER", "0")

        # Create indexes now that all columns are guaranteed to exist
        conn.executescript(CREATE_INDEXES_SQL)

        cursor = conn.execute("SELECT version FROM schema_migrations WHERE version = ?", (SCHEMA_VERSION,))
        if not cursor.fetchone():
            conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (SCHEMA_VERSION,))
    finally:
        conn.close()
