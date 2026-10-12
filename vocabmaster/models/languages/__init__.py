"""Language-specific models."""

from vocabmaster.models.languages.english import EnglishFields
from vocabmaster.models.languages.japanese import JapaneseFields
from vocabmaster.models.languages.german import GermanFields
from vocabmaster.models.languages.romance import RomanceFields
from vocabmaster.models.languages.vietnamese import VietnameseFields

__all__ = [
    "EnglishFields",
    "JapaneseFields",
    "GermanFields",
    "RomanceFields",
    "VietnameseFields",
]
