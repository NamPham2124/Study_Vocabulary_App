# VocabMaster 🧠📚

A robust, production-ready Spaced Repetition System (SRS) and multilingual vocabulary learning platform engineered for durable data storage, fault-tolerant CSV/XLSX imports, linguistic typing across multiple language families, and crash-resilient daily study sessions.

---

## 🌟 Architecture & Core Features

### 1. Persistent Relational Storage (`vocabmaster/db`)
- Powered by SQLite with Write-Ahead Logging (`WAL`), strict foreign keys (`PRAGMA foreign_keys = ON`), parameterized queries, and ACID transaction boundaries.
- Dedicated relational tables:
  - `users`: User profiles, cryptographically salted password hashes.
  - `decks`: Multilingual card collections with target language binding.
  - `vocabulary_items`: Rich linguistic representations (IPA, part of speech, examples, synonyms, antonyms, language-specific fields).
  - `srs_cards`: Spaced repetition state, ease factor, repetition counts, intervals, and due dates.
  - `learning_sessions`: Daily study sessions with card queue persistence and crash recovery pointers.
  - `session_card_logs`: Granular log of every card answer attempt and response latency.
  - `import_batches`: Audit logs for file imports with row-level error tracking.

### 2. Cryptographic Security & Multi-Tenant Isolation (`vocabmaster/auth`)
- **Password Hashing**: PBKDF2-HMAC-SHA256 with 120,000 iterations and 16-byte cryptographically secure random salts.
- **Authentication**: Signed JWT access tokens (HMAC-SHA256) with expiration enforcement.
- **Strict Access Control**: Zero cross-user data leakage. All deck, vocabulary, import, and study session operations strictly enforce user ownership.

### 3. Language-Specific Vocabulary Models (`vocabmaster/models`)
- Strongly typed Pydantic models with linguistic schema validation:
  - **English (`en`)**: CEFR levels (A1-C2), collocations, phrasal verbs, irregular forms.
  - **Japanese (`ja`)**: Kanji/Word, Furigana/Kana reading, Romaji, JLPT level (N5-N1), verb types, transitivity, kanji components.
  - **German (`de`)**: Grammatical gender (masculine, feminine, neuter), articles (`der`, `die`, `das`), plural forms, case governances (`Nominativ`, `Akkusativ`, `Dativ`, `Genitiv`), prepositions, CEFR level.
  - **Romance (`es`, `fr`)**: Gender, plural form, conjugation groups, auxiliary verbs.
  - **Vietnamese (`vi`)**: Tone classification (`ngang`, `huyền`, `sắc`, `hỏi`, `ngã`, `nặng`), Sino-Vietnamese roots (Hán-Việt), regional pronunciations.

### 4. Robust CSV & XLSX Importer (`vocabmaster/importer`)
- **Format Support**: Delimited text (`.csv`) and Excel workbooks (`.xlsx`).
- **Encoding & Delimiter Detection**: Automatic handling of UTF-8, UTF-8 with BOM (`\ufeff`), Latin-1, and delimiter sniffing (comma, semicolon, tab, pipe).
- **Intelligent Header Mapping**: Auto-detects synonymous column names across languages (e.g. `term` / `word` / `từ`, `definition` / `meaning` / `nghĩa`).
- **Fault-Tolerant Processing**: Individual malformed or invalid rows are captured in an error log without failing the remainder of the import.
- **Deduplication Modes**:
  - `skip`: Preserves existing terms.
  - `overwrite`: Updates definitions and linguistic fields of existing terms.
  - `allow_duplicates`: Inserts new records regardless of existing terms.
- **Automatic SRS Initialization**: Automatically initializes SRS cards in state `NEW` for all imported vocabulary items.

### 5. SM-2+ Spaced Repetition Engine (`vocabmaster/srs`)
- Full implementation of the SuperMemo SM-2+ spaced repetition algorithm:
  - **Card States**: `NEW`, `LEARNING`, `REVIEW`, `RELEARNING`.
  - **Rating Scale (0-5)**:
    - `0`: Complete blackout
    - `1`: Incorrect, remembered upon seeing answer
    - `2`: Incorrect, hard struggle
    - `3`: Correct with difficulty
    - `4`: Good recall with reasonable effort
    - `5`: Perfect, effortless recall
  - **Interval Progression**:
    - First success: 1 day
    - Second success: 6 days
    - Subsequent successes: $I_n = \text{round}(I_{n-1} \times EF)$
  - **Dynamic Ease Factor**:
    - $EF' = EF + (0.1 - (5 - q) \times (0.08 + (5 - q) \times 0.02))$
    - Bound by minimum ease factor $EF_{min} = 1.30$.
  - **Lapse Penalties**: Resets repetitions to 0, transitions to `RELEARNING`, schedules immediate review, and applies ease factor penalty.

### 6. Crash-Resilient Recoverable Daily Study Sessions (`vocabmaster/session`)
- Daily learning sessions manage due review cards and new cards within configurable quotas.
- **Atomic Step Persistence**: After every card answer, SRS metrics, session index (`current_index`), and card attempt logs are immediately committed to persistent storage.
- **Crash Recovery**: If an application closes, disconnects, or crashes mid-session, reopening the session restores the exact card queue and index without repeating answered cards or losing metrics.
- **Intraday Requeuing**: Failed cards (ratings < 3) are automatically re-appended to the end of the session queue for immediate reinforcement before session completion.
- **Performance Metrics**: Computes accuracy percentage, time elapsed, retention scores, and completed cards.

---

## 🚀 Quickstart & CLI Usage

### 1. Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Initialize Database & Register User
```bash
# Initialize SQLite database schema
vocabmaster init-db

# Register and log in
vocabmaster register --username learner --email learner@example.com --password mysecretpass
```

### 3. Create Decks & Import Vocabulary
```bash
# Create a Japanese deck
vocabmaster deck-create --name "JLPT N5 Core" --lang ja

# List decks
vocabmaster deck-list

# Import vocabulary from CSV or Excel XLSX
vocabmaster import --deck <DECK_ID> --file vocabulary.csv --dedup skip
```

### 4. Interactive Study Session & Recovery
```bash
# Start flashcard study
vocabmaster study --deck <DECK_ID>

# If interrupted, simply resume:
vocabmaster resume
```

### 5. Check Progress & Statistics
```bash
vocabmaster stats
```

---

## 🌐 REST API Endpoints

Run the server:
```bash
uvicorn vocabmaster.api.app:create_app --factory --port 8000 --reload
```

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register user account |
| `POST` | `/api/auth/login` | Login and receive Bearer JWT |
| `GET` | `/api/auth/me` | Fetch authenticated user profile |
| `POST` | `/api/decks` | Create a vocabulary deck |
| `GET` | `/api/decks` | List user decks with stats |
| `GET` | `/api/decks/{id}` | Get deck details |
| `PUT` | `/api/decks/{id}` | Update deck |
| `DELETE` | `/api/decks/{id}` | Delete deck (cascades items & cards) |
| `POST` | `/api/decks/{id}/vocab` | Add a vocabulary item |
| `GET` | `/api/decks/{id}/vocab` | List items with search & pagination |
| `PUT` | `/api/vocab/{id}` | Update vocabulary item |
| `DELETE` | `/api/vocab/{id}` | Delete vocabulary item |
| `POST` | `/api/decks/{id}/import` | Upload CSV or XLSX file |
| `POST` | `/api/sessions/start` | Start or resume daily session |
| `GET` | `/api/sessions/active` | Retrieve active recoverable session |
| `POST` | `/api/sessions/{id}/answer` | Submit rating & advance session |
| `POST` | `/api/sessions/{id}/pause` | Pause active session |
| `POST` | `/api/sessions/{id}/resume` | Resume paused session |
| `GET` | `/api/sessions/{id}/summary` | Get session performance analytics |
| `GET` | `/api/stats` | System overview & cards due today |

---

## 🧪 Testing

Run the automated test suite with pytest:
```bash
.venv/bin/pytest -v
```
All 32 unit and integration tests verify persistent storage, transactions, foreign keys, password hashing, JWTs, access control, linguistic models, SM-2+ spaced repetition, CSV/XLSX imports, crash recovery, and REST API flows.
