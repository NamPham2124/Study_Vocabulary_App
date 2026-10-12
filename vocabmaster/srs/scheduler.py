"""SRS scheduling helpers and database integration."""

from datetime import datetime
from typing import Any, Dict, Optional
import sqlite3
from vocabmaster.db import repository
from vocabmaster.srs.algorithm import CardState, compute_srs_update


def review_card(
    conn: sqlite3.Connection,
    card_id: str,
    user_id: str,
    rating: int,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Review a card, calculate updated SRS metrics, and persist to database.
    Returns the updated card dictionary.
    """
    card = repository.get_srs_card_by_id(conn, card_id, user_id)
    if not card:
        raise ValueError(f"Card {card_id} not found for user {user_id}")

    res = compute_srs_update(
        state=CardState(card["state"]),
        step_index=card["step_index"],
        repetition_count=card["repetition_count"],
        interval_days=card["interval_days"],
        ease_factor=card["ease_factor"],
        rating=rating,
        now=now,
    )

    updated = repository.update_srs_card(
        conn=conn,
        card_id=card_id,
        user_id=user_id,
        state=res.state.value,
        step_index=res.step_index,
        repetition_count=res.repetition_count,
        interval_days=res.interval_days,
        ease_factor=res.ease_factor,
        due_date=res.due_date,
        last_reviewed_at=res.last_reviewed_at,
    )
    if not updated:
        raise RuntimeError(f"Failed to update card {card_id}")
    return updated
