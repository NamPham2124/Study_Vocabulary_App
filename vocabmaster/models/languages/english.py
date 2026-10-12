"""English language vocabulary models and validation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class EnglishFields(BaseModel):
    cefr_level: Optional[str] = Field(None, pattern=r"^(A1|A2|B1|B2|C1|C2)$")
    collocations: List[str] = Field(default_factory=list)
    phrasal_verbs: List[str] = Field(default_factory=list)
    irregular_past: Optional[str] = None
    irregular_past_participle: Optional[str] = None
