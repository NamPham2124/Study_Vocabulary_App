"""Column name mapping and header normalization for multilingual CSV, XLSX, and pasted table imports."""

import re
from typing import Dict, List, Optional


COLUMN_SYNONYMS: Dict[str, List[str]] = {
    # Core fields
    "term": [
        "term", "word", "vocabulary", "vocab", "tu", "từ", "từ vựng", "tu vung",
        "từ mới", "tu moi", "từ tiếng anh", "tu tieng anh", "english word", "headword",
        "chinese", "hanzi", "汉字", "kanji", "schluesselwort"
    ],
    "definition": [
        "definition", "meaning", "translation", "dich", "dịch", "nghia", "nghĩa",
        "nghĩa tiếng việt", "nghia tieng viet", "vietnamese meaning", "định nghĩa",
        "dinh nghia", "ý nghĩa", "y nghia", "giải nghĩa", "giai nghia", "dịch nghĩa",
        "dich nghia", "tiếng việt", "tieng viet", "bedeutung", "gloss"
    ],
    "ipa": [
        "ipa", "pronunciation", "phonetic", "phonetics", "phien_am", "phiên âm", "phien am",
        "phat_am", "phát âm", "phat am", "phát_âm", "cách đọc", "cach doc", "cách_đọc", "cach_doc",
        "phiên âm quốc tế", "phien am quoc te", "phiên âm ipa", "phien am ipa", "phát âm ipa", "phat am ipa",
        "kí hiệu phiên âm", "ký hiệu phiên âm", "ki hieu phien am", "ky hieu phien am",
        "transcription", "phonetic transcription", "phonetic_transcription",
        "pronounce", "spelling", "pron", "sound", "doc", "đọc",
        "ipa uk", "ipa us", "ipa_uk", "ipa_us", "uk ipa", "us ipa", "uk", "us",
        "aussprache"
    ],
    "part_of_speech": [
        "part_of_speech", "pos", "loai_tu", "loại từ", "loai tu", "từ loại", "tu loai",
        "từ_loại", "tu_loai", "phân loại", "phan loai", "chức năng từ", "chuc nang tu",
        "wortart", "type"
    ],
    "root_word": [
        "root_word", "base_word", "từ_gốc", "tu_goc", "từ gốc", "tu goc", "gốc từ", "goc tu",
        "từ căn", "tu can", "root", "base form", "stem"
    ],
    "examples": [
        "examples", "example", "sentence", "sentences", "cau_vi_du", "ví dụ", "vi du",
        "câu ví dụ", "cau vi du", "ví dụ câu", "vi du cau", "mẫu câu", "mau cau",
        "câu mẫu", "cau mau", "example sentence", "beispiel", "例句"
    ],
    "example_translation": [
        "example_translation", "translation_of_example", "dịch ví dụ", "dich vi du",
        "dịch câu", "dich cau", "nghĩa ví dụ", "nghia vi du", "nghĩa câu", "nghia cau",
        "example vietnamese"
    ],
    "example_pinyin": [
        "example_pinyin", "pinyin ví dụ", "pinyin vi du", "pinyin câu"
    ],
    "synonyms": [
        "synonyms", "synonym", "tu_dong_nghia", "từ đồng nghĩa", "đồng nghĩa", "dong nghia"
    ],
    "antonyms": [
        "antonyms", "antonym", "tu_trai_nghia", "từ trái nghĩa", "trái nghĩa", "trai nghia"
    ],
    "collocations": [
        "collocations", "collocation", "cum_tu", "cụm từ đi kèm", "cụm từ", "cum tu"
    ],
    "mnemonics": [
        "mnemonics", "mnemonic", "meo_nho", "mẹo nhớ", "meo nho", "mẹo ghi nhớ", "meo ghi nho",
        "cách nhớ", "cach nho", "goi_nho", "gợi nhớ", "memory hint"
    ],
    "notes": [
        "notes", "note", "ghi_chu", "ghi chú", "ghi chu", "anmerkung", "comment"
    ],
    "tags": [
        "tags", "tag", "labels", "the", "thẻ", "nhan", "nhãn"
    ],
    # Chinese fields
    "pinyin": [
        "pinyin", "拼音", "pinyin with tone marks", "phien am pinyin", "phiên âm pinyin"
    ],
    "tone": [
        "tone", "tones", "thanh_dieu", "thanh điệu", "thanh dieu", "dấu", "dau"
    ],
    "hsk_level": [
        "hsk", "hsk_level", "hsk level", "cấp độ hsk", "cap do hsk"
    ],
    "traditional": [
        "traditional", "phồn thể", "phon the", "繁体", "繁體"
    ],
    "simplified": [
        "simplified", "giản thể", "gian the", "简体", "簡體"
    ],
    # Other language fields
    "reading": ["reading", "furigana", "kana", "hiragana", "katakana"],
    "romaji": ["romaji", "la_tinh"],
    "jlpt_level": ["jlpt", "jlpt_level", "cap_do_jlpt"],
    "cefr_level": ["cefr", "cefr_level", "level"],
    "article": ["article", "artikel", "mao_tu", "mạo từ"],
    "gender": ["gender", "genus", "giong", "giống"],
    "plural_form": ["plural", "plural_form", "pluralform", "so_nhieu", "số nhiều"],
    "sino_vietnamese": ["sino_vietnamese", "han_viet", "hán việt"],
}


def normalize_header(header: str) -> str:
    """Normalize a header string: lowercase, stripped of BOM, punctuation, and normalized spacing."""
    h = str(header).replace("\ufeff", "").strip().lower()
    h = re.sub(r"[\s\-_]+", "_", h)
    return h


def get_header_candidates(header: str) -> List[str]:
    """
    Generate normalized match candidates from a header string.
    Handles parenthetical explanations, punctuation, and spacing variants.
    e.g., 'Phiên âm (IPA)' -> ['phiên_âm_(ipa)', 'phiên_âm_ipa', 'phiên_âm', 'ipa']
    """
    h = str(header).replace("\ufeff", "").strip().lower()
    if not h:
        return []

    candidates = set()
    norm1 = re.sub(r"[\s\-_]+", "_", h)
    candidates.add(norm1)

    # Without punctuation
    no_punct = re.sub(r"[^\w\s]", " ", h).strip()
    if no_punct:
        candidates.add(re.sub(r"[\s\-_]+", "_", no_punct))
        candidates.add(no_punct)

    # Stripped of parenthetical expressions: 'Phiên âm (IPA)' -> 'Phiên âm'
    no_parens = re.sub(r"[\(\[\{].*?[\)\]\}]", "", h).strip()
    if no_parens:
        candidates.add(re.sub(r"[\s\-_]+", "_", no_parens))
        candidates.add(no_parens)

    # Content inside parenthetical expressions: 'Phiên âm (IPA)' -> 'IPA'
    inside_parens = re.findall(r"[\(\[\{](.*?)[\)\]\}]", h)
    for ins in inside_parens:
        ins_clean = ins.strip()
        if ins_clean:
            candidates.add(re.sub(r"[\s\-_]+", "_", ins_clean))
            candidates.add(ins_clean)

    return list(candidates)


def build_column_mapping(headers: List[str]) -> Dict[str, str]:
    """
    Build a mapping from canonical field names to the actual column header found in the file.
    Supports exact synonym matches, parenthetical variations, and smart token heuristics.
    Returns: {canonical_field: actual_header}
    """
    mapping: Dict[str, str] = {}
    assigned_headers = set()

    header_info = []
    for orig in headers:
        if not orig:
            continue
        cands = get_header_candidates(orig)
        norm_cands = {normalize_header(c) for c in cands}
        header_info.append((orig, norm_cands, orig.strip().lower()))

    # Tier 1: Exact matches against synonyms
    for canonical, aliases in COLUMN_SYNONYMS.items():
        if canonical in mapping:
            continue
        for alias in aliases:
            norm_alias = normalize_header(alias)
            found = False
            for orig, cands, _ in header_info:
                if orig in assigned_headers:
                    continue
                if norm_alias in cands:
                    mapping[canonical] = orig
                    assigned_headers.add(orig)
                    found = True
                    break
            if found:
                break

    # Tier 2: Smart token heuristics for remaining unmapped core fields
    for orig, _, lower in header_info:
        if orig in assigned_headers:
            continue
        tokens = set(re.split(r"[\s\-_/\(\)\[\],]+", lower))

        if "ipa" not in mapping and (
            "ipa" in tokens
            or "phonetic" in lower
            or "phát âm" in lower
            or "phat am" in lower
            or "phiên âm" in lower
            or "phien am" in lower
            or "pronunciation" in lower
        ):
            mapping["ipa"] = orig
            assigned_headers.add(orig)
        elif "part_of_speech" not in mapping and (
            "pos" in tokens
            or "từ loại" in lower
            or "tu loai" in lower
            or "loại từ" in lower
            or "loai tu" in lower
        ):
            mapping["part_of_speech"] = orig
            assigned_headers.add(orig)
        elif "definition" not in mapping and (
            "định nghĩa" in lower
            or "dinh nghia" in lower
            or "nghĩa" in lower
            or "meaning" in lower
            or "translation" in lower
        ):
            mapping["definition"] = orig
            assigned_headers.add(orig)
        elif "term" not in mapping and (
            "word" in tokens
            or "từ vựng" in lower
            or "tu vung" in lower
            or "vocab" in tokens
        ):
            mapping["term"] = orig
            assigned_headers.add(orig)

    return mapping
