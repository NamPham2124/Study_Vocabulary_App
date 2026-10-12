"""Core vocabulary item base models and enums."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Language(str, Enum):
    EN = "en"
    ZH = "zh"  # Mandarin Chinese
    JA = "ja"
    DE = "de"
    ES = "es"
    FR = "fr"
    VI = "vi"
    OTHER = "other"


class ScriptPreference(str, Enum):
    HANS = "hans"  # Simplified Chinese
    HANT = "hant"  # Traditional Chinese


class BaseVocabCreate(BaseModel):
    deck_id: str
    term: str = Field(..., min_length=1, description="Word or character")
    definition: str = Field(..., min_length=1, description="Meaning or translation")
    language: Language = Language.EN
    ipa: str = ""
    part_of_speech: str = ""
    examples: List[str] = Field(default_factory=list)
    synonyms: List[str] = Field(default_factory=list)
    antonyms: List[str] = Field(default_factory=list)
    notes: str = ""
    tags: List[str] = Field(default_factory=list)
    root_word: str = ""
    root_word_id: Optional[str] = None
    vietnamese_meanings: List[str] = Field(default_factory=list)
    english_definitions: List[str] = Field(default_factory=list)
    mnemonics: str = ""
    audio_url: str = ""
    is_favorite: bool = False
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
    root_word: Optional[str] = None
    root_word_id: Optional[str] = None
    vietnamese_meanings: Optional[List[str]] = None
    english_definitions: Optional[List[str]] = None
    mnemonics: Optional[str] = None
    audio_url: Optional[str] = None
    is_favorite: Optional[bool] = None
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
    root_word: str = ""
    root_word_id: Optional[str] = None
    vietnamese_meanings: List[str] = Field(default_factory=list)
    english_definitions: List[str] = Field(default_factory=list)
    mnemonics: str = ""
    audio_url: str = ""
    is_favorite: bool = False
    language_specific_fields: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str
