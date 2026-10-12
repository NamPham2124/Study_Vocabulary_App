"""Column name mapping and header normalization for CSV and XLSX imports."""

import re
from typing import Dict, List, Optional


COLUMN_SYNONYMS: Dict[str, List[str]] = {
    "term": ["term", "word", "vocabulary", "vocab", "tu", "từ", "kanji", "schluesselwort", "headword"],
    "definition": ["definition", "meaning", "translation", "dich", "dịch", "nghia", "nghĩa", "bedeutung", "gloss"],
    "ipa": ["ipa", "pronunciation", "phonetic", "phien_am", "phiên âm", "aussprache"],
    "part_of_speech": ["part_of_speech", "pos", "loai_tu", "loại từ", "wortart", "type"],
    "examples": ["examples", "example", "sentence", "sentences", "cau_vi_du", "ví dụ", "beispiel"],
    "synonyms": ["synonyms", "synonym", "tu_dong_nghia"],
    "antonyms": ["antonyms", "antonym", "tu_trai_nghia"],
    "notes": ["notes", "note", "ghi_chu", "ghi chú", "anmerkung", "comment"],
    "tags": ["tags", "tag", "labels", "the"],
    # Language-specific fields
    "reading": ["reading", "furigana", "kana", "hiragana", "katakana", "doc", "đọc"],
    "romaji": ["romaji", "la_tinh"],
    "jlpt_level": ["jlpt", "jlpt_level", "cap_do_jlpt"],
    "cefr_level": ["cefr", "cefr_level", "level"],
    "article": ["article", "artikel", "mao_tu", "mạo từ"],
    "gender": ["gender", "genus", "giong", "giống"],
    "plural_form": ["plural", "plural_form", "pluralform", "so_nhieu", "số nhiều"],
    "tone": ["tone", "thanh_dieu", "thanh điệu", "dau", "dấu"],
    "sino_vietnamese": ["sino_vietnamese", "han_viet", "hán việt"],
}


def normalize_header(header: str) -> str:
    """Normalize a header string: lowercase, stripped of BOM and separators."""
    h = str(header).replace("\ufeff", "").strip().lower()
    h = re.sub(r"[\s\-_]+", "_", h)
    return h


def build_column_mapping(headers: List[str]) -> Dict[str, str]:
    """
    Build a mapping from canonical field names to the actual column header found in the file.
    Returns: {canonical_field: actual_header}
    """
    mapping: Dict[str, str] = {}
    normalized_to_original = {normalize_header(h): h for h in headers if h}

    for canonical, aliases in COLUMN_SYNONYMS.items():
        for alias in aliases:
            norm_alias = normalize_header(alias)
            if norm_alias in normalized_to_original:
                mapping[canonical] = normalized_to_original[norm_alias]
                break

    return mapping
