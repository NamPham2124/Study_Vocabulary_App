"""Repository layer for parameterized SQLite database operations."""

import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import sqlite3


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Users & User Settings
# ---------------------------------------------------------------------------

def create_user(
    conn: sqlite3.Connection,
    user_id: str,
    username: str,
    email: str,
    password_hash: str,
    salt: str,
    interface_language: str = "vi",
    active_learning_language: str = "en",
    has_selected_language: int = 0,
    english_voice_preference: str = "en-US",
    chinese_voice_preference: str = "zh-CN",
    script_preference: str = "hans",
    timezone_name: str = "Asia/Ho_Chi_Minh",
    daily_new_target: int = 10,
    daily_review_target: int = 50,
    daily_time_goal: int = 20,
) -> Dict[str, Any]:
    now = _now_iso()
    sql = """
    INSERT INTO users (
        id, username, email, password_hash, salt, is_active,
        interface_language, active_learning_language, has_selected_language,
        english_voice_preference, chinese_voice_preference, script_preference,
        timezone, daily_new_target, daily_review_target, daily_time_goal, created_at, updated_at
    )
    VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            user_id,
            username,
            email.lower(),
            password_hash,
            salt,
            interface_language,
            active_learning_language,
            has_selected_language,
            english_voice_preference,
            chinese_voice_preference,
            script_preference,
            timezone_name,
            daily_new_target,
            daily_review_target,
            daily_time_goal,
            now,
            now,
        ),
    )
    return get_user_by_id(conn, user_id)  # type: ignore


def get_user_by_id(conn: sqlite3.Connection, user_id: str) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM users WHERE id = ?"
    row = conn.execute(sql, (user_id,)).fetchone()
    return dict(row) if row else None


def get_user_by_email(conn: sqlite3.Connection, email: str) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM users WHERE LOWER(email) = LOWER(?)"
    row = conn.execute(sql, (email.strip(),)).fetchone()
    return dict(row) if row else None


def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM users WHERE LOWER(username) = LOWER(?)"
    row = conn.execute(sql, (username.strip(),)).fetchone()
    return dict(row) if row else None


def update_user_settings(
    conn: sqlite3.Connection, user_id: str, **updates: Any
) -> Optional[Dict[str, Any]]:
    existing = get_user_by_id(conn, user_id)
    if not existing:
        return None

    now = _now_iso()
    set_clauses = ["updated_at = ?"]
    params: List[Any] = [now]

    allowed = {
        "interface_language",
        "active_learning_language",
        "has_selected_language",
        "english_voice_preference",
        "chinese_voice_preference",
        "script_preference",
        "timezone",
        "daily_new_target",
        "daily_review_target",
        "daily_time_goal",
    }
    for k, v in updates.items():
        if k in allowed and v is not None:
            set_clauses.append(f"{k} = ?")
            params.append(v)

    params.append(user_id)
    sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
    conn.execute(sql, params)
    return get_user_by_id(conn, user_id)


def list_users(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    sql = "SELECT id, username, email, is_active, interface_language, active_learning_language, created_at FROM users ORDER BY created_at DESC"
    return [dict(row) for row in conn.execute(sql).fetchall()]


# ---------------------------------------------------------------------------
# Learning Paths
# ---------------------------------------------------------------------------

def create_learning_path(
    conn: sqlite3.Connection,
    path_id: str,
    user_id: str,
    name: str,
    description: str = "",
    learning_language: str = "en",
    objective: str = "",
    daily_new_target: int = 5,
    daily_time_goal: int = 20,
    deck_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    now = _now_iso()
    sql = """
    INSERT INTO learning_paths (
        id, user_id, name, description, learning_language, objective,
        daily_new_target, daily_time_goal, status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
    """
    conn.execute(
        sql,
        (
            path_id,
            user_id,
            name,
            description,
            learning_language,
            objective,
            daily_new_target,
            daily_time_goal,
            now,
            now,
        ),
    )

    if deck_ids:
        for d_id in deck_ids:
            link_deck_to_path(conn, path_id, d_id)

    return get_learning_path_by_id(conn, path_id, user_id)  # type: ignore


def get_learning_path_by_id(
    conn: sqlite3.Connection, path_id: str, user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    if user_id:
        sql = "SELECT * FROM learning_paths WHERE id = ? AND user_id = ?"
        row = conn.execute(sql, (path_id, user_id)).fetchone()
    else:
        sql = "SELECT * FROM learning_paths WHERE id = ?"
        row = conn.execute(sql, (path_id,)).fetchone()

    if not row:
        return None
    d = dict(row)

    # Fetch linked decks
    decks_sql = "SELECT deck_id FROM path_decks WHERE path_id = ?"
    deck_rows = conn.execute(decks_sql, (path_id,)).fetchall()
    d["linked_deck_ids"] = [r["deck_id"] for r in deck_rows]

    # Calculate total vocabulary count across linked decks
    if d["linked_deck_ids"]:
        placeholders = ",".join("?" * len(d["linked_deck_ids"]))
        cnt_sql = f"SELECT COUNT(*) as count FROM vocabulary_items WHERE deck_id IN ({placeholders})"
        cnt_row = conn.execute(cnt_sql, d["linked_deck_ids"]).fetchone()
        d["total_vocabulary_count"] = cnt_row["count"] if cnt_row else 0
    else:
        d["total_vocabulary_count"] = 0

    return d


def list_learning_paths_for_user(
    conn: sqlite3.Connection, user_id: str, learning_language: Optional[str] = None
) -> List[Dict[str, Any]]:
    clauses = ["user_id = ?"]
    params: List[Any] = [user_id]
    if learning_language:
        clauses.append("learning_language = ?")
        params.append(learning_language)

    sql = f"SELECT * FROM learning_paths WHERE {' AND '.join(clauses)} ORDER BY created_at DESC"
    rows = conn.execute(sql, params).fetchall()
    results = []
    for r in rows:
        path = get_learning_path_by_id(conn, r["id"], user_id)
        if path:
            results.append(path)
    return results


def update_learning_path(
    conn: sqlite3.Connection, path_id: str, user_id: str, **updates: Any
) -> Optional[Dict[str, Any]]:
    existing = get_learning_path_by_id(conn, path_id, user_id)
    if not existing:
        return None

    now = _now_iso()
    set_clauses = ["updated_at = ?"]
    params: List[Any] = [now]

    allowed = {
        "name",
        "description",
        "objective",
        "daily_new_target",
        "daily_time_goal",
        "status",
    }
    for k, v in updates.items():
        if k in allowed and v is not None:
            set_clauses.append(f"{k} = ?")
            params.append(v)

    params.extend([path_id, user_id])
    sql = f"UPDATE learning_paths SET {', '.join(set_clauses)} WHERE id = ? AND user_id = ?"
    conn.execute(sql, params)

    if "deck_ids" in updates and updates["deck_ids"] is not None:
        conn.execute("DELETE FROM path_decks WHERE path_id = ?", (path_id,))
        for d_id in updates["deck_ids"]:
            link_deck_to_path(conn, path_id, d_id)

    return get_learning_path_by_id(conn, path_id, user_id)


def delete_learning_path(conn: sqlite3.Connection, path_id: str, user_id: str) -> bool:
    sql = "DELETE FROM learning_paths WHERE id = ? AND user_id = ?"
    cursor = conn.execute(sql, (path_id, user_id))
    return cursor.rowcount > 0


def link_deck_to_path(conn: sqlite3.Connection, path_id: str, deck_id: str) -> None:
    path_row = conn.execute("SELECT learning_language FROM learning_paths WHERE id = ?", (path_id,)).fetchone()
    deck_row = conn.execute("SELECT target_language FROM decks WHERE id = ?", (deck_id,)).fetchone()
    if path_row and deck_row:
        if path_row["learning_language"] != deck_row["target_language"]:
            raise ValueError(
                f"Cannot link deck with language '{deck_row['target_language']}' to path with language '{path_row['learning_language']}'"
            )
    conn.execute(
        "INSERT OR IGNORE INTO path_decks (path_id, deck_id) VALUES (?, ?)",
        (path_id, deck_id),
    )


def unlink_deck_from_path(conn: sqlite3.Connection, path_id: str, deck_id: str) -> None:
    conn.execute(
        "DELETE FROM path_decks WHERE path_id = ? AND deck_id = ?",
        (path_id, deck_id),
    )


# ---------------------------------------------------------------------------
# Decks (Vocabulary Sets)
# ---------------------------------------------------------------------------

def _deserialize_deck_row(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    d = dict(row)
    if "tags" in d and isinstance(d["tags"], str):
        try:
            d["tags"] = json.loads(d["tags"])
        except Exception:
            d["tags"] = []
    elif "tags" not in d or d["tags"] is None:
        d["tags"] = []

    d["stats"] = {
        "total_cards": int(d.get("total_cards") or 0),
        "due_cards": int(d.get("due_reviews") or 0),
        "new_cards": int(d.get("new_cards") or 0),
    }
    return d


def create_deck(
    conn: sqlite3.Connection,
    deck_id: str,
    user_id: str,
    name: str,
    description: str = "",
    target_language: str = "en",
    tags: Optional[List[str]] = None,
    max_new_cards_per_day: Optional[int] = 10,
    max_reviews_per_day: Optional[int] = 50,
    daily_goal: Optional[int] = 20,
    preferred_duration: Optional[int] = 20,
    status: Optional[str] = "ACTIVE",
    icon: Optional[str] = "fa-folder",
    color: Optional[str] = "#3b82f6",
) -> Dict[str, Any]:
    now = _now_iso()
    tags_json = json.dumps(tags or [])
    effective_max_new = max_new_cards_per_day if max_new_cards_per_day is not None else 10
    effective_max_rev = max_reviews_per_day if max_reviews_per_day is not None else 50
    effective_goal = daily_goal if daily_goal is not None else 20
    effective_dur = preferred_duration if preferred_duration is not None else 20
    effective_status = status or "ACTIVE"
    effective_icon = icon or "fa-folder"
    effective_color = color or "#3b82f6"

    sql = """
    INSERT INTO decks (
        id, user_id, name, description, target_language, tags,
        max_new_cards_per_day, max_reviews_per_day, daily_goal, preferred_duration,
        status, icon, color, created_at, updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            deck_id,
            user_id,
            name,
            description,
            target_language,
            tags_json,
            effective_max_new,
            effective_max_rev,
            effective_goal,
            effective_dur,
            effective_status,
            effective_icon,
            effective_color,
            now,
            now,
        ),
    )
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
    return _deserialize_deck_row(row)


def list_decks_for_user(
    conn: sqlite3.Connection, user_id: str, learning_language: Optional[str] = None
) -> List[Dict[str, Any]]:
    clauses = ["d.user_id = ?"]
    params: List[Any] = [now_iso := _now_iso(), user_id]

    if learning_language:
        clauses.append("d.target_language = ?")
        params.append(learning_language)

    sql = f"""
    SELECT d.*, 
           COUNT(v.id) AS total_cards,
           SUM(CASE WHEN s.due_date <= ? AND s.state != 'NEW' THEN 1 ELSE 0 END) AS due_reviews,
           SUM(CASE WHEN s.state = 'NEW' THEN 1 ELSE 0 END) AS new_cards
    FROM decks d
    LEFT JOIN vocabulary_items v ON d.id = v.deck_id
    LEFT JOIN srs_cards s ON v.id = s.vocab_id
    WHERE {' AND '.join(clauses)}
    GROUP BY d.id
    ORDER BY d.created_at DESC
    """
    rows = conn.execute(sql, params).fetchall()
    return [_deserialize_deck_row(r) for r in rows]  # type: ignore


def update_deck(
    conn: sqlite3.Connection,
    deck_id: str,
    user_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    target_language: Optional[str] = None,
    tags: Optional[List[str]] = None,
    max_new_cards_per_day: Optional[int] = None,
    max_reviews_per_day: Optional[int] = None,
    daily_goal: Optional[int] = None,
    preferred_duration: Optional[int] = None,
    status: Optional[str] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    existing = get_deck_by_id(conn, deck_id, user_id)
    if not existing:
        return None

    now = _now_iso()
    set_clauses = ["updated_at = ?"]
    params: List[Any] = [now]

    if name is not None:
        set_clauses.append("name = ?")
        params.append(name)
    if description is not None:
        set_clauses.append("description = ?")
        params.append(description)
    if target_language is not None:
        set_clauses.append("target_language = ?")
        params.append(target_language)
    if tags is not None:
        set_clauses.append("tags = ?")
        params.append(json.dumps(tags))
    if max_new_cards_per_day is not None:
        set_clauses.append("max_new_cards_per_day = ?")
        params.append(max_new_cards_per_day)
    if max_reviews_per_day is not None:
        set_clauses.append("max_reviews_per_day = ?")
        params.append(max_reviews_per_day)
    if daily_goal is not None:
        set_clauses.append("daily_goal = ?")
        params.append(daily_goal)
    if preferred_duration is not None:
        set_clauses.append("preferred_duration = ?")
        params.append(preferred_duration)
    if status is not None:
        set_clauses.append("status = ?")
        params.append(status)
    if icon is not None:
        set_clauses.append("icon = ?")
        params.append(icon)
    if color is not None:
        set_clauses.append("color = ?")
        params.append(color)

    params.extend([deck_id, user_id])
    sql = f"UPDATE decks SET {', '.join(set_clauses)} WHERE id = ? AND user_id = ?"
    conn.execute(sql, params)
    return get_deck_by_id(conn, deck_id, user_id)


def delete_deck(
    conn: sqlite3.Connection, deck_id: str, user_id: str, delete_vocabulary: bool = False
) -> bool:
    deck = get_deck_by_id(conn, deck_id, user_id)
    if not deck:
        return False

    if not delete_vocabulary:
        # Reassign vocabulary to fallback deck so vocabulary is preserved
        target_lang = deck.get("target_language", "en")
        cursor = conn.execute(
            "SELECT id FROM decks WHERE user_id = ? AND target_language = ? AND id != ? ORDER BY created_at ASC LIMIT 1",
            (user_id, target_lang, deck_id),
        )
        row = cursor.fetchone()
        if row:
            fallback_id = row["id"]
        else:
            fallback_id = str(uuid.uuid4())
            create_deck(
                conn,
                deck_id=fallback_id,
                user_id=user_id,
                name=f"Từ Vựng Chung ({target_lang.upper()})",
                description="Bộ thẻ lưu trữ từ vựng",
                target_language=target_lang,
            )
        conn.execute(
            "UPDATE vocabulary_items SET deck_id = ? WHERE deck_id = ? AND user_id = ?",
            (fallback_id, deck_id, user_id),
        )
        conn.execute(
            "UPDATE srs_cards SET deck_id = ? WHERE deck_id = ? AND user_id = ?",
            (fallback_id, deck_id, user_id),
        )

    sql = "DELETE FROM decks WHERE id = ? AND user_id = ?"
    cursor = conn.execute(sql, (deck_id, user_id))
    return cursor.rowcount > 0


def list_user_tags(
    conn: sqlite3.Connection, user_id: str, language: Optional[str] = None
) -> List[str]:
    tags_set = set()
    deck_sql = "SELECT tags FROM decks WHERE user_id = ?"
    deck_params = [user_id]
    if language:
        deck_sql += " AND target_language = ?"
        deck_params.append(language)
    for r in conn.execute(deck_sql, deck_params).fetchall():
        try:
            t = json.loads(r["tags"] or "[]")
            if isinstance(t, list):
                tags_set.update(t)
        except Exception:
            pass

    vocab_sql = "SELECT tags FROM vocabulary_items WHERE user_id = ?"
    vocab_params = [user_id]
    if language:
        vocab_sql += " AND language = ?"
        vocab_params.append(language)
    for r in conn.execute(vocab_sql, vocab_params).fetchall():
        try:
            t = json.loads(r["tags"] or "[]")
            if isinstance(t, list):
                tags_set.update(t)
        except Exception:
            pass

    return sorted([t.strip() for t in tags_set if t and str(t).strip()])


# ---------------------------------------------------------------------------
# Vocabulary Items
# ---------------------------------------------------------------------------

def create_vocab_item(conn: sqlite3.Connection, item: Dict[str, Any]) -> Dict[str, Any]:
    now = _now_iso()
    examples_json = json.dumps(item.get("examples", []))
    synonyms_json = json.dumps(item.get("synonyms", []))
    antonyms_json = json.dumps(item.get("antonyms", []))
    tags_json = json.dumps(item.get("tags", []))
    vi_meanings_json = json.dumps(item.get("vietnamese_meanings", []))
    en_defs_json = json.dumps(item.get("english_definitions", []))
    lang_fields_json = json.dumps(item.get("language_specific_fields", {}))

    sql = """
    INSERT INTO vocabulary_items (
        id, deck_id, user_id, language, term, definition, ipa,
        part_of_speech, examples, synonyms, antonyms, notes,
        tags, root_word, root_word_id, vietnamese_meanings, english_definitions,
        mnemonics, audio_url, is_favorite, language_specific_fields, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            item.get("root_word", ""),
            item.get("root_word_id", None),
            vi_meanings_json,
            en_defs_json,
            item.get("mnemonics", ""),
            item.get("audio_url", ""),
            1 if item.get("is_favorite") else 0,
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
    for field in ("examples", "synonyms", "antonyms", "tags", "vietnamese_meanings", "english_definitions"):
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
    d["is_favorite"] = bool(d.get("is_favorite", 0))
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


def find_vocab_by_term_in_language(
    conn: sqlite3.Connection, user_id: str, language: str, term: str
) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM vocabulary_items WHERE user_id = ? AND language = ? AND LOWER(term) = LOWER(?) LIMIT 1"
    row = conn.execute(sql, (user_id, language, term.strip())).fetchone()
    return _deserialize_vocab_row(row)


def list_vocab_items(
    conn: sqlite3.Connection,
    deck_id: Optional[str] = None,
    user_id: Optional[str] = None,
    language: Optional[str] = None,
    path_id: Optional[str] = None,
    part_of_speech: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    clauses = []
    params: List[Any] = []

    if user_id:
        clauses.append("v.user_id = ?")
        params.append(user_id)
    if deck_id:
        clauses.append("v.deck_id = ?")
        params.append(deck_id)
    if language:
        clauses.append("v.language = ?")
        params.append(language)
    if part_of_speech:
        clauses.append("LOWER(v.part_of_speech) = LOWER(?)")
        params.append(part_of_speech)
    if is_favorite is not None:
        clauses.append("v.is_favorite = ?")
        params.append(1 if is_favorite else 0)
    if path_id:
        clauses.append("v.deck_id IN (SELECT deck_id FROM path_decks WHERE path_id = ?)")
        params.append(path_id)
    if search:
        clauses.append("(LOWER(v.term) LIKE ? OR LOWER(v.definition) LIKE ? OR LOWER(v.root_word) LIKE ?)")
        s = f"%{search.lower()}%"
        params.extend([s, s, s])

    where_str = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
    SELECT v.*, s.state as srs_state, s.due_date as srs_due_date, s.repetition_count as srs_reps
    FROM vocabulary_items v
    LEFT JOIN srs_cards s ON v.id = s.vocab_id
    {where_str}
    ORDER BY v.created_at DESC LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    rows = conn.execute(sql, params).fetchall()
    return [_deserialize_vocab_row(r) for r in rows if r]  # type: ignore


def list_vocab_items_by_deck(
    conn: sqlite3.Connection, deck_id: str, user_id: str, limit: int = 100, offset: int = 0
) -> List[Dict[str, Any]]:
    return list_vocab_items(conn, deck_id=deck_id, user_id=user_id, limit=limit, offset=offset)


def update_vocab_item(
    conn: sqlite3.Connection, vocab_id: str, user_id: str, updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    existing = get_vocab_item_by_id(conn, vocab_id, user_id)
    if not existing:
        return None

    now = _now_iso()
    set_clauses = ["updated_at = ?"]
    params: List[Any] = [now]

    simple_fields = [
        "term", "definition", "ipa", "part_of_speech", "notes",
        "language", "root_word", "root_word_id", "mnemonics", "audio_url"
    ]
    for field in simple_fields:
        if field in updates and updates[field] is not None:
            set_clauses.append(f"{field} = ?")
            params.append(updates[field])

    if "is_favorite" in updates and updates["is_favorite"] is not None:
        set_clauses.append("is_favorite = ?")
        params.append(1 if updates["is_favorite"] else 0)

    json_fields = [
        "examples", "synonyms", "antonyms", "tags",
        "vietnamese_meanings", "english_definitions", "language_specific_fields"
    ]
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
# Word Relationships (Root Word, Word Family, Synonyms, Antonyms)
# ---------------------------------------------------------------------------

def create_word_relationship(
    conn: sqlite3.Connection,
    rel_id: str,
    user_id: str,
    source_vocab_id: str,
    target_vocab_id: str,
    relation_type: str,
    notes: str = "",
) -> Dict[str, Any]:
    now = _now_iso()
    sql = """
    INSERT INTO word_relationships (id, user_id, source_vocab_id, target_vocab_id, relation_type, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(sql, (rel_id, user_id, source_vocab_id, target_vocab_id, relation_type, notes, now))
    return {
        "id": rel_id,
        "user_id": user_id,
        "source_vocab_id": source_vocab_id,
        "target_vocab_id": target_vocab_id,
        "relation_type": relation_type,
        "notes": notes,
        "created_at": now,
    }


def list_relationships_for_vocab(
    conn: sqlite3.Connection, vocab_id: str, user_id: str
) -> List[Dict[str, Any]]:
    sql = """
    SELECT r.*, v.term as target_term, v.definition as target_definition, v.ipa as target_ipa
    FROM word_relationships r
    JOIN vocabulary_items v ON r.target_vocab_id = v.id
    WHERE r.source_vocab_id = ? AND r.user_id = ?
    """
    rows = conn.execute(sql, (vocab_id, user_id)).fetchall()
    return [dict(r) for r in rows]


def delete_word_relationship(conn: sqlite3.Connection, rel_id: str, user_id: str) -> bool:
    sql = "DELETE FROM word_relationships WHERE id = ? AND user_id = ?"
    cursor = conn.execute(sql, (rel_id, user_id))
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Spaced Repetition (SRS) Cards
# ---------------------------------------------------------------------------

def create_srs_card(conn: sqlite3.Connection, card: Dict[str, Any]) -> Dict[str, Any]:
    existing = get_srs_card_by_vocab_id(conn, card["vocab_id"])
    if existing:
        return existing

    now = _now_iso()
    sql = """
    INSERT INTO srs_cards (
        id, vocab_id, deck_id, user_id, state, step_index,
        repetition_count, interval_days, ease_factor, due_date,
        last_reviewed_at, lapses, history_count, difficulty, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            card.get("lapses", 0),
            card.get("history_count", 0),
            card.get("difficulty", 0.3),
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
    lapses: Optional[int] = None,
    history_count: Optional[int] = None,
    difficulty: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    existing = get_srs_card_by_id(conn, card_id, user_id)
    if not existing:
        return None

    cur_lapses = lapses if lapses is not None else existing.get("lapses", 0)
    cur_history = history_count if history_count is not None else (existing.get("history_count", 0) + 1)
    cur_diff = difficulty if difficulty is not None else existing.get("difficulty", 0.3)

    sql = """
    UPDATE srs_cards
    SET state = ?, step_index = ?, repetition_count = ?, interval_days = ?,
        ease_factor = ?, due_date = ?, last_reviewed_at = ?,
        lapses = ?, history_count = ?, difficulty = ?
    WHERE id = ? AND user_id = ?
    """
    conn.execute(
        sql,
        (
            state,
            step_index,
            repetition_count,
            interval_days,
            ease_factor,
            due_date,
            last_reviewed_at,
            cur_lapses,
            cur_history,
            cur_diff,
            card_id,
            user_id,
        ),
    )
    return get_srs_card_by_id(conn, card_id, user_id)


def get_due_review_cards(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    path_id: Optional[str] = None,
    learning_language: Optional[str] = None,
    as_of_iso: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    as_of = as_of_iso or _now_iso()
    clauses = ["s.user_id = ?", "s.state != 'NEW'", "s.due_date <= ?"]
    params: List[Any] = [user_id, as_of]

    if deck_id:
        clauses.append("s.deck_id = ?")
        params.append(deck_id)
    elif path_id:
        clauses.append("s.deck_id IN (SELECT deck_id FROM path_decks WHERE path_id = ?)")
        params.append(path_id)

    if learning_language:
        clauses.append("v.language = ?")
        params.append(learning_language)

    sql = f"""
    SELECT s.*, v.term, v.definition, v.language, v.ipa, v.part_of_speech,
           v.language_specific_fields, v.examples, v.root_word, v.audio_url
    FROM srs_cards s
    JOIN vocabulary_items v ON s.vocab_id = v.id
    WHERE {' AND '.join(clauses)}
    ORDER BY s.due_date ASC
    LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    results = []
    for r in rows:
        d = dict(r)
        if "language_specific_fields" in d and isinstance(d["language_specific_fields"], str):
            try:
                d["language_specific_fields"] = json.loads(d["language_specific_fields"])
            except Exception:
                d["language_specific_fields"] = {}
        if "examples" in d and isinstance(d["examples"], str):
            try:
                d["examples"] = json.loads(d["examples"])
            except Exception:
                d["examples"] = []
        results.append(d)
    return results


def get_new_cards(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    path_id: Optional[str] = None,
    learning_language: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    clauses = ["s.user_id = ?", "s.state = 'NEW'"]
    params: List[Any] = [user_id]

    if deck_id:
        clauses.append("s.deck_id = ?")
        params.append(deck_id)
    elif path_id:
        clauses.append("s.deck_id IN (SELECT deck_id FROM path_decks WHERE path_id = ?)")
        params.append(path_id)

    if learning_language:
        clauses.append("v.language = ?")
        params.append(learning_language)

    sql = f"""
    SELECT s.*, v.term, v.definition, v.language, v.ipa, v.part_of_speech,
           v.language_specific_fields, v.examples, v.root_word, v.audio_url
    FROM srs_cards s
    JOIN vocabulary_items v ON s.vocab_id = v.id
    WHERE {' AND '.join(clauses)}
    ORDER BY s.created_at ASC
    LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    results = []
    for r in rows:
        d = dict(r)
        if "language_specific_fields" in d and isinstance(d["language_specific_fields"], str):
            try:
                d["language_specific_fields"] = json.loads(d["language_specific_fields"])
            except Exception:
                d["language_specific_fields"] = {}
        if "examples" in d and isinstance(d["examples"], str):
            try:
                d["examples"] = json.loads(d["examples"])
            except Exception:
                d["examples"] = []
        results.append(d)
    return results


def get_reinforcement_cards(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    path_id: Optional[str] = None,
    learning_language: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    clauses = ["s.user_id = ?"]
    params: List[Any] = [user_id]

    if deck_id:
        clauses.append("s.deck_id = ?")
        params.append(deck_id)
    elif path_id:
        clauses.append("s.deck_id IN (SELECT deck_id FROM path_decks WHERE path_id = ?)")
        params.append(path_id)

    if learning_language:
        clauses.append("v.language = ?")
        params.append(learning_language)

    sql = f"""
    SELECT s.*, v.term, v.definition, v.language, v.ipa, v.part_of_speech,
           v.language_specific_fields, v.examples, v.root_word, v.audio_url
    FROM srs_cards s
    JOIN vocabulary_items v ON s.vocab_id = v.id
    WHERE {' AND '.join(clauses)}
    ORDER BY 
        CASE WHEN s.state IN ('RELEARNING', 'LEARNING') OR s.lapses > 0 THEN 0 ELSE 1 END ASC,
        s.due_date ASC,
        s.created_at ASC
    LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    results = []
    for r in rows:
        d = dict(r)
        if "language_specific_fields" in d and isinstance(d["language_specific_fields"], str):
            try:
                d["language_specific_fields"] = json.loads(d["language_specific_fields"])
            except Exception:
                d["language_specific_fields"] = {}
        if "examples" in d and isinstance(d["examples"], str):
            try:
                d["examples"] = json.loads(d["examples"])
            except Exception:
                d["examples"] = []
        results.append(d)
    return results


def get_lapsed_or_weak_cards(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    path_id: Optional[str] = None,
    learning_language: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    clauses = ["s.user_id = ?", "(s.lapses > 0 OR s.state IN ('RELEARNING', 'LEARNING') OR s.ease_factor < 2.3)"]
    params: List[Any] = [user_id]

    if deck_id:
        clauses.append("s.deck_id = ?")
        params.append(deck_id)
    elif path_id:
        clauses.append("s.deck_id IN (SELECT deck_id FROM path_decks WHERE path_id = ?)")
        params.append(path_id)

    if learning_language:
        clauses.append("v.language = ?")
        params.append(learning_language)

    sql = f"""
    SELECT s.*, v.term, v.definition, v.language, v.ipa, v.part_of_speech,
           v.language_specific_fields, v.examples, v.root_word, v.audio_url
    FROM srs_cards s
    JOIN vocabulary_items v ON s.vocab_id = v.id
    WHERE {' AND '.join(clauses)}
    ORDER BY s.lapses DESC, s.ease_factor ASC, s.due_date ASC
    LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    results = []
    for r in rows:
        d = dict(r)
        if "language_specific_fields" in d and isinstance(d["language_specific_fields"], str):
            try:
                d["language_specific_fields"] = json.loads(d["language_specific_fields"])
            except Exception:
                d["language_specific_fields"] = {}
        if "examples" in d and isinstance(d["examples"], str):
            try:
                d["examples"] = json.loads(d["examples"])
            except Exception:
                d["examples"] = []
        results.append(d)
    return results


def get_due_and_new_counts(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    path_id: Optional[str] = None,
    learning_language: Optional[str] = None,
    as_of_iso: Optional[str] = None,
) -> Dict[str, int]:
    as_of = as_of_iso or _now_iso()
    clauses = ["s.user_id = ?"]
    params: List[Any] = [as_of, user_id]

    if deck_id:
        clauses.append("s.deck_id = ?")
        params.append(deck_id)
    elif path_id:
        clauses.append("s.deck_id IN (SELECT deck_id FROM path_decks WHERE path_id = ?)")
        params.append(path_id)

    if learning_language:
        clauses.append("v.language = ?")
        params.append(learning_language)

    where_str = f"WHERE {' AND '.join(clauses)}"
    sql = f"""
    SELECT 
        SUM(CASE WHEN s.state = 'NEW' THEN 1 ELSE 0 END) AS new_count,
        SUM(CASE WHEN s.state != 'NEW' AND s.due_date <= ? THEN 1 ELSE 0 END) AS due_count,
        SUM(CASE WHEN s.state = 'REVIEW' THEN 1 ELSE 0 END) AS learned_count,
        COUNT(s.id) AS total_cards
    FROM srs_cards s
    JOIN vocabulary_items v ON s.vocab_id = v.id
    {where_str}
    """
    row = conn.execute(sql, params).fetchone()
    return {
        "new_count": (row["new_count"] or 0) if row else 0,
        "due_count": (row["due_count"] or 0) if row else 0,
        "learned_count": (row["learned_count"] or 0) if row else 0,
        "total_cards": (row["total_cards"] or 0) if row else 0,
    }


# ---------------------------------------------------------------------------
# Learning Sessions (20-Minute Workflow & Recoverable State)
# ---------------------------------------------------------------------------

def create_session(conn: sqlite3.Connection, session: Dict[str, Any]) -> Dict[str, Any]:
    now = _now_iso()
    queue_json = json.dumps(session.get("card_ids_queue", []))
    durations_json = json.dumps(session.get("phase_durations", {}))
    phase_data_json = json.dumps(session.get("phase_data", {}))

    sql = """
    INSERT INTO learning_sessions (
        id, user_id, deck_id, path_id, learning_language, title, session_date, session_type, current_phase,
        status, card_ids_queue, current_index, total_cards, completed_cards,
        correct_count, incorrect_count, phase_durations, phase_data, phase_target_seconds,
        start_time, end_time, last_active_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            session["id"],
            session["user_id"],
            session.get("deck_id"),
            session.get("path_id"),
            session.get("learning_language", "en"),
            session["title"],
            session.get("session_date", now[:10]),
            session.get("session_type", "daily_20min"),
            session.get("current_phase", "review"),
            session.get("status", "ACTIVE"),
            queue_json,
            session.get("current_index", 0),
            session.get("total_cards", len(session.get("card_ids_queue", []))),
            session.get("completed_cards", 0),
            session.get("correct_count", 0),
            session.get("incorrect_count", 0),
            durations_json,
            phase_data_json,
            session.get("phase_target_seconds", 1200),
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
    for field in ("card_ids_queue", "phase_durations", "phase_data"):
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = [] if field == "card_ids_queue" else {}
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
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    path_id: Optional[str] = None,
    learning_language: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    clauses = ["user_id = ?", "status IN ('ACTIVE', 'PAUSED')"]
    params: List[Any] = [user_id]
    if deck_id:
        clauses.append("(deck_id = ? OR deck_id IS NULL)")
        params.append(deck_id)
    if path_id:
        clauses.append("(path_id = ? OR path_id IS NULL)")
        params.append(path_id)
    if learning_language:
        clauses.append("(learning_language = ? OR learning_language IS NULL)")
        params.append(learning_language)

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
        if k in ("card_ids_queue", "phase_durations", "phase_data") and isinstance(v, (list, dict)):
            set_clauses.append(f"{k} = ?")
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
        time_spent_seconds, exercise_type, user_response, is_correct,
        scheduled_next_interval, was_new_card, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            log.get("exercise_type", "flashcard"),
            log.get("user_response", ""),
            1 if log.get("is_correct", True) else 0,
            log.get("scheduled_next_interval", 0.0),
            1 if log.get("was_new_card", 0) else 0,
            now,
        ),
    )
    return log


def get_daily_study_progress(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    learning_language: Optional[str] = None,
    study_date: Optional[str] = None,
) -> Dict[str, int]:
    date_str = study_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    clauses = ["l.user_id = ?", "DATE(l.created_at) = ?"]
    params: List[Any] = [user_id, date_str]

    if deck_id:
        clauses.append("s.deck_id = ?")
        params.append(deck_id)
    if learning_language:
        clauses.append("v.language = ?")
        params.append(learning_language)

    where_sql = " AND ".join(clauses)
    sql = f"""
    SELECT 
        COUNT(DISTINCT CASE WHEN l.exercise_type = 'new_words' OR l.was_new_card = 1 THEN l.card_id END) AS new_studied,
        COUNT(DISTINCT CASE WHEN l.exercise_type != 'new_words' AND l.was_new_card = 0 THEN l.card_id END) AS reviews_studied
    FROM session_card_logs l
    JOIN srs_cards s ON l.card_id = s.id
    JOIN vocabulary_items v ON s.vocab_id = v.id
    WHERE {where_sql}
    """
    row = conn.execute(sql, params).fetchone()
    return {
        "new_cards_studied_today": (row["new_studied"] or 0) if row else 0,
        "review_cards_studied_today": (row["reviews_studied"] or 0) if row else 0,
    }


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


def get_vocab_study_history(
    conn: sqlite3.Connection, vocab_id: str, user_id: str, limit: int = 50
) -> Dict[str, Any]:
    vocab = get_vocab_item_by_id(conn, vocab_id, user_id)
    srs_card = get_srs_card_by_vocab_id(conn, vocab_id)

    sql = """
    SELECT l.*, s.interval_days as card_interval, s.state as card_state
    FROM session_card_logs l
    JOIN srs_cards s ON l.card_id = s.id
    WHERE s.vocab_id = ? AND l.user_id = ?
    ORDER BY l.created_at DESC
    LIMIT ?
    """
    rows = conn.execute(sql, (vocab_id, user_id, limit)).fetchall()
    logs = [dict(r) for r in rows]

    total_attempts = len(logs)
    correct_count = sum(1 for l in logs if l.get("is_correct"))
    retention_rate = round((correct_count / total_attempts * 100), 1) if total_attempts > 0 else 0.0

    return {
        "vocab_id": vocab_id,
        "term": vocab.get("term") if vocab else "",
        "definition": vocab.get("definition") if vocab else "",
        "ipa": vocab.get("ipa") if vocab else "",
        "language": vocab.get("language") if vocab else "en",
        "total_attempts": total_attempts,
        "correct_count": correct_count,
        "incorrect_count": total_attempts - correct_count,
        "retention_rate": retention_rate,
        "srs_card": srs_card,
        "history": logs,
    }


def get_srs_distribution(
    conn: sqlite3.Connection,
    user_id: str,
    learning_language: Optional[str] = None,
    deck_id: Optional[str] = None,
) -> Dict[str, Any]:
    clauses = ["s.user_id = ?"]
    params: List[Any] = [user_id]
    if learning_language:
        clauses.append("v.language = ?")
        params.append(learning_language)
    if deck_id:
        clauses.append("s.deck_id = ?")
        params.append(deck_id)

    where_sql = f"WHERE {' AND '.join(clauses)}"
    sql = f"""
    SELECT
        COUNT(s.id) AS total_cards,
        SUM(CASE WHEN s.interval_days <= 1.0 OR s.state IN ('NEW', 'RELEARNING') THEN 1 ELSE 0 END) AS box_1_day,
        SUM(CASE WHEN s.interval_days > 1.0 AND s.interval_days <= 3.0 THEN 1 ELSE 0 END) AS box_3_days,
        SUM(CASE WHEN s.interval_days > 3.0 AND s.interval_days <= 7.0 THEN 1 ELSE 0 END) AS box_7_days,
        SUM(CASE WHEN s.interval_days > 7.0 AND s.interval_days <= 14.0 THEN 1 ELSE 0 END) AS box_14_days,
        SUM(CASE WHEN s.interval_days > 14.0 THEN 1 ELSE 0 END) AS box_30_plus_days,
        SUM(CASE WHEN s.lapses > 0 OR s.state = 'RELEARNING' THEN 1 ELSE 0 END) AS lapsed_count
    FROM srs_cards s
    JOIN vocabulary_items v ON s.vocab_id = v.id
    {where_sql}
    """
    row = conn.execute(sql, params).fetchone()
    if not row:
        return {
            "total_cards": 0,
            "box_1_day": 0,
            "box_3_days": 0,
            "box_7_days": 0,
            "box_14_days": 0,
            "box_30_plus_days": 0,
            "lapsed_count": 0,
        }
    return {
        "total_cards": int(row["total_cards"] or 0),
        "box_1_day": int(row["box_1_day"] or 0),
        "box_3_days": int(row["box_3_days"] or 0),
        "box_7_days": int(row["box_7_days"] or 0),
        "box_14_days": int(row["box_14_days"] or 0),
        "box_30_plus_days": int(row["box_30_plus_days"] or 0),
        "lapsed_count": int(row["lapsed_count"] or 0),
    }


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
# Practice Submissions (Writing & Typing)
# ---------------------------------------------------------------------------

def create_practice_submission(
    conn: sqlite3.Connection,
    sub_id: str,
    user_id: str,
    vocab_id: Optional[str],
    practice_type: str,
    prompt: str,
    user_text: str,
    model_answer: str = "",
    self_assessment_score: int = 4,
) -> Dict[str, Any]:
    now = _now_iso()
    sql = """
    INSERT INTO practice_submissions (
        id, user_id, vocab_id, practice_type, prompt, user_text,
        model_answer, self_assessment_score, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            sub_id,
            user_id,
            vocab_id,
            practice_type,
            prompt,
            user_text,
            model_answer,
            self_assessment_score,
            now,
        ),
    )
    return {
        "id": sub_id,
        "user_id": user_id,
        "vocab_id": vocab_id,
        "practice_type": practice_type,
        "prompt": prompt,
        "user_text": user_text,
        "model_answer": model_answer,
        "self_assessment_score": self_assessment_score,
        "created_at": now,
    }


record_practice_submission = create_practice_submission


def list_practice_submissions(
    conn: sqlite3.Connection, user_id: str, limit: int = 20
) -> List[Dict[str, Any]]:
    sql = """
    SELECT p.*, v.term as vocab_term, v.language as vocab_language
    FROM practice_submissions p
    LEFT JOIN vocabulary_items v ON p.vocab_id = v.id
    WHERE p.user_id = ?
    ORDER BY p.created_at DESC
    LIMIT ?
    """
    rows = conn.execute(sql, (user_id, limit)).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Study Logs, Streaks, & Skill Progress
# ---------------------------------------------------------------------------

def record_study_activity(
    conn: sqlite3.Connection,
    user_id: str,
    study_date: str,
    learning_language: str,
    duration_seconds: float,
    cards_reviewed: int,
    new_words_learned: int,
) -> None:
    now = _now_iso()
    log_id = str(uuid.uuid4())
    sql = """
    INSERT INTO user_study_logs (
        id, user_id, study_date, learning_language, duration_seconds,
        cards_reviewed, new_words_learned, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (
            log_id,
            user_id,
            study_date,
            learning_language,
            duration_seconds,
            cards_reviewed,
            new_words_learned,
            now,
        ),
    )


def get_user_streak(
    conn: sqlite3.Connection, user_id: str, learning_language: Optional[str] = None
) -> Dict[str, Any]:
    clauses = ["user_id = ?"]
    params: List[Any] = [user_id]
    if learning_language:
        clauses.append("learning_language = ?")
        params.append(learning_language)

    sql = f"""
    SELECT DISTINCT study_date
    FROM user_study_logs
    WHERE {' AND '.join(clauses)}
    ORDER BY study_date DESC
    """
    rows = conn.execute(sql, params).fetchall()
    dates = [r["study_date"] for r in rows]

    if not dates:
        return {"current_streak": 0, "longest_streak": 0, "active_days_count": 0}

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    today_str = today.isoformat()
    yesterday_str = yesterday.isoformat()

    # Calculate current streak
    current_streak = 0
    check_date = today if (today_str in dates) else (yesterday if (yesterday_str in dates) else None)

    if check_date:
        while True:
            if check_date.isoformat() in dates:
                current_streak += 1
                check_date = check_date - timedelta(days=1)
            else:
                break

    # Calculate longest streak
    sorted_unique_dates = sorted(
        [datetime.fromisoformat(d).date() for d in dates]
    )
    longest_streak = 0
    temp_streak = 0
    prev_d = None

    for d in sorted_unique_dates:
        if prev_d is None or d == prev_d + timedelta(days=1):
            temp_streak += 1
        elif d > prev_d + timedelta(days=1):
            temp_streak = 1
        prev_d = d
        if temp_streak > longest_streak:
            longest_streak = temp_streak

    return {
        "current_streak": current_streak,
        "longest_streak": max(longest_streak, current_streak),
        "active_days_count": len(dates),
    }


def get_user_study_calendar(
    conn: sqlite3.Connection, user_id: str, days: int = 90
) -> List[Dict[str, Any]]:
    start_date = (datetime.now(timezone.utc).date() - timedelta(days=days)).isoformat()
    sql = """
    SELECT study_date, 
           SUM(duration_seconds) as total_duration,
           SUM(cards_reviewed) as total_reviewed,
           SUM(new_words_learned) as total_new
    FROM user_study_logs
    WHERE user_id = ? AND study_date >= ?
    GROUP BY study_date
    ORDER BY study_date ASC
    """
    rows = conn.execute(sql, (user_id, start_date)).fetchall()
    return [dict(r) for r in rows]


def get_skill_breakdown(
    conn: sqlite3.Connection, user_id: str, learning_language: str = "en"
) -> Dict[str, Any]:
    """Calculate separated skill competencies based on actual review logs."""
    sql = """
    SELECT l.exercise_type,
           COUNT(*) as total_attempts,
           SUM(CASE WHEN l.rating >= 3 THEN 1 ELSE 0 END) as successful_attempts
    FROM session_card_logs l
    JOIN vocabulary_items v ON l.card_id = v.id OR l.card_id IN (SELECT id FROM srs_cards WHERE vocab_id = v.id)
    WHERE l.user_id = ? AND v.language = ?
    GROUP BY l.exercise_type
    """
    rows = conn.execute(sql, (user_id, learning_language)).fetchall()
    skills_map = {}
    for r in rows:
        ex = r["exercise_type"]
        tot = r["total_attempts"]
        succ = r["successful_attempts"]
        pct = round(succ / tot * 100, 1) if tot > 0 else 0.0
        skills_map[ex] = {"attempts": tot, "accuracy_pct": pct}

    # Define language-specific skills
    if learning_language == "zh":
        default_skills = {
            "hanzi_recognition": skills_map.get("hanzi_to_meaning", {"attempts": 0, "accuracy_pct": 100.0}),
            "pinyin_recall": skills_map.get("hanzi_to_pinyin", {"attempts": 0, "accuracy_pct": 100.0}),
            "tone_practice": skills_map.get("tone_recognition", {"attempts": 0, "accuracy_pct": 100.0}),
            "chinese_typing": skills_map.get("hanzi_typing", {"attempts": 0, "accuracy_pct": 100.0}),
            "listening": skills_map.get("audio_to_meaning", {"attempts": 0, "accuracy_pct": 100.0}),
        }
    else:
        default_skills = {
            "meaning_recall": skills_map.get("word_to_meaning", {"attempts": 0, "accuracy_pct": 100.0}),
            "spelling": skills_map.get("spelling", {"attempts": 0, "accuracy_pct": 100.0}),
            "listening": skills_map.get("audio_to_meaning", {"attempts": 0, "accuracy_pct": 100.0}),
            "sentence_usage": skills_map.get("sentence_writing", {"attempts": 0, "accuracy_pct": 100.0}),
        }

    return default_skills


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


def seed_sample_template_deck(
    conn: sqlite3.Connection,
    user_id: str,
    language: str = "en",
    deck_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Seed a sample vocabulary template deck with 5 rich words for the user."""
    deck_id = str(uuid.uuid4())
    name = deck_name or ("Bộ Từ Vựng Mẫu (Sample Template)" if language == "en" else "Bộ Từ Vựng Tiếng Trung Mẫu (Sample Template)")
    description = "Bộ thẻ từ vựng mẫu chuẩn - bạn có thể bấm nút 'Đổi tên' để chỉnh sửa tên bộ thẻ này theo ý muốn!"
    
    deck = create_deck(
        conn,
        deck_id=deck_id,
        user_id=user_id,
        name=name,
        description=description,
        target_language=language,
        tags=["mau", "template"]
    )

    if language == "zh":
        sample_words = [
            {
                "term": "努力",
                "part_of_speech": "verb",
                "definition": "nỗ lực, cố gắng hết mình",
                "language_specific_fields": {"pinyin": "nǔ lì", "hsk_level": "3"},
                "examples": ["我们要努力学习汉语。"]
            },
            {
                "term": "坚持",
                "part_of_speech": "verb",
                "definition": "kiên trì, bền lòng",
                "language_specific_fields": {"pinyin": "jiān chí", "hsk_level": "3"},
                "examples": ["只要坚持，就一定会成功。"]
            },
            {
                "term": "热情",
                "part_of_speech": "adjective",
                "definition": "nhiệt tình, niềm nở",
                "language_specific_fields": {"pinyin": "rè qíng", "hsk_level": "3"},
                "examples": ["他对每个人都非常热情。"]
            },
            {
                "term": "希望",
                "part_of_speech": "verb",
                "definition": "hy vọng, mong đợi",
                "language_specific_fields": {"pinyin": "xī wàng", "hsk_level": "2"},
                "examples": ["希望你一切顺利。"]
            },
            {
                "term": "成功",
                "part_of_speech": "noun",
                "definition": "thành công, thắng lợi",
                "language_specific_fields": {"pinyin": "chéng gōng", "hsk_level": "3"},
                "examples": ["失败是成功之母。"]
            }
        ]
    else:
        sample_words = [
            {
                "term": "resilient",
                "ipa": "/rɪˈzɪl.jənt/",
                "part_of_speech": "adjective",
                "definition": "có khả năng phục hồi nhanh chóng, kiên cường",
                "root_word": "resilience",
                "examples": [
                    "The local economy proved remarkably resilient.",
                    "She is remarkably resilient in difficult times."
                ]
            },
            {
                "term": "perseverance",
                "ipa": "/ˌpɜː.sɪˈvɪə.rəns/",
                "part_of_speech": "noun",
                "definition": "sự kiên trì, bền chí theo đuổi mục tiêu",
                "root_word": "persevere",
                "examples": [
                    "His perseverance led to great academic success.",
                    "Success requires continuous perseverance."
                ]
            },
            {
                "term": "serendipity",
                "ipa": "/ˌser.ənˈdɪp.ə.ti/",
                "part_of_speech": "noun",
                "definition": "sự tình cờ may mắn, cơ duyên bất ngờ",
                "examples": [
                    "Finding this wonderful book was pure serendipity.",
                    "A fortunate stroke of serendipity brought them together."
                ]
            },
            {
                "term": "eloquent",
                "ipa": "/ˈel.ə.kwənt/",
                "part_of_speech": "adjective",
                "definition": "hùng biện, có tài ăn nói lưu loát và truyền cảm",
                "examples": [
                    "She gave an eloquent speech at the opening ceremony."
                ]
            },
            {
                "term": "epiphany",
                "ipa": "/ɪˈpɪf.ən.i/",
                "part_of_speech": "noun",
                "definition": "sự giác ngộ, nhận thức bừng sáng bất ngờ",
                "examples": [
                    "He experienced a sudden epiphany that changed his perspective."
                ]
            }
        ]

    for item_data in sample_words:
        vocab_id = str(uuid.uuid4())
        item_data.update({
            "id": vocab_id,
            "deck_id": deck_id,
            "user_id": user_id,
            "language": language,
        })
        create_vocab_item(conn, item_data)
        create_srs_card(conn, {
            "id": str(uuid.uuid4()),
            "vocab_id": vocab_id,
            "deck_id": deck_id,
            "user_id": user_id,
            "state": "NEW",
            "step_index": 0,
            "repetition_count": 0,
            "interval_days": 0.0,
            "ease_factor": 2.5,
            "due_date": _now_iso(),
            "difficulty": 0.3,
        })

    return get_deck_by_id(conn, deck_id, user_id)  # type: ignore


def reset_user_vocabulary(
    conn: sqlite3.Connection,
    user_id: str,
    language: Optional[str] = None
) -> Dict[str, Any]:
    """Delete all vocabulary, cards, and decks for user, then seed 1 sample template deck."""
    if language:
        # Delete only decks and cards of specified language
        deck_rows = conn.execute("SELECT id FROM decks WHERE user_id = ? AND target_language = ?", (user_id, language)).fetchall()
        deck_ids = [r["id"] for r in deck_rows]
        if deck_ids:
            placeholders = ",".join("?" for _ in deck_ids)
            conn.execute(f"DELETE FROM srs_cards WHERE deck_id IN ({placeholders})", deck_ids)
            conn.execute(f"DELETE FROM vocabulary_items WHERE deck_id IN ({placeholders})", deck_ids)
            conn.execute(f"DELETE FROM decks WHERE id IN ({placeholders})", deck_ids)
    else:
        conn.execute("DELETE FROM srs_cards WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM vocabulary_items WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM learning_sessions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM session_card_logs WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM practice_submissions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM word_relationships WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM decks WHERE user_id = ?", (user_id,))

    # Seed 1 clean template deck
    target_lang = language or "en"
    template_deck = seed_sample_template_deck(conn, user_id=user_id, language=target_lang)
    return template_deck

