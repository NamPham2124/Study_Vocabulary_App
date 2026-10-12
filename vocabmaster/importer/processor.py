"""Core import processor coordinating mapping, validation, and database persistence."""

import uuid
from typing import Any, Dict, List, Literal, NamedTuple, Optional
import sqlite3
from pydantic import ValidationError

from vocabmaster.db import repository
from vocabmaster.importer.column_mapper import build_column_mapping
from vocabmaster.importer.csv_importer import parse_csv_data
from vocabmaster.importer.xlsx_importer import parse_xlsx_data
from vocabmaster.models.base import Language
from vocabmaster.models.factory import validate_language_fields


class ImportResult(NamedTuple):
    batch_id: str
    filename: str
    total_rows: int
    imported_count: int
    skipped_count: int
    error_count: int
    errors: List[Dict[str, Any]]


DedupMode = Literal["skip", "overwrite", "allow_duplicates"]


def import_vocabulary_file(
    conn: sqlite3.Connection,
    user_id: str,
    deck_id: str,
    file_bytes: bytes,
    filename: str,
    dedup_strategy: DedupMode = "skip",
) -> ImportResult:
    """
    Import vocabulary from CSV or XLSX with fault-tolerant processing and audit logging.
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
            f"Detected headers: {headers}. Need at least 'term' and 'definition'."
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

    for idx, row in enumerate(rows, start=2):  # Row 1 is header
        try:
            term = row.get(col_map["term"], "").strip()
            definition = row.get(col_map["definition"], "").strip()

            if not term:
                errors.append({"row": idx, "error": "Empty term"})
                continue
            if not definition:
                errors.append({"row": idx, "term": term, "error": "Empty definition"})
                continue

            ipa = row.get(col_map.get("ipa", ""), "").strip()
            pos = row.get(col_map.get("part_of_speech", ""), "").strip()
            notes = row.get(col_map.get("notes", ""), "").strip()

            # Examples parsing (split by semicolon or newline if present)
            examples_raw = row.get(col_map.get("examples", ""), "").strip()
            examples = [e.strip() for e in re_split(examples_raw) if e.strip()] if examples_raw else []

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
            for field in ("reading", "romaji", "jlpt_level", "cefr_level", "article", "gender", "plural_form", "tone", "sino_vietnamese"):
                if field in col_map:
                    val = row.get(col_map[field], "").strip()
                    if val:
                        lang_fields_raw[field] = val

            validated_lang_fields = validate_language_fields(target_lang, lang_fields_raw)

            existing = repository.find_vocab_by_term(conn, deck_id, term)
            if existing:
                if dedup_strategy == "skip":
                    skipped_count += 1
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
                            "examples": examples or existing["examples"],
                            "synonyms": synonyms or existing["synonyms"],
                            "antonyms": antonyms or existing["antonyms"],
                            "tags": tags or existing["tags"],
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
                "language_specific_fields": validated_lang_fields,
            }
            repository.create_vocab_item(conn, item_data)

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
    """Split comma, semicolon or newline delimited list."""
    import re
    return re.split(r"[;\n|]", text)
