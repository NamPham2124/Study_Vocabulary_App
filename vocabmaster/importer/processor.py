"""Core import processor coordinating mapping, validation, root-word parsing, and persistence."""

import re
import uuid
from typing import Any, Dict, List, Literal, NamedTuple, Optional, Tuple
import sqlite3
from pydantic import ValidationError

from vocabmaster.db import repository
from vocabmaster.importer.column_mapper import build_column_mapping
from vocabmaster.importer.csv_importer import parse_csv_data
from vocabmaster.importer.xlsx_importer import parse_xlsx_data
from vocabmaster.models.base import Language
from vocabmaster.models.factory import validate_language_fields
from vocabmaster.models.languages.chinese import normalize_pinyin, extract_tone_numbers_from_pinyin


class ImportResult(NamedTuple):
    batch_id: str
    filename: str
    total_rows: int
    imported_count: int
    skipped_count: int
    error_count: int
    errors: List[Dict[str, Any]]


DedupMode = Literal["skip", "overwrite", "merge", "allow_duplicates"]

ROOT_WORD_PATTERNS = [
    re.compile(r"^[↳\->\*\s]*(?:root\s*word|từ\s*gốc|root)\s*:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^[↳\->]+\s*(.+)$"),
]


def extract_root_marker(raw_term: str) -> Optional[str]:
    """Check if the term string contains a root-word marker like '↳ Root word: extend'."""
    cleaned = raw_term.strip()
    for pattern in ROOT_WORD_PATTERNS:
        m = pattern.match(cleaned)
        if m:
            clean_term = m.group(1).strip()
            # Prevent empty term
            if clean_term:
                return clean_term
    return None


def parse_tabular_text(text_data: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Parse text copied directly from Excel / Google Sheets or textareas."""
    return parse_csv_data(text_data.encode("utf-8"))


def preview_vocabulary_import(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: str,
    file_bytes: bytes,
    filename: str,
) -> Dict[str, Any]:
    """
    Parse and validate rows for the multi-step import wizard preview without committing.
    """
    deck = repository.get_deck_by_id(conn, deck_id, user_id)
    if not deck:
        raise ValueError(f"Deck {deck_id} does not exist or user has no access")

    target_lang = Language(deck.get("target_language", "en"))
    ext = filename.lower().split(".")[-1] if "." in filename else ""

    if ext == "xlsx":
        headers, rows = parse_xlsx_data(file_bytes)
        file_type = "xlsx"
    else:
        headers, rows = parse_csv_data(file_bytes)
        file_type = "csv"

    col_map = build_column_mapping(headers)

    preview_rows = []
    errors = []
    has_term = "term" in col_map
    has_def = "definition" in col_map

    if not has_term or not has_def:
        errors.append({
            "row": 0,
            "error": f"Missing required columns. Found: {headers}. Need at least term and definition."
        })

    for idx, row in enumerate(rows[:50], start=2):  # Preview first 50 rows
        term_raw = row.get(col_map.get("term", ""), "").strip() if has_term else ""
        def_raw = row.get(col_map.get("definition", ""), "").strip() if has_def else ""
        ipa_raw = row.get(col_map.get("ipa", ""), "").strip()
        pos_raw = row.get(col_map.get("part_of_speech", ""), "").strip()
        root_raw = row.get(col_map.get("root_word", ""), "").strip()

        is_root_marker = bool(extract_root_marker(term_raw)) if term_raw else False

        preview_rows.append({
            "row_number": idx,
            "term": term_raw,
            "definition": def_raw,
            "ipa": ipa_raw,
            "part_of_speech": pos_raw,
            "root_word": root_raw,
            "is_root_marker": is_root_marker,
            "is_valid": bool(term_raw and def_raw),
        })

    return {
        "filename": filename,
        "file_type": file_type,
        "total_rows": len(rows),
        "detected_headers": headers,
        "column_mapping": col_map,
        "preview_rows": preview_rows,
        "target_language": target_lang.value,
        "errors": errors,
    }


def import_vocabulary_file(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: str,
    file_bytes: bytes,
    filename: str,
    dedup_strategy: DedupMode = "skip",
) -> ImportResult:
    """
    Import vocabulary with intelligent column mapping, root-word relationship preservation,
    multilingual validation, deduplication, and atomic error isolation.
    """
    deck = repository.get_deck_by_id(conn, deck_id, user_id)
    if not deck:
        raise ValueError(f"Deck {deck_id} does not exist or user has no access")

    target_lang = Language(deck.get("target_language", "en"))
    ext = filename.lower().split(".")[-1] if "." in filename else ""

    if ext == "xlsx":
        headers, rows = parse_xlsx_data(file_bytes)
        file_type = "xlsx"
    else:
        headers, rows = parse_csv_data(file_bytes)
        file_type = "csv"

    col_map = build_column_mapping(headers)

    errors: List[Dict[str, Any]] = []
    imported_count = 0
    skipped_count = 0

    if "term" not in col_map or "definition" not in col_map:
        batch_id = str(uuid.uuid4())
        err_msg = (
            f"Missing required columns in {filename}. "
            f"Detected headers: {headers}. Need at least 'term' (or Từ vựng) and 'definition' (or Nghĩa tiếng Việt)."
        )
        errors.append({"row": 0, "error": err_msg})
        repository.create_import_batch(
            conn,
            {
                "id": batch_id,
                "user_id": user_id,
                "deck_id": deck_id,
                "filename": filename,
                "file_type": file_type,
                "total_rows": len(rows),
                "imported_count": 0,
                "skipped_count": 0,
                "error_count": 1,
                "errors": errors,
            },
        )
        return ImportResult(
            batch_id=batch_id,
            filename=filename,
            total_rows=len(rows),
            imported_count=0,
            skipped_count=0,
            error_count=1,
            errors=errors,
        )

    last_created_vocab_item = None

    for idx, row in enumerate(rows, start=2):  # Row 1 is header
        try:
            raw_term = row.get(col_map["term"], "").strip()
            definition = row.get(col_map["definition"], "").strip()

            if not raw_term:
                errors.append({"row": idx, "error": "Empty term or character"})
                continue
            if not definition:
                errors.append({"row": idx, "term": raw_term, "error": "Empty definition / meaning"})
                continue

            # Check if this row is a structured root-word row marker:
            # e.g. "↳ Root word: extend" or "↳ extend"
            is_root_row = False
            root_term_extracted = extract_root_marker(raw_term)
            if root_term_extracted is not None:
                is_root_row = True
                term = root_term_extracted
            else:
                term = raw_term

            ipa = row.get(col_map.get("ipa", ""), "").strip()
            pos = row.get(col_map.get("part_of_speech", ""), "").strip()
            notes = row.get(col_map.get("notes", ""), "").strip()
            mnemonics = row.get(col_map.get("mnemonics", ""), "").strip()

            # Root word from dedicated column if present
            col_root_word = row.get(col_map.get("root_word", ""), "").strip() if "root_word" in col_map else ""

            # Examples parsing
            examples_raw = row.get(col_map.get("examples", ""), "").strip()
            examples = [e.strip() for e in re_split(examples_raw) if e.strip()] if examples_raw else []

            # Example translation
            ex_trans_raw = row.get(col_map.get("example_translation", ""), "").strip()
            if ex_trans_raw and examples:
                examples[0] = f"{examples[0]} ({ex_trans_raw})"

            # Tags parsing
            tags_raw = row.get(col_map.get("tags", ""), "").strip()
            tags = [t.strip() for t in re_split(tags_raw) if t.strip()] if tags_raw else []

            # Synonyms & Antonyms
            syn_raw = row.get(col_map.get("synonyms", ""), "").strip()
            synonyms = [s.strip() for s in re_split(syn_raw) if s.strip()] if syn_raw else []
            ant_raw = row.get(col_map.get("antonyms", ""), "").strip()
            antonyms = [a.strip() for a in re_split(ant_raw) if a.strip()] if ant_raw else []

            # Language-specific fields
            lang_fields_raw: Dict[str, Any] = {}
            for field in (
                "pinyin", "tone", "hsk_level", "traditional", "simplified",
                "reading", "romaji", "jlpt_level", "cefr_level", "article",
                "gender", "plural_form", "sino_vietnamese"
            ):
                if field in col_map:
                    val = row.get(col_map[field], "").strip()
                    if val:
                        lang_fields_raw[field] = val

            # Normalize Chinese Pinyin if in Chinese deck
            if target_lang == Language.ZH:
                if "pinyin" in lang_fields_raw:
                    lang_fields_raw["pinyin"] = normalize_pinyin(lang_fields_raw["pinyin"])
                    # Auto tone sequence if tone not specified
                    if not lang_fields_raw.get("tone_sequence"):
                        extracted_tones = extract_tone_numbers_from_pinyin(lang_fields_raw["pinyin"])
                        if extracted_tones:
                            lang_fields_raw["tone_sequence"] = "-".join(str(t) for t in extracted_tones)

            validated_lang_fields = validate_language_fields(target_lang, lang_fields_raw)

            # Multiple Vietnamese meanings
            vietnamese_meanings = [m.strip() for m in re_split(definition) if m.strip()]

            # Deduplication checking
            existing = repository.find_vocab_by_term(conn, deck_id, term)
            if existing:
                if dedup_strategy == "skip":
                    # If existing vocabulary is missing IPA, POS, or mnemonics, but imported row provides it, backfill it!
                    backfill: Dict[str, Any] = {}
                    if not existing.get("ipa") and ipa:
                        backfill["ipa"] = ipa
                    if not existing.get("part_of_speech") and pos:
                        backfill["part_of_speech"] = pos
                    if not existing.get("mnemonics") and mnemonics:
                        backfill["mnemonics"] = mnemonics
                    if backfill:
                        repository.update_vocab_item(conn, existing["id"], user_id, backfill)

                    skipped_count += 1
                    if is_root_row and last_created_vocab_item:
                        # Link root relationship to existing item
                        repository.create_word_relationship(
                            conn, str(uuid.uuid4()), user_id,
                            source_vocab_id=last_created_vocab_item["id"],
                            target_vocab_id=existing["id"],
                            relation_type="root_word",
                            notes="Linked from import"
                        )
                    continue
                elif dedup_strategy == "merge":
                    # Merge missing fields
                    merged_meanings = list(dict.fromkeys(existing.get("vietnamese_meanings", []) + vietnamese_meanings))
                    merged_examples = list(dict.fromkeys(existing.get("examples", []) + examples))
                    repository.update_vocab_item(
                        conn,
                        vocab_id=existing["id"],
                        user_id=user_id,
                        updates={
                            "ipa": existing["ipa"] or ipa,
                            "part_of_speech": existing["part_of_speech"] or pos,
                            "vietnamese_meanings": merged_meanings,
                            "examples": merged_examples,
                            "mnemonics": existing["mnemonics"] or mnemonics,
                        },
                    )
                    imported_count += 1
                    continue
                elif dedup_strategy == "overwrite":
                    repository.update_vocab_item(
                        conn,
                        vocab_id=existing["id"],
                        user_id=user_id,
                        updates={
                            "definition": definition,
                            "ipa": ipa or existing["ipa"],
                            "part_of_speech": pos or existing["part_of_speech"],
                            "notes": notes or existing["notes"],
                            "mnemonics": mnemonics or existing["mnemonics"],
                            "examples": examples or existing["examples"],
                            "synonyms": synonyms or existing["synonyms"],
                            "antonyms": antonyms or existing["antonyms"],
                            "tags": tags or existing["tags"],
                            "vietnamese_meanings": vietnamese_meanings,
                            "language_specific_fields": validated_lang_fields or existing["language_specific_fields"],
                        },
                    )
                    imported_count += 1
                    continue

            # Create new vocabulary item
            vocab_id = str(uuid.uuid4())
            item_data = {
                "id": vocab_id,
                "deck_id": deck_id,
                "user_id": user_id,
                "language": target_lang.value,
                "term": term,
                "definition": definition,
                "ipa": ipa,
                "part_of_speech": pos,
                "examples": examples,
                "synonyms": synonyms,
                "antonyms": antonyms,
                "notes": notes,
                "tags": tags,
                "root_word": col_root_word,
                "root_word_id": None,
                "vietnamese_meanings": vietnamese_meanings,
                "english_definitions": [],
                "mnemonics": mnemonics,
                "audio_url": "",
                "is_favorite": False,
                "language_specific_fields": validated_lang_fields,
            }
            new_item = repository.create_vocab_item(conn, item_data)

            # If this row is a marked root word row (e.g. ↳ Root word: extend)
            if is_root_row and last_created_vocab_item:
                repository.create_word_relationship(
                    conn,
                    rel_id=str(uuid.uuid4()),
                    user_id=user_id,
                    source_vocab_id=last_created_vocab_item["id"],
                    target_vocab_id=vocab_id,
                    relation_type="root_word",
                    notes="Structured root word relationship parsed from import",
                )
                repository.update_vocab_item(
                    conn,
                    vocab_id=last_created_vocab_item["id"],
                    user_id=user_id,
                    updates={"root_word": term, "root_word_id": vocab_id},
                )
            else:
                last_created_vocab_item = new_item

            # Automatically create SRS card for spaced repetition
            card_id = str(uuid.uuid4())
            repository.create_srs_card(
                conn,
                {
                    "id": card_id,
                    "vocab_id": vocab_id,
                    "deck_id": deck_id,
                    "user_id": user_id,
                    "state": "NEW",
                },
            )
            imported_count += 1

        except ValidationError as ve:
            errors.append({"row": idx, "term": row.get(col_map.get("term", ""), ""), "error": f"Linguistic validation error: {str(ve)}"})
        except Exception as exc:
            errors.append({"row": idx, "error": str(exc)})

    batch_id = str(uuid.uuid4())
    repository.create_import_batch(
        conn,
        {
            "id": batch_id,
            "user_id": user_id,
            "deck_id": deck_id,
            "filename": filename,
            "file_type": file_type,
            "total_rows": len(rows),
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "error_count": len(errors),
            "errors": errors,
        },
    )

    return ImportResult(
        batch_id=batch_id,
        filename=filename,
        total_rows=len(rows),
        imported_count=imported_count,
        skipped_count=skipped_count,
        error_count=len(errors),
        errors=errors,
    )


def re_split(text: str) -> List[str]:
    """Split comma, semicolon, newline, or pipe delimited lists."""
    return [p.strip() for p in re.split(r"[;\n|]", str(text)) if p.strip()]
