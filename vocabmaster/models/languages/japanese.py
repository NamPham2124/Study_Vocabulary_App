"""Japanese language vocabulary models and validation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class JapaneseFields(BaseModel):
    reading: str = Field(..., description="Furigana or Kana reading (e.g. たべる)")
    romaji: Optional[str] = None
    pitch_accent: Optional[str] = None
    jlpt_level: Optional[str] = Field(None, pattern=r"^(N5|N4|N3|N2|N1)$")
    verb_type: Optional[str] = Field(
        None, description="ichidan, godan, suru, kuru, or irregular"
    )
    transitivity: Optional[str] = Field(
        None, description="transitive, intransitive, or both"
    )
    kanji_components: List[str] = Field(default_factory=list)
