"""Database initialization and schema migration management."""

import sqlite3
from typing import Optional, Union
from pathlib import Path
from vocabmaster.db.connection import DatabaseManager
from vocabmaster.db.schema import CREATE_TABLES_SQL, SCHEMA_VERSION


def init_db(db_path: Optional[Union[str, Path]] = None) -> None:
    """Initialize the database schema if not already initialized."""
    manager = DatabaseManager(db_path)
    conn = manager.get_connection()
    try:
        conn.executescript(CREATE_TABLES_SQL)
        cursor = conn.execute("SELECT version FROM schema_migrations WHERE version = ?", (SCHEMA_VERSION,))
        if not cursor.fetchone():
            conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (SCHEMA_VERSION,))
    finally:
        conn.close()
