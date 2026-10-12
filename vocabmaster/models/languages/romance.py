"""Romance languages (Spanish, French) vocabulary models and validation."""

from typing import Optional
from pydantic import BaseModel, Field


class RomanceFields(BaseModel):
    gender: Optional[str] = Field(None, pattern=r"^(masculine|feminine)$")
    plural_form: Optional[str] = None
    conjugation_group: Optional[str] = None  # e.g. -ar, -er, -ir or 1er groupe
    auxiliary_verb: Optional[str] = None  # e.g. haber, avoir, être
