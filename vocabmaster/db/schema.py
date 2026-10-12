"""Database schema definition and table creation scripts."""

SCHEMA_VERSION = 3

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
    interface_language TEXT NOT NULL DEFAULT 'vi',
    active_learning_language TEXT NOT NULL DEFAULT 'en',
    has_selected_language INTEGER NOT NULL DEFAULT 0,
    english_voice_preference TEXT NOT NULL DEFAULT 'en-US',
    chinese_voice_preference TEXT NOT NULL DEFAULT 'zh-CN',
    script_preference TEXT NOT NULL DEFAULT 'hans',
    timezone TEXT NOT NULL DEFAULT 'Asia/Ho_Chi_Minh',
    daily_new_target INTEGER NOT NULL DEFAULT 10,
    daily_review_target INTEGER NOT NULL DEFAULT 50,
    daily_time_goal INTEGER NOT NULL DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learning Paths table
CREATE TABLE IF NOT EXISTS learning_paths (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    learning_language TEXT NOT NULL DEFAULT 'en',
    objective TEXT DEFAULT '',
    daily_new_target INTEGER NOT NULL DEFAULT 10,
    daily_time_goal INTEGER NOT NULL DEFAULT 20,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Decks table (Collections / Vocabulary Folders)
CREATE TABLE IF NOT EXISTS decks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    target_language TEXT NOT NULL DEFAULT 'en',
    tags TEXT DEFAULT '[]',
    max_new_cards_per_day INTEGER NOT NULL DEFAULT 10,
    max_reviews_per_day INTEGER NOT NULL DEFAULT 50,
    daily_goal INTEGER NOT NULL DEFAULT 20,
    preferred_duration INTEGER NOT NULL DEFAULT 20,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    icon TEXT NOT NULL DEFAULT 'fa-folder',
    color TEXT NOT NULL DEFAULT '#3b82f6',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Path to Decks association
CREATE TABLE IF NOT EXISTS path_decks (
    path_id TEXT NOT NULL,
    deck_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (path_id, deck_id),
    FOREIGN KEY (path_id) REFERENCES learning_paths (id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE
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
    root_word TEXT DEFAULT '',
    root_word_id TEXT DEFAULT NULL,
    vietnamese_meanings TEXT DEFAULT '[]',
    english_definitions TEXT DEFAULT '[]',
    mnemonics TEXT DEFAULT '',
    audio_url TEXT DEFAULT '',
    is_favorite INTEGER DEFAULT 0,
    language_specific_fields TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (root_word_id) REFERENCES vocabulary_items (id) ON DELETE SET NULL
);

-- Word Relationships table
CREATE TABLE IF NOT EXISTS word_relationships (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    source_vocab_id TEXT NOT NULL,
    target_vocab_id TEXT NOT NULL,
    relation_type TEXT NOT NULL, -- root_word, word_family, synonym, antonym, collocation, compound
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (source_vocab_id) REFERENCES vocabulary_items (id) ON DELETE CASCADE,
    FOREIGN KEY (target_vocab_id) REFERENCES vocabulary_items (id) ON DELETE CASCADE
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
    lapses INTEGER NOT NULL DEFAULT 0,
    history_count INTEGER NOT NULL DEFAULT 0,
    difficulty REAL NOT NULL DEFAULT 0.3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vocab_id) REFERENCES vocabulary_items (id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Learning Sessions table (Daily 20-min and dedicated study sessions)
CREATE TABLE IF NOT EXISTS learning_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    deck_id TEXT DEFAULT NULL,
    path_id TEXT DEFAULT NULL,
    title TEXT NOT NULL,
    session_date TEXT NOT NULL,          -- YYYY-MM-DD
    learning_language TEXT NOT NULL DEFAULT 'en',
    session_type TEXT NOT NULL DEFAULT 'daily_20min', -- daily_20min, review_only, practice_only
    current_phase TEXT NOT NULL DEFAULT 'review',     -- review, new_words, recall_test, practice, completed
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, PAUSED, COMPLETED, ABANDONED
    card_ids_queue TEXT NOT NULL DEFAULT '[]', -- JSON list of srs_card IDs in queue
    current_index INTEGER NOT NULL DEFAULT 0,  -- Pointer to active card in queue
    total_cards INTEGER NOT NULL DEFAULT 0,
    completed_cards INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    incorrect_count INTEGER NOT NULL DEFAULT 0,
    phase_durations TEXT NOT NULL DEFAULT '{}', -- JSON {"review": 120, "new_words": 200, ...}
    phase_data TEXT NOT NULL DEFAULT '{}',      -- JSON phase queues and states
    phase_target_seconds INTEGER NOT NULL DEFAULT 1200, -- 20 minutes default
    start_time TEXT NOT NULL,
    end_time TEXT DEFAULT NULL,
    last_active_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE SET NULL,
    FOREIGN KEY (path_id) REFERENCES learning_paths (id) ON DELETE SET NULL
);

-- Session Card Logs table (detailed answers during sessions)
CREATE TABLE IF NOT EXISTS session_card_logs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    card_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    rating INTEGER NOT NULL,             -- 0 to 5 (Again: 0-1, Hard: 2-3, Good: 4, Easy: 5)
    time_spent_seconds REAL NOT NULL DEFAULT 0.0,
    exercise_type TEXT NOT NULL DEFAULT 'flashcard',
    user_response TEXT DEFAULT '',
    is_correct INTEGER NOT NULL DEFAULT 1,
    scheduled_next_interval REAL NOT NULL DEFAULT 0.0,
    was_new_card INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES srs_cards (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Practice Submissions table (Speaking / Writing / Typing submissions)
CREATE TABLE IF NOT EXISTS practice_submissions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    vocab_id TEXT DEFAULT NULL,
    practice_type TEXT NOT NULL, -- sentence_writing, paragraph_writing, hanzi_typing, pinyin_input, dictation
    prompt TEXT NOT NULL,
    user_text TEXT NOT NULL,
    model_answer TEXT DEFAULT '',
    self_assessment_score INTEGER DEFAULT 4,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (vocab_id) REFERENCES vocabulary_items (id) ON DELETE SET NULL
);

-- User Daily Study Logs (for calendar heatmap & streaks)
CREATE TABLE IF NOT EXISTS user_study_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    study_date TEXT NOT NULL, -- YYYY-MM-DD
    learning_language TEXT NOT NULL DEFAULT 'en',
    duration_seconds REAL NOT NULL DEFAULT 0.0,
    cards_reviewed INTEGER NOT NULL DEFAULT 0,
    new_words_learned INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Import Batches table (Audit logs for CSV / XLSX imports)
CREATE TABLE IF NOT EXISTS import_batches (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    deck_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,             -- csv, xlsx, paste
    total_rows INTEGER NOT NULL DEFAULT 0,
    imported_count INTEGER NOT NULL DEFAULT 0,
    skipped_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    errors_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE
);
"""

CREATE_INDEXES_SQL = """
-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_paths_user ON learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_decks_user ON decks(user_id);
CREATE INDEX IF NOT EXISTS idx_decks_lang ON decks(user_id, target_language);
CREATE INDEX IF NOT EXISTS idx_vocab_deck ON vocabulary_items(deck_id);
CREATE INDEX IF NOT EXISTS idx_vocab_user ON vocabulary_items(user_id);
CREATE INDEX IF NOT EXISTS idx_vocab_term ON vocabulary_items(term);
CREATE INDEX IF NOT EXISTS idx_vocab_lang ON vocabulary_items(language);
CREATE INDEX IF NOT EXISTS idx_vocab_root ON vocabulary_items(root_word_id);
CREATE INDEX IF NOT EXISTS idx_srs_due ON srs_cards(user_id, due_date, state);
CREATE INDEX IF NOT EXISTS idx_srs_deck_due ON srs_cards(deck_id, due_date);
CREATE INDEX IF NOT EXISTS idx_sessions_user_status ON learning_sessions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_sessions_lang ON learning_sessions(user_id, learning_language, status);
CREATE INDEX IF NOT EXISTS idx_session_logs_session ON session_card_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_session_logs_card ON session_card_logs(card_id);
CREATE INDEX IF NOT EXISTS idx_session_logs_user_date ON session_card_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_study_logs_user_date ON user_study_logs(user_id, study_date);
"""
