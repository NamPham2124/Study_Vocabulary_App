"""Recoverable Daily Learning Session Manager."""

from datetime import datetime, timezone
import json
import uuid
from typing import Any, Dict, List, Optional
import sqlite3

from vocabmaster.config import settings
from vocabmaster.db import repository
from vocabmaster.srs.scheduler import review_card


def start_or_resume_session(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    new_card_limit: Optional[int] = None,
    review_limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Start a new daily session or automatically recover an unfinished active/paused session.
    """
    # 1. Check for recoverable existing active or paused session
    existing = repository.get_active_or_paused_session(conn, user_id, deck_id)
    if existing:
        if existing["status"] == "PAUSED":
            # Resume it
            existing = repository.update_session(
                conn, existing["id"], user_id, status="ACTIVE"
            )
        current_card = get_current_card(conn, existing["id"], user_id)
        return {
            "session": existing,
            "recovered": True,
            "current_card": current_card,
        }

    # 2. Build a fresh daily queue
    limit_new = new_card_limit if new_card_limit is not None else settings.default_new_cards_per_day
    limit_rev = review_limit if review_limit is not None else settings.default_reviews_per_day

    due_reviews = repository.get_due_review_cards(conn, user_id, deck_id=deck_id, limit=limit_rev)
    new_cards = repository.get_new_cards(conn, user_id, deck_id=deck_id, limit=limit_new)

    queue_ids: List[str] = [c["id"] for c in due_reviews] + [c["id"] for c in new_cards]

    session_id = str(uuid.uuid4())
    deck_name = "All Decks"
    if deck_id:
        deck = repository.get_deck_by_id(conn, deck_id, user_id)
        if deck:
            deck_name = deck["name"]

    now = datetime.now(timezone.utc).isoformat()
    session_data = {
        "id": session_id,
        "user_id": user_id,
        "deck_id": deck_id,
        "title": f"Daily Study - {deck_name} ({now[:10]})",
        "session_date": now[:10],
        "status": "ACTIVE" if queue_ids else "COMPLETED",
        "card_ids_queue": queue_ids,
        "current_index": 0,
        "total_cards": len(queue_ids),
        "completed_cards": 0,
        "correct_count": 0,
        "incorrect_count": 0,
        "start_time": now,
        "end_time": now if not queue_ids else None,
    }

    created = repository.create_session(conn, session_data)
    current_card = get_current_card(conn, session_id, user_id) if queue_ids else None

    return {
        "session": created,
        "recovered": False,
        "current_card": current_card,
    }


def get_current_card(
    conn: sqlite3.Connection, session_id: str, user_id: str
) -> Optional[Dict[str, Any]]:
    """Get the active card data for the session's current position."""
    session = repository.get_session_by_id(conn, session_id, user_id)
    if not session:
        return None

    queue = session.get("card_ids_queue", [])
    idx = session.get("current_index", 0)

    if idx >= len(queue):
        if session["status"] != "COMPLETED":
            now = datetime.now(timezone.utc).isoformat()
            repository.update_session(
                conn, session_id, user_id, status="COMPLETED", end_time=now
            )
        return None

    card_id = queue[idx]
    srs_card = repository.get_srs_card_by_id(conn, card_id, user_id)
    if not srs_card:
        return None

    vocab_item = repository.get_vocab_item_by_id(conn, srs_card["vocab_id"], user_id)
    if not vocab_item:
        return None

    return {
        "session_id": session_id,
        "current_index": idx,
        "total_cards": len(queue),
        "card_id": srs_card["id"],
        "vocab_id": vocab_item["id"],
        "term": vocab_item["term"],
        "definition": vocab_item["definition"],
        "ipa": vocab_item["ipa"],
        "part_of_speech": vocab_item["part_of_speech"],
        "examples": vocab_item["examples"],
        "synonyms": vocab_item["synonyms"],
        "antonyms": vocab_item["antonyms"],
        "notes": vocab_item["notes"],
        "tags": vocab_item["tags"],
        "language": vocab_item["language"],
        "language_specific_fields": vocab_item["language_specific_fields"],
        "state": srs_card["state"],
        "repetition_count": srs_card["repetition_count"],
        "ease_factor": srs_card["ease_factor"],
        "interval_days": srs_card["interval_days"],
    }


def submit_card_answer(
    conn: sqlite3.Connection,
    session_id: str,
    user_id: str,
    rating: int,
    time_spent_seconds: float = 0.0,
    requeue_failed_cards: bool = True,
) -> Dict[str, Any]:
    """
    Record answer for current card, update SRS card, increment index, and persist state.
    Resilient to interruptions at every step.
    """
    session = repository.get_session_by_id(conn, session_id, user_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")
    if session["status"] not in ("ACTIVE", "PAUSED"):
        raise ValueError(f"Cannot submit answer to session with status {session['status']}")

    queue = session.get("card_ids_queue", [])
    idx = session.get("current_index", 0)

    if idx >= len(queue):
        raise ValueError("Session is already completed")

    card_id = queue[idx]

    # 1. Update SRS card
    updated_card = review_card(conn, card_id, user_id, rating)

    # 2. Record individual card log
    log_id = str(uuid.uuid4())
    repository.record_card_log(
        conn,
        {
            "id": log_id,
            "session_id": session_id,
            "card_id": card_id,
            "user_id": user_id,
            "rating": rating,
            "time_spent_seconds": time_spent_seconds,
            "scheduled_next_interval": updated_card["interval_days"],
        },
    )

    # 3. Update session metrics
    is_correct = rating >= 3
    correct_count = session["correct_count"] + (1 if is_correct else 0)
    incorrect_count = session["incorrect_count"] + (0 if is_correct else 1)
    completed_cards = session["completed_cards"] + 1
    next_idx = idx + 1

    # If failed and requeue enabled, append to current queue for intraday review
    if not is_correct and requeue_failed_cards:
        queue.append(card_id)

    is_completed = next_idx >= len(queue)
    now = datetime.now(timezone.utc).isoformat()
    status = "COMPLETED" if is_completed else "ACTIVE"
    end_time = now if is_completed else session.get("end_time")

    updated_session = repository.update_session(
        conn,
        session_id,
        user_id,
        status=status,
        card_ids_queue=queue,
        current_index=next_idx,
        total_cards=len(queue),
        completed_cards=completed_cards,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        end_time=end_time,
    )

    next_card = get_current_card(conn, session_id, user_id) if not is_completed else None

    return {
        "session": updated_session,
        "is_completed": is_completed,
        "completed_cards": completed_cards,
        "total_cards": len(queue),
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "updated_card_srs": updated_card,
        "next_card": next_card,
    }


def pause_session(
    conn: sqlite3.Connection, session_id: str, user_id: str
) -> Optional[Dict[str, Any]]:
    return repository.update_session(conn, session_id, user_id, status="PAUSED")


def resume_session(
    conn: sqlite3.Connection, session_id: str, user_id: str
) -> Optional[Dict[str, Any]]:
    return repository.update_session(conn, session_id, user_id, status="ACTIVE")


def abandon_session(
    conn: sqlite3.Connection, session_id: str, user_id: str
) -> Optional[Dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    return repository.update_session(
        conn, session_id, user_id, status="ABANDONED", end_time=now
    )


def get_session_summary(
    conn: sqlite3.Connection, session_id: str, user_id: str
) -> Dict[str, Any]:
    session = repository.get_session_by_id(conn, session_id, user_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    logs = repository.get_session_card_logs(conn, session_id, user_id)
    total_reviewed = len(logs)
    correct_count = session.get("correct_count", 0)
    accuracy = (correct_count / total_reviewed * 100.0) if total_reviewed > 0 else 0.0
    total_time = sum(l["time_spent_seconds"] for l in logs)

    return {
        "session_id": session_id,
        "title": session["title"],
        "status": session["status"],
        "session_date": session["session_date"],
        "total_cards_in_queue": session["total_cards"],
        "completed_cards": session["completed_cards"],
        "correct_count": correct_count,
        "incorrect_count": session.get("incorrect_count", 0),
        "accuracy_percentage": round(accuracy, 1),
        "total_time_seconds": round(total_time, 1),
        "start_time": session["start_time"],
        "end_time": session["end_time"],
    }
