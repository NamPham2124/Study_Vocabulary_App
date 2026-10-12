"""Spaced Repetition System (SRS) algorithm implementation."""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import NamedTuple, Optional
from vocabmaster.config import settings


class CardState(str, Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"


class SRSReviewResult(NamedTuple):
    state: CardState
    step_index: int
    repetition_count: int
    interval_days: float
    ease_factor: float
    due_date: str
    last_reviewed_at: str


def compute_srs_update(
    state: CardState,
    step_index: int,
    repetition_count: int,
    interval_days: float,
    ease_factor: float,
    rating: int,
    now: Optional[datetime] = None,
) -> SRSReviewResult:
    """
    Calculate updated SRS parameters based on SM-2+ spaced repetition.
    
    Ratings:
      0: Complete blackout
      1: Incorrect, remembered upon seeing answer
      2: Incorrect, hard struggle
      3: Correct with difficulty
      4: Good recall with reasonable effort
      5: Perfect, effortless recall
    """
    if rating < 0 or rating > 5:
        raise ValueError(f"Rating must be between 0 and 5, got {rating}")

    current_time = now or datetime.now(timezone.utc)
    last_reviewed_at = current_time.isoformat()
    min_ef = settings.min_ease_factor

    # Failure cases (ratings 0, 1, 2)
    if rating < 3:
        new_state = CardState.RELEARNING if state == CardState.REVIEW else CardState.LEARNING
        new_step_index = 0
        new_repetition_count = 0
        # Lapse penalty: ease factor drops
        new_ef = max(min_ef, round(ease_factor - 0.20, 3))
        # Relearning card due in short interval (~10 mins / 0.007 days, or next day)
        new_interval = 0.01 if rating == 2 else 0.005
        due_time = current_time + timedelta(days=new_interval)
        return SRSReviewResult(
            state=new_state,
            step_index=new_step_index,
            repetition_count=new_repetition_count,
            interval_days=new_interval,
            ease_factor=new_ef,
            due_date=due_time.isoformat(),
            last_reviewed_at=last_reviewed_at,
        )

    # Success cases (ratings 3, 4, 5)
    # 1. Card in NEW, LEARNING, or RELEARNING
    if state in (CardState.NEW, CardState.LEARNING, CardState.RELEARNING):
        if rating >= 4:
            # Graduate immediately if good/easy
            new_state = CardState.REVIEW
            new_repetition_count = 1
            new_step_index = 0
            new_interval = 1.0 if rating == 4 else 3.0
        else:
            # Rating == 3, advance step
            if step_index >= 1:
                new_state = CardState.REVIEW
                new_repetition_count = 1
                new_step_index = 0
                new_interval = 1.0
            else:
                new_state = CardState.LEARNING
                new_step_index = step_index + 1
                new_repetition_count = 0
                new_interval = 0.5

        new_ef = ease_factor
        due_time = current_time + timedelta(days=new_interval)
        return SRSReviewResult(
            state=new_state,
            step_index=new_step_index,
            repetition_count=new_repetition_count,
            interval_days=new_interval,
            ease_factor=new_ef,
            due_date=due_time.isoformat(),
            last_reviewed_at=last_reviewed_at,
        )

    # 2. Card in REVIEW state
    new_repetition_count = repetition_count + 1
    if new_repetition_count == 1:
        new_interval = 1.0
    elif new_repetition_count == 2:
        new_interval = 6.0
    else:
        new_interval = round(interval_days * ease_factor, 1)

    # Adjust Ease Factor via SM-2 formula:
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    delta_ef = 0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)
    new_ef = max(min_ef, round(ease_factor + delta_ef, 3))
    
    # Easy bonus
    if rating == 5:
        new_interval = round(new_interval * 1.3, 1)

    due_time = current_time + timedelta(days=new_interval)
    return SRSReviewResult(
        state=CardState.REVIEW,
        step_index=0,
        repetition_count=new_repetition_count,
        interval_days=new_interval,
        ease_factor=new_ef,
        due_date=due_time.isoformat(),
        last_reviewed_at=last_reviewed_at,
    )
