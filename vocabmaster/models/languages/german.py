"""German language vocabulary models and validation."""

from typing import Optional
from pydantic import BaseModel, Field


class GermanFields(BaseModel):
    article: Optional[str] = Field(None, pattern=r"^(der|die|das)$")
    gender: Optional[str] = Field(None, pattern=r"^(masculine|feminine|neuter)$")
    plural_form: Optional[str] = None
    case_governed: Optional[str] = Field(
        None, pattern=r"^(Nominativ|Akkusativ|Dativ|Genitiv)$"
    )
    preposition: Optional[str] = None
    cefr_level: Optional[str] = Field(None, pattern=r"^(A1|A2|B1|B2|C1|C2)$")
