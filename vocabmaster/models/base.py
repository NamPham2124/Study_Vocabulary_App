"""Core vocabulary item base models and enums."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Language(str, Enum):
    EN = "en"
    JA = "ja"
    DE = "de"
    ES = "es"
    FR = "fr"
    VI = "vi"
    OTHER = "other"


class BaseVocabCreate(BaseModel):
    deck_id: str
    term: str = Field(..., min_length=1, description="Word or phrase")
    definition: str = Field(..., min_length=1, description="Meaning or translation")
    language: Language = Language.EN
    ipa: str = ""
    part_of_speech: str = ""
    examples: List[str] = Field(default_factory=list)
    synonyms: List[str] = Field(default_factory=list)
    antonyms: List[str] = Field(default_factory=list)
    notes: str = ""
    tags: List[str] = Field(default_factory=list)
    language_specific_fields: Dict[str, Any] = Field(default_factory=dict)


class BaseVocabUpdate(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    language: Optional[Language] = None
    ipa: Optional[str] = None
    part_of_speech: Optional[str] = None
    examples: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    antonyms: Optional[List[str]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    language_specific_fields: Optional[Dict[str, Any]] = None


class BaseVocabResponse(BaseModel):
    id: str
    deck_id: str
    user_id: str
    language: str
    term: str
    definition: str
    ipa: str = ""
    part_of_speech: str = ""
    examples: List[str] = Field(default_factory=list)
    synonyms: List[str] = Field(default_factory=list)
    antonyms: List[str] = Field(default_factory=list)
    notes: str = ""
    tags: List[str] = Field(default_factory=list)
    language_specific_fields: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str
