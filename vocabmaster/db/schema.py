"""Database schema definition and table creation scripts."""

SCHEMA_VERSION = 1

CREATE_TABLES_SQL = """
-- Schema migration metadata
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decks table
CREATE TABLE IF NOT EXISTS decks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    target_language TEXT NOT NULL DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Vocabulary Items table
CREATE TABLE IF NOT EXISTS vocabulary_items (
    id TEXT PRIMARY KEY,
    deck_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    language TEXT NOT NULL,
    term TEXT NOT NULL,
    definition TEXT NOT NULL,
    ipa TEXT DEFAULT '',
    part_of_speech TEXT DEFAULT '',
    examples TEXT DEFAULT '[]',
    synonyms TEXT DEFAULT '[]',
    antonyms TEXT DEFAULT '[]',
    notes TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',
    language_specific_fields TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Spaced Repetition (SRS) Cards table
CREATE TABLE IF NOT EXISTS srs_cards (
    id TEXT PRIMARY KEY,
    vocab_id TEXT NOT NULL UNIQUE,
    deck_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'NEW',  -- NEW, LEARNING, REVIEW, RELEARNING
    step_index INTEGER NOT NULL DEFAULT 0,
    repetition_count INTEGER NOT NULL DEFAULT 0,
    interval_days REAL NOT NULL DEFAULT 0.0,
    ease_factor REAL NOT NULL DEFAULT 2.5,
    due_date TEXT NOT NULL,              -- ISO 8601 string: YYYY-MM-DDTHH:MM:SSZ
    last_reviewed_at TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vocab_id) REFERENCES vocabulary_items (id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Learning Sessions table (Recoverable daily study sessions)
CREATE TABLE IF NOT EXISTS learning_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    deck_id TEXT DEFAULT NULL,           -- NULL if studying across all user decks
    title TEXT NOT NULL,
    session_date TEXT NOT NULL,          -- YYYY-MM-DD
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, PAUSED, COMPLETED, ABANDONED
    card_ids_queue TEXT NOT NULL DEFAULT '[]', -- JSON list of srs_card IDs in queue
    current_index INTEGER NOT NULL DEFAULT 0,  -- Pointer to active card in queue
    total_cards INTEGER NOT NULL DEFAULT 0,
    completed_cards INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    incorrect_count INTEGER NOT NULL DEFAULT 0,
    start_time TEXT NOT NULL,
    end_time TEXT DEFAULT NULL,
    last_active_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE SET NULL
);

-- Session Card Logs table (detailed answers during sessions)
CREATE TABLE IF NOT EXISTS session_card_logs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    card_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    rating INTEGER NOT NULL,             -- 0 to 5
    time_spent_seconds REAL NOT NULL DEFAULT 0.0,
    scheduled_next_interval REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES srs_cards (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Import Batches table (Audit logs for CSV / XLSX imports)
CREATE TABLE IF NOT EXISTS import_batches (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    deck_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,             -- csv or xlsx
    total_rows INTEGER NOT NULL DEFAULT 0,
    imported_count INTEGER NOT NULL DEFAULT 0,
    skipped_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    errors_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_decks_user ON decks(user_id);
CREATE INDEX IF NOT EXISTS idx_vocab_deck ON vocabulary_items(deck_id);
CREATE INDEX IF NOT EXISTS idx_vocab_user ON vocabulary_items(user_id);
CREATE INDEX IF NOT EXISTS idx_vocab_term ON vocabulary_items(term);
CREATE INDEX IF NOT EXISTS idx_srs_due ON srs_cards(user_id, due_date, state);
CREATE INDEX IF NOT EXISTS idx_srs_deck_due ON srs_cards(deck_id, due_date);
CREATE INDEX IF NOT EXISTS idx_sessions_user_status ON learning_sessions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_session_logs_session ON session_card_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_session_logs_card ON session_card_logs(card_id);
"""
