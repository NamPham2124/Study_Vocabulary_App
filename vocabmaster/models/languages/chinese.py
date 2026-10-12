"""Mandarin Chinese vocabulary linguistic models, Pinyin normalization, and validation."""

import re
import unicodedata
from typing import List, Optional
from pydantic import BaseModel, Field


# Tone mark mappings for Pinyin
PINYIN_TONE_MARKS = {
    'a': ['ā', 'á', 'ǎ', 'à', 'a'],
    'e': ['ē', 'é', 'ě', 'è', 'e'],
    'i': ['ī', 'í', 'ǐ', 'ì', 'i'],
    'o': ['ō', 'ó', 'ǒ', 'ò', 'o'],
    'u': ['ū', 'ú', 'ǔ', 'ù', 'u'],
    'ü': ['ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü'],
    'v': ['ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü'],
}


class ChineseFields(BaseModel):
    simplified: Optional[str] = None
    traditional: Optional[str] = None
    pinyin: str = Field(..., description="Pinyin with tone marks, e.g. 'xuéxí'")
    pinyin_numbered: Optional[str] = Field(None, description="Numbered pinyin, e.g. 'xue2xi2'")
    tone_sequence: Optional[str] = Field(None, description="Tone sequence, e.g. '2-2', '2-4'")
    hsk_level: Optional[str] = Field(None, pattern=r"^(HSK [1-6]|HSK[1-6]|1|2|3|4|5|6)$")
    character_components: List[str] = Field(default_factory=list)
    related_words: List[str] = Field(default_factory=list)
    radical: Optional[str] = None
    stroke_count: Optional[int] = None


def normalize_pinyin(pinyin_str: str) -> str:
    """Normalize Pinyin string with Unicode NFC normalization and lowercased spacing."""
    if not pinyin_str:
        return ""
    normalized = unicodedata.normalize("NFC", pinyin_str.strip().lower())
    # Replace v with ü if used as shorthand
    return normalized


def extract_tone_numbers_from_pinyin(pinyin_text: str) -> List[int]:
    """
    Extract tone numbers (1-5) from tone-marked Pinyin syllables.
    Tone 5 represents neutral tone. Supports space-separated and joined syllables.
    """
    tone_char_map = {
        'ā': 1, 'ē': 1, 'ī': 1, 'ō': 1, 'ū': 1, 'ǖ': 1,
        'á': 2, 'é': 2, 'í': 2, 'ó': 2, 'ú': 2, 'ǘ': 2,
        'ǎ': 3, 'ě': 3, 'ǐ': 3, 'ǒ': 3, 'ǔ': 3, 'ǚ': 3,
        'à': 4, 'è': 4, 'ì': 4, 'ò': 4, 'ù': 4, 'ǜ': 4,
    }
    tones: List[int] = []
    # Segment Pinyin syllables (handles both space-separated and joined words)
    syllable_pattern = r"(?:zh|ch|sh|[bpmfdtnlgkhjqxrzcsyw])?[aeiouüāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+(?:ng|n|r)?"
    syllables = re.findall(syllable_pattern, pinyin_text.strip().lower())
    if not syllables:
        # Fallback to whitespace split if regex did not match
        syllables = [s for s in re.split(r"[\s\-']+", pinyin_text.strip().lower()) if s]

    for syl in syllables:
        found = 5  # default neutral
        for ch in syl:
            if ch in tone_char_map:
                found = tone_char_map[ch]
                break
        tones.append(found)
    return tones
