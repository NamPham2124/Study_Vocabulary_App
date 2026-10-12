"""Recoverable Daily Learning Session Manager (20-Minute Workflow & Targeted Study)."""

from datetime import datetime, timezone
import json
import uuid
from typing import Any, Dict, List, Optional
import sqlite3

from vocabmaster.config import settings
from vocabmaster.db import repository
from vocabmaster.srs.scheduler import review_card


PHASES_ORDER = ["review", "new_words", "recall_test", "practice", "completed"]


def start_or_resume_session(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: Optional[str] = None,
    path_id: Optional[str] = None,
    learning_language: Optional[str] = None,
    session_type: Optional[str] = None,
    new_card_limit: Optional[int] = None,
    review_limit: Optional[int] = None,
    unlimited: bool = False,
) -> Dict[str, Any]:
    """
    Start a new daily session or automatically recover an unfinished active/paused session.
    Enforces strict, configurable daily limits unless unlimited=True.
    """
    user = repository.get_user_by_id(conn, user_id)
    deck = repository.get_deck_by_id(conn, deck_id, user_id) if deck_id else None

    # Determine resolved language
    resolved_lang = learning_language
    if not resolved_lang and deck:
        resolved_lang = deck.get("language")
    if not resolved_lang and user:
        resolved_lang = user.get("preferred_language", "en")
    if not resolved_lang:
        resolved_lang = "en"

    # 1. Check for recoverable existing active or paused session matching language and context
    existing = repository.get_active_or_paused_session(
        conn, user_id, deck_id=deck_id, path_id=path_id, learning_language=resolved_lang
    )
    if existing:
        if existing["status"] == "PAUSED":
            existing = repository.update_session(
                conn, existing["id"], user_id, status="ACTIVE"
            )
        current_card = get_current_card(conn, existing["id"], user_id)
        return {
            "session": existing,
            "recovered": True,
            "current_card": current_card,
        }

    # 2. Build structured queues with bounded limits
    if unlimited:
        limit_new = new_card_limit or 1000
        limit_rev = review_limit or 1000
    else:
        # Determine target limits from deck or user settings
        target_new = (
            new_card_limit
            if new_card_limit is not None
            else (deck.get("max_new_cards_per_day") if deck and deck.get("max_new_cards_per_day") is not None else (user.get("daily_new_target", 5) if user else 5))
        )
        target_rev = (
            review_limit
            if review_limit is not None
            else (deck.get("max_reviews_per_day") if deck and deck.get("max_reviews_per_day") is not None else (user.get("daily_review_target", 50) if user else 50))
        )

        # Subtract cards already completed today
        progress = repository.get_daily_study_progress(
            conn, user_id, deck_id=deck_id, learning_language=resolved_lang
        )
        already_new = progress["new_cards_studied_today"]
        already_rev = progress["review_cards_studied_today"]

        limit_new = max(0, target_new - already_new)
        limit_rev = max(0, target_rev - already_rev)

    due_reviews = (
        repository.get_due_review_cards(
            conn, user_id, deck_id=deck_id, path_id=path_id, learning_language=resolved_lang, limit=limit_rev
        )
        if limit_rev > 0
        else []
    )
    new_cards = (
        repository.get_new_cards(
            conn, user_id, deck_id=deck_id, path_id=path_id, learning_language=resolved_lang, limit=limit_new
        )
        if limit_new > 0
        else []
    )

    review_ids = [c["id"] for c in due_reviews]
    new_ids = [c["id"] for c in new_cards]

    if session_type is None:
        if deck_id and not path_id:
            session_type = "deck_study"
        else:
            session_type = "daily_20min"

    if session_type == "deck_study":
        primary_queue = review_ids + new_ids
        initial_phase = "deck_study"
    elif session_type == "review_only":
        primary_queue = review_ids
        initial_phase = "review"
    elif session_type == "practice_only":
        primary_queue = review_ids[:5] + new_ids[:5]
        initial_phase = "practice"
    else:
        # daily_20min
        if review_ids:
            primary_queue = review_ids
            initial_phase = "review"
        elif new_ids:
            primary_queue = new_ids
            initial_phase = "new_words"
        else:
            primary_queue = []
            initial_phase = "completed"

    phase_data = {
        "review": review_ids,
        "new_words": new_ids,
        "recall_test": (review_ids[:5] + new_ids[:5]),
        "practice": (new_ids[:3] or review_ids[:3]),
    }

    session_id = str(uuid.uuid4())
    context_title = "Daily 20-Min Session"
    if path_id:
        path = repository.get_learning_path_by_id(conn, path_id, user_id)
        if path:
            context_title = f"Path: {path['name']}"
    elif deck_id:
        if deck:
            context_title = f"Deck: {deck['name']}"

    now = datetime.now(timezone.utc).isoformat()
    session_data = {
        "id": session_id,
        "user_id": user_id,
        "deck_id": deck_id,
        "path_id": path_id,
        "learning_language": resolved_lang,
        "title": f"{context_title} ({now[:10]})",
        "session_date": now[:10],
        "session_type": session_type,
        "current_phase": initial_phase,
        "status": "ACTIVE" if primary_queue else "COMPLETED",
        "card_ids_queue": primary_queue,
        "current_index": 0,
        "total_cards": len(primary_queue),
        "completed_cards": 0,
        "correct_count": 0,
        "incorrect_count": 0,
        "phase_durations": {"review": 0, "new_words": 0, "recall_test": 0, "practice": 0},
        "phase_data": phase_data,
        "phase_target_seconds": 1200,
        "start_time": now,
        "end_time": now if not primary_queue else None,
    }

    created = repository.create_session(conn, session_data)
    current_card = get_current_card(conn, session_id, user_id) if primary_queue else None

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
        "current_phase": session.get("current_phase", "review"),
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
        "root_word": vocab_item.get("root_word", ""),
        "vietnamese_meanings": vocab_item.get("vietnamese_meanings", []),
        "english_definitions": vocab_item.get("english_definitions", []),
        "mnemonics": vocab_item.get("mnemonics", ""),
        "audio_url": vocab_item.get("audio_url", ""),
        "is_favorite": vocab_item.get("is_favorite", False),
        "language": vocab_item["language"],
        "language_specific_fields": vocab_item["language_specific_fields"],
        "state": srs_card["state"],
        "repetition_count": srs_card["repetition_count"],
        "ease_factor": srs_card["ease_factor"],
        "interval_days": srs_card["interval_days"],
    }


def advance_phase(
    conn: sqlite3.Connection, session_id: str, user_id: str
) -> Dict[str, Any]:
    """Advance to next phase in the 20-minute daily learning workflow."""
    session = repository.get_session_by_id(conn, session_id, user_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    cur_phase = session.get("current_phase", "review")
    phase_data = session.get("phase_data", {})

    cur_idx = PHASES_ORDER.index(cur_phase) if cur_phase in PHASES_ORDER else len(PHASES_ORDER)
    next_phase = "completed"
    next_queue: List[str] = []
    for next_candidate in PHASES_ORDER[cur_idx + 1:]:
        candidate_queue = phase_data.get(next_candidate, [])
        if candidate_queue:
            next_phase = next_candidate
            next_queue = candidate_queue
            break

    now = datetime.now(timezone.utc).isoformat()
    if next_phase == "completed" or not next_queue:
        updated = repository.update_session(
            conn, session_id, user_id, status="COMPLETED", current_phase="completed", end_time=now
        )
        # Record daily study activity log
        total_time = sum(session.get("phase_durations", {}).values()) or 300
        learning_language = session.get("learning_language", "en")
        repository.record_study_activity(
            conn=conn,
            user_id=user_id,
            study_date=session.get("session_date", now[:10]),
            learning_language=learning_language,
            duration_seconds=float(total_time),
            cards_reviewed=session.get("completed_cards", 0),
            new_words_learned=len(phase_data.get("new_words", [])),
        )
        return {"session": updated, "current_card": None, "is_completed": True}

    updated = repository.update_session(
        conn,
        session_id,
        user_id,
        current_phase=next_phase,
        card_ids_queue=next_queue,
        current_index=0,
        total_cards=len(next_queue),
    )
    current_card = get_current_card(conn, session_id, user_id)
    return {"session": updated, "current_card": current_card, "is_completed": False}


def submit_card_answer(
    conn: sqlite3.Connection,
    session_id: str,
    user_id: str,
    rating: int,
    exercise_type: str = "flashcard",
    user_response: str = "",
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
        raise ValueError("Current phase queue is already completed")

    card_id = queue[idx]

    current_srs_card = repository.get_srs_card_by_id(conn, card_id, user_id)
    was_new = 1 if (current_srs_card and current_srs_card.get("state") == "NEW") else 0

    # 1. Update SRS card
    updated_card = review_card(conn, card_id, user_id, rating)

    # 2. Record card log
    is_correct = rating >= 3
    log_id = str(uuid.uuid4())
    repository.record_card_log(
        conn,
        {
            "id": log_id,
            "session_id": session_id,
            "card_id": card_id,
            "user_id": user_id,
            "rating": rating,
            "exercise_type": exercise_type,
            "user_response": user_response,
            "is_correct": is_correct,
            "time_spent_seconds": time_spent_seconds,
            "scheduled_next_interval": updated_card["interval_days"],
            "was_new_card": was_new,
        },
    )

    # 3. Update session metrics
    correct_count = session["correct_count"] + (1 if is_correct else 0)
    incorrect_count = session["incorrect_count"] + (0 if is_correct else 1)
    completed_cards = session["completed_cards"] + 1
    next_idx = idx + 1

    # Update phase durations
    cur_phase = session.get("current_phase", "review")
    phase_durations = session.get("phase_durations", {})
    phase_durations[cur_phase] = phase_durations.get(cur_phase, 0) + time_spent_seconds

    # If failed and requeue enabled, append to current queue for intraday review
    if not is_correct and requeue_failed_cards:
        queue.append(card_id)

    is_phase_completed = next_idx >= len(queue)
    now = datetime.now(timezone.utc).isoformat()

    updated_session = repository.update_session(
        conn,
        session_id,
        user_id,
        card_ids_queue=queue,
        current_index=next_idx,
        total_cards=len(queue),
        completed_cards=completed_cards,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        phase_durations=phase_durations,
    )

    # If this phase queue is finished in daily_20min workflow
    if is_phase_completed and session.get("session_type") == "daily_20min":
        advance_res = advance_phase(conn, session_id, user_id)
        return {
            "session": advance_res["session"],
            "phase_transitioned": True,
            "is_completed": advance_res["is_completed"],
            "completed_cards": completed_cards,
            "total_cards": advance_res["session"]["total_cards"],
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "updated_card_srs": updated_card,
            "next_card": advance_res["current_card"],
        }

    is_completed = is_phase_completed
    if is_completed:
        repository.update_session(conn, session_id, user_id, status="COMPLETED", end_time=now)
        # Record study log
        total_time = sum(phase_durations.values()) or time_spent_seconds
        learning_language = session.get("learning_language", "en")
        repository.record_study_activity(
            conn=conn,
            user_id=user_id,
            study_date=session.get("session_date", now[:10]),
            learning_language=learning_language,
            duration_seconds=float(total_time),
            cards_reviewed=completed_cards,
            new_words_learned=0,
        )

    next_card = get_current_card(conn, session_id, user_id) if not is_completed else None

    return {
        "session": updated_session,
        "phase_transitioned": False,
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

    streak_info = repository.get_user_streak(conn, user_id)

    return {
        "session_id": session_id,
        "title": session["title"],
        "status": session["status"],
        "session_type": session.get("session_type", "daily_20min"),
        "session_date": session["session_date"],
        "total_cards_in_queue": session["total_cards"],
        "completed_cards": session["completed_cards"],
        "correct_count": correct_count,
        "incorrect_count": session.get("incorrect_count", 0),
        "accuracy_percentage": round(accuracy, 1),
        "total_time_seconds": round(total_time, 1),
        "current_streak": streak_info["current_streak"],
        "start_time": session["start_time"],
        "end_time": session["end_time"],
    }
