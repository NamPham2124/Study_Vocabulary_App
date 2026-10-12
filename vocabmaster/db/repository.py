"""Repository layer for parameterized SQLite database operations."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import sqlite3


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def create_user(
    conn: sqlite3.Connection,
    user_id: str,
    username: str,
    email: str,
    password_hash: str,
    salt: str,
) -> Dict[str, Any]:
    now = _now_iso()
    sql = """
    INSERT INTO users (id, username, email, password_hash, salt, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, 1, ?, ?)
    """
    conn.execute(sql, (user_id, username, email.lower(), password_hash, salt, now, now))
    return get_user_by_id(conn, user_id)  # type: ignore


def get_user_by_id(conn: sqlite3.Connection, user_id: str) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM users WHERE id = ?"
    row = conn.execute(sql, (user_id,)).fetchone()
    return dict(row) if row else None


def get_user_by_email(conn: sqlite3.Connection, email: str) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM users WHERE email = ?"
    row = conn.execute(sql, (email.lower(),)).fetchone()
    return dict(row) if row else None


def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM users WHERE username = ?"
    row = conn.execute(sql, (username,)).fetchone()
    return dict(row) if row else None


def list_users(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    sql = "SELECT id, username, email, is_active, created_at FROM users ORDER BY created_at DESC"
    return [dict(row) for row in conn.execute(sql).fetchall()]


# ---------------------------------------------------------------------------
# Decks
# ---------------------------------------------------------------------------

def create_deck(
    conn: sqlite3.Connection,
    deck_id: str,
    user_id: str,
    name: str,
    description: str = "",
    target_language: str = "en",
) -> Dict[str, Any]:
    now = _now_iso()
    sql = """
    INSERT INTO decks (id, user_id, name, description, target_language, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(sql, (deck_id, user_id, name, description, target_language, now, now))
    return get_deck_by_id(conn, deck_id, user_id)  # type: ignore


def get_deck_by_id(
    conn: sqlite3.Connection, deck_id: str, user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    if user_id:
        sql = "SELECT * FROM decks WHERE id = ? AND user_id = ?"
        row = conn.execute(sql, (deck_id, user_id)).fetchone()
    else:
        sql = "SELECT * FROM decks WHERE id = ?"
        row = conn.execute(sql, (deck_id,)).fetchone()
    return dict(row) if row else None


def list_decks_for_user(conn: sqlite3.Connection, user_id: str) -> List[Dict[str, Any]]:
    sql = """
    SELECT d.*, 
           COUNT(v.id) AS total_cards,
           SUM(CASE WHEN s.due_date <= ? AND s.state != 'NEW' THEN 1 ELSE 0 END) AS due_reviews,
           SUM(CASE WHEN s.state = 'NEW' THEN 1 ELSE 0 END) AS new_cards
    FROM decks d
    LEFT JOIN vocabulary_items v ON d.id = v.deck_id
    LEFT JOIN srs_cards s ON v.id = s.vocab_id
    WHERE d.user_id = ?
    GROUP BY d.id
    ORDER BY d.created_at DESC
    """
    now = _now_iso()
    rows = conn.execute(sql, (now, user_id)).fetchall()
    return [dict(r) for r in rows]


def update_deck(
    conn: sqlite3.Connection,
    deck_id: str,
    user_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    target_language: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    existing = get_deck_by_id(conn, deck_id, user_id)
    if not existing:
        return None

    new_name = name if name is not None else existing["name"]
    new_desc = description if description is not None else existing["description"]
    new_lang = target_language if target_language is not None else existing["target_language"]
    now = _now_iso()

    sql = """
    UPDATE decks SET name = ?, description = ?, target_language = ?, updated_at = ?
    WHERE id = ? AND user_id = ?
    """
    conn.execute(sql, (new_name, new_desc, new_lang, now, deck_id, user_id))
    return get_deck_by_id(conn, deck_id, user_id)


def delete_deck(conn: sqlite3.Connection, deck_id: str, user_id: str) -> bool:
    sql = "DELETE FROM decks WHERE id = ? AND user_id = ?"
    cursor = conn.execute(sql, (deck_id, user_id))
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Vocabulary Items
# ---------------------------------------------------------------------------

def create_vocab_item(conn: sqlite3.Connection, item: Dict[str, Any]) -> Dict[str, Any]:
    now = _now_iso()
    examples_json = json.dumps(item.get("examples", []))
    synonyms_json = json.dumps(item.get("synonyms", []))
    antonyms_json = json.dumps(item.get("antonyms", []))
    tags_json = json.dumps(item.get("tags", []))
    lang_fields_json = json.dumps(item.get("language_specific_fields", {}))

    sql = """
    INSERT INTO vocabulary_items (
        id, deck_id, user_id, language, term, definition, ipa,
        part_of_speech, examples, synonyms, antonyms, notes,
        tags, language_specific_fields, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            item["id"],
            item["deck_id"],
            item["user_id"],
            item.get("language", "en"),
            item["term"],
            item["definition"],
            item.get("ipa", ""),
            item.get("part_of_speech", ""),
            examples_json,
            synonyms_json,
            antonyms_json,
            item.get("notes", ""),
            tags_json,
            lang_fields_json,
            now,
            now,
        ),
    )
    return get_vocab_item_by_id(conn, item["id"], item["user_id"])  # type: ignore


def _deserialize_vocab_row(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    d = dict(row)
    for field in ("examples", "synonyms", "antonyms", "tags"):
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = []
    if "language_specific_fields" in d and isinstance(d["language_specific_fields"], str):
        try:
            d["language_specific_fields"] = json.loads(d["language_specific_fields"])
        except Exception:
            d["language_specific_fields"] = {}
    return d


def get_vocab_item_by_id(
    conn: sqlite3.Connection, vocab_id: str, user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    if user_id:
        sql = "SELECT * FROM vocabulary_items WHERE id = ? AND user_id = ?"
        row = conn.execute(sql, (vocab_id, user_id)).fetchone()
    else:
        sql = "SELECT * FROM vocabulary_items WHERE id = ?"
        row = conn.execute(sql, (vocab_id,)).fetchone()
    return _deserialize_vocab_row(row)


def find_vocab_by_term(
    conn: sqlite3.Connection, deck_id: str, term: str
) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM vocabulary_items WHERE deck_id = ? AND LOWER(term) = LOWER(?)"
    row = conn.execute(sql, (deck_id, term.strip())).fetchone()
    return _deserialize_vocab_row(row)


def list_vocab_items(
    conn: sqlite3.Connection,
    deck_id: Optional[str] = None,
    user_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    clauses = []
    params: List[Any] = []

    if user_id:
        clauses.append("user_id = ?")
        params.append(user_id)
    if deck_id:
        clauses.append("deck_id = ?")
        params.append(deck_id)
    if search:
        clauses.append("(LOWER(term) LIKE ? OR LOWER(definition) LIKE ?)")
        term_search = f"%{search.lower()}%"
        params.extend([term_search, term_search])

    where_str = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT * FROM vocabulary_items {where_str} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(sql, params).fetchall()
    return [_deserialize_vocab_row(r) for r in rows if r]  # type: ignore


def update_vocab_item(
    conn: sqlite3.Connection, vocab_id: str, user_id: str, updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    existing = get_vocab_item_by_id(conn, vocab_id, user_id)
    if not existing:
        return None

    now = _now_iso()
    set_clauses = ["updated_at = ?"]
    params: List[Any] = [now]

    simple_fields = ["term", "definition", "ipa", "part_of_speech", "notes", "language"]
    for field in simple_fields:
        if field in updates and updates[field] is not None:
            set_clauses.append(f"{field} = ?")
            params.append(updates[field])

    json_fields = ["examples", "synonyms", "antonyms", "tags", "language_specific_fields"]
    for field in json_fields:
        if field in updates and updates[field] is not None:
            set_clauses.append(f"{field} = ?")
            params.append(json.dumps(updates[field]))

    params.extend([vocab_id, user_id])
    sql = f"UPDATE vocabulary_items SET {', '.join(set_clauses)} WHERE id = ? AND user_id = ?"
    conn.execute(sql, params)
    return get_vocab_item_by_id(conn, vocab_id, user_id)


def delete_vocab_item(conn: sqlite3.Connection, vocab_id: str, user_id: str) -> bool:
    sql = "DELETE FROM vocabulary_items WHERE id = ? AND user_id = ?"
    cursor = conn.execute(sql, (vocab_id, user_id))
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Spaced Repetition (SRS) Cards
# ---------------------------------------------------------------------------

def create_srs_card(conn: sqlite3.Connection, card: Dict[str, Any]) -> Dict[str, Any]:
    now = _now_iso()
    sql = """
    INSERT INTO srs_cards (
        id, vocab_id, deck_id, user_id, state, step_index,
        repetition_count, interval_days, ease_factor, due_date,
        last_reviewed_at, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            card["id"],
            card["vocab_id"],
            card["deck_id"],
            card["user_id"],
            card.get("state", "NEW"),
            card.get("step_index", 0),
            card.get("repetition_count", 0),
            card.get("interval_days", 0.0),
            card.get("ease_factor", 2.5),
            card.get("due_date", now),
            card.get("last_reviewed_at", None),
            now,
        ),
    )
    return get_srs_card_by_id(conn, card["id"])  # type: ignore


def get_srs_card_by_id(
    conn: sqlite3.Connection, card_id: str, user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    if user_id:
        sql = "SELECT * FROM srs_cards WHERE id = ? AND user_id = ?"
        row = conn.execute(sql, (card_id, user_id)).fetchone()
    else:
        sql = "SELECT * FROM srs_cards WHERE id = ?"
        row = conn.execute(sql, (card_id,)).fetchone()
    return dict(row) if row else None


def get_srs_card_by_vocab_id(
    conn: sqlite3.Connection, vocab_id: str
) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM srs_cards WHERE vocab_id = ?"
    row = conn.execute(sql, (vocab_id,)).fetchone()
    return dict(row) if row else None


def update_srs_card(
    conn: sqlite3.Connection,
    card_id: str,
    user_id: str,
    state: str,
    step_index: int,
    repetition_count: int,
    interval_days: float,
    ease_factor: float,
    due_date: str,
    last_reviewed_at: str,
) -> Optional[Dict[str, Any]]:
    sql = """
    UPDATE srs_cards
    SET state = ?, step_index = ?, repetition_count = ?, interval_days = ?,
        ease_factor = ?, due_date = ?, last_reviewed_at = ?
    WHERE id = ? AND user_id = ?
    """
    cursor = conn.execute(
        sql,
        (
            state,
            step_index,
            repetition_count,
            interval_days,
            ease_factor,
            due_date,
            last_reviewed_at,
            card_id,
            user_id,
        ),
    )
    if cursor.rowcount == 0:
        return None
    return get_srs_card_by_id(conn, card_id, user_id)


def get_due_review_cards(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    as_of_iso: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Fetch cards in LEARNING, REVIEW, or RELEARNING that are due."""
    as_of = as_of_iso or _now_iso()
    clauses = ["user_id = ?", "state != 'NEW'", "due_date <= ?"]
    params: List[Any] = [user_id, as_of]

    if deck_id:
        clauses.append("deck_id = ?")
        params.append(deck_id)

    sql = f"""
    SELECT * FROM srs_cards
    WHERE {' AND '.join(clauses)}
    ORDER BY due_date ASC
    LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def get_new_cards(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Fetch unlearned cards in state 'NEW'."""
    clauses = ["user_id = ?", "state = 'NEW'"]
    params: List[Any] = [user_id]

    if deck_id:
        clauses.append("deck_id = ?")
        params.append(deck_id)

    sql = f"""
    SELECT * FROM srs_cards
    WHERE {' AND '.join(clauses)}
    ORDER BY created_at ASC
    LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def get_due_and_new_counts(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    as_of_iso: Optional[str] = None,
) -> Dict[str, int]:
    as_of = as_of_iso or _now_iso()
    clauses = ["user_id = ?"]
    params: List[Any] = [user_id]

    if deck_id:
        clauses.append("deck_id = ?")
        params.append(deck_id)

    where_str = f"WHERE {' AND '.join(clauses)}"
    sql = f"""
    SELECT 
        SUM(CASE WHEN state = 'NEW' THEN 1 ELSE 0 END) AS new_count,
        SUM(CASE WHEN state != 'NEW' AND due_date <= ? THEN 1 ELSE 0 END) AS due_count
    FROM srs_cards
    {where_str}
    """
    row = conn.execute(sql, [as_of] + params).fetchone()
    return {
        "new_count": (row["new_count"] or 0) if row else 0,
        "due_count": (row["due_count"] or 0) if row else 0,
    }


# ---------------------------------------------------------------------------
# Learning Sessions (Recoverable Daily Learning)
# ---------------------------------------------------------------------------

def create_session(conn: sqlite3.Connection, session: Dict[str, Any]) -> Dict[str, Any]:
    now = _now_iso()
    queue_json = json.dumps(session.get("card_ids_queue", []))

    sql = """
    INSERT INTO learning_sessions (
        id, user_id, deck_id, title, session_date, status,
        card_ids_queue, current_index, total_cards, completed_cards,
        correct_count, incorrect_count, start_time, end_time, last_active_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            session["id"],
            session["user_id"],
            session.get("deck_id"),
            session["title"],
            session.get("session_date", now[:10]),
            session.get("status", "ACTIVE"),
            queue_json,
            session.get("current_index", 0),
            session.get("total_cards", len(session.get("card_ids_queue", []))),
            session.get("completed_cards", 0),
            session.get("correct_count", 0),
            session.get("incorrect_count", 0),
            session.get("start_time", now),
            session.get("end_time"),
            now,
        ),
    )
    return get_session_by_id(conn, session["id"], session["user_id"])  # type: ignore


def _deserialize_session_row(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    d = dict(row)
    if "card_ids_queue" in d and isinstance(d["card_ids_queue"], str):
        try:
            d["card_ids_queue"] = json.loads(d["card_ids_queue"])
        except Exception:
            d["card_ids_queue"] = []
    return d


def get_session_by_id(
    conn: sqlite3.Connection, session_id: str, user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    if user_id:
        sql = "SELECT * FROM learning_sessions WHERE id = ? AND user_id = ?"
        row = conn.execute(sql, (session_id, user_id)).fetchone()
    else:
        sql = "SELECT * FROM learning_sessions WHERE id = ?"
        row = conn.execute(sql, (session_id,)).fetchone()
    return _deserialize_session_row(row)


def get_active_or_paused_session(
    conn: sqlite3.Connection, user_id: str, deck_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    clauses = ["user_id = ?", "status IN ('ACTIVE', 'PAUSED')"]
    params: List[Any] = [user_id]
    if deck_id:
        clauses.append("(deck_id = ? OR deck_id IS NULL)")
        params.append(deck_id)

    sql = f"""
    SELECT * FROM learning_sessions
    WHERE {' AND '.join(clauses)}
    ORDER BY last_active_at DESC
    LIMIT 1
    """
    row = conn.execute(sql, params).fetchone()
    return _deserialize_session_row(row)


def update_session(
    conn: sqlite3.Connection, session_id: str, user_id: str, **updates: Any
) -> Optional[Dict[str, Any]]:
    existing = get_session_by_id(conn, session_id, user_id)
    if not existing:
        return None

    now = _now_iso()
    updates["last_active_at"] = now

    set_clauses = []
    params: List[Any] = []

    for k, v in updates.items():
        if k == "card_ids_queue" and isinstance(v, list):
            set_clauses.append("card_ids_queue = ?")
            params.append(json.dumps(v))
        else:
            set_clauses.append(f"{k} = ?")
            params.append(v)

    params.extend([session_id, user_id])
    sql = f"UPDATE learning_sessions SET {', '.join(set_clauses)} WHERE id = ? AND user_id = ?"
    conn.execute(sql, params)
    return get_session_by_id(conn, session_id, user_id)


def record_card_log(conn: sqlite3.Connection, log: Dict[str, Any]) -> Dict[str, Any]:
    now = _now_iso()
    sql = """
    INSERT INTO session_card_logs (
        id, session_id, card_id, user_id, rating,
        time_spent_seconds, scheduled_next_interval, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            log["id"],
            log["session_id"],
            log["card_id"],
            log["user_id"],
            log["rating"],
            log.get("time_spent_seconds", 0.0),
            log.get("scheduled_next_interval", 0.0),
            now,
        ),
    )
    return log


def get_session_card_logs(
    conn: sqlite3.Connection, session_id: str, user_id: str
) -> List[Dict[str, Any]]:
    sql = """
    SELECT * FROM session_card_logs
    WHERE session_id = ? AND user_id = ?
    ORDER BY created_at ASC
    """
    rows = conn.execute(sql, (session_id, user_id)).fetchall()
    return [dict(r) for r in rows]


def list_user_sessions(
    conn: sqlite3.Connection, user_id: str, limit: int = 20
) -> List[Dict[str, Any]]:
    sql = """
    SELECT * FROM learning_sessions
    WHERE user_id = ?
    ORDER BY start_time DESC
    LIMIT ?
    """
    rows = conn.execute(sql, (user_id, limit)).fetchall()
    return [_deserialize_session_row(r) for r in rows if r]  # type: ignore


# ---------------------------------------------------------------------------
# Import Batches
# ---------------------------------------------------------------------------

def create_import_batch(conn: sqlite3.Connection, batch: Dict[str, Any]) -> Dict[str, Any]:
    now = _now_iso()
    errors_json = json.dumps(batch.get("errors", []))
    sql = """
    INSERT INTO import_batches (
        id, user_id, deck_id, filename, file_type,
        total_rows, imported_count, skipped_count, error_count,
        errors_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            batch["id"],
            batch["user_id"],
            batch["deck_id"],
            batch["filename"],
            batch["file_type"],
            batch.get("total_rows", 0),
            batch.get("imported_count", 0),
            batch.get("skipped_count", 0),
            batch.get("error_count", 0),
            errors_json,
            now,
        ),
    )
    return get_import_batch_by_id(conn, batch["id"], batch["user_id"])  # type: ignore


def get_import_batch_by_id(
    conn: sqlite3.Connection, batch_id: str, user_id: str
) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM import_batches WHERE id = ? AND user_id = ?"
    row = conn.execute(sql, (batch_id, user_id)).fetchone()
    if not row:
        return None
    d = dict(row)
    if "errors_json" in d and isinstance(d["errors_json"], str):
        try:
            d["errors"] = json.loads(d["errors_json"])
        except Exception:
            d["errors"] = []
    return d
