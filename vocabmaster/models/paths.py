"""Pydantic schemas for Learning Paths."""

from typing import List, Optional
from pydantic import BaseModel, Field
from vocabmaster.models.base import Language


class LearningPathCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    learning_language: Language = Language.EN
    objective: str = ""
    daily_new_target: int = Field(5, ge=1, le=100)
    daily_time_goal: int = Field(20, ge=5, le=180)
    deck_ids: List[str] = Field(default_factory=list)


class LearningPathUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    objective: Optional[str] = None
    daily_new_target: Optional[int] = Field(None, ge=1, le=100)
    daily_time_goal: Optional[int] = Field(None, ge=5, le=180)
    status: Optional[str] = None  # ACTIVE, ARCHIVED
    deck_ids: Optional[List[str]] = None


class LearningPathResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    learning_language: str
    objective: str
    daily_new_target: int
    daily_time_goal: int
    status: str
    linked_deck_ids: List[str] = Field(default_factory=list)
    total_vocabulary_count: int = 0
    created_at: str
    updated_at: str
