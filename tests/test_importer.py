"""Unit tests for CSV and XLSX imports, column mapping, and error resilience."""

import io
import openpyxl
import pytest
from vocabmaster.db.connection import get_db
from vocabmaster.db import repository
from vocabmaster.importer.processor import import_vocabulary_file
from vocabmaster.importer.column_mapper import build_column_mapping


def test_column_mapping_aliases():
    headers = ["Word", "Meaning", "Phonetic", "Loại từ", "Examples", "Tags"]
    mapping = build_column_mapping(headers)

    assert mapping["term"] == "Word"
    assert mapping["definition"] == "Meaning"
    assert mapping["ipa"] == "Phonetic"
    assert mapping["part_of_speech"] == "Loại từ"
    assert mapping["examples"] == "Examples"
    assert mapping["tags"] == "Tags"


def test_csv_import_success_with_bom_and_semicolon(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-csv-1", test_user["id"], "English Tech")

    # CSV with UTF-8 BOM, semicolon separator, and Vietnamese column names
    csv_content = (
        "\ufeffTừ;Nghĩa;Phiên âm;Ví dụ\n"
        "algorithm;thuật toán;/ˈælɡərɪðəm/;A step-by-step problem-solving procedure\n"
        "heuristic;phương pháp kinh nghiệm;/hjʊəˈrɪstɪk/;A practical shortcut\n"
    ).encode("utf-8-sig")

    with get_db(temp_db_path) as conn:
        res = import_vocabulary_file(
            conn=conn,
            user_id=test_user["id"],
            deck_id="deck-csv-1",
            file_bytes=csv_content,
            filename="tech_terms.csv",
        )

        assert res.total_rows == 2
        assert res.imported_count == 2
        assert res.skipped_count == 0
        assert res.error_count == 0

        # Verify items in database
        items = repository.list_vocab_items(conn, deck_id="deck-csv-1", user_id=test_user["id"])
        assert len(items) == 2
        terms = {i["term"]: i for i in items}
        assert "algorithm" in terms
        assert terms["algorithm"]["definition"] == "thuật toán"
        assert terms["algorithm"]["ipa"] == "/ˈælɡərɪðəm/"

        # Verify SRS cards auto-created
        card = repository.get_srs_card_by_vocab_id(conn, terms["algorithm"]["id"])
        assert card is not None
        assert card["state"] == "NEW"


def test_xlsx_import_success(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-xlsx-1", test_user["id"], "Japanese Core", target_language="ja")

    # Create XLSX in-memory
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Vocabulary"
    ws.append(["Term", "Definition", "Reading", "JLPT"])
    ws.append(["猫", "Cat", "ねこ", "N5"])
    ws.append(["犬", "Dog", "いぬ", "N5"])

    xlsx_stream = io.BytesIO()
    wb.save(xlsx_stream)
    xlsx_bytes = xlsx_stream.getvalue()

    with get_db(temp_db_path) as conn:
        res = import_vocabulary_file(
            conn=conn,
            user_id=test_user["id"],
            deck_id="deck-xlsx-1",
            file_bytes=xlsx_bytes,
            filename="japanese_vocab.xlsx",
        )

        assert res.total_rows == 2
        assert res.imported_count == 2
        assert res.error_count == 0

        items = repository.list_vocab_items(conn, deck_id="deck-xlsx-1", user_id=test_user["id"])
        assert len(items) == 2
        cat = next(i for i in items if i["term"] == "猫")
        assert cat["language_specific_fields"]["reading"] == "ねこ"
        assert cat["language_specific_fields"]["jlpt_level"] == "N5"


def test_import_fault_tolerance(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-fault-1", test_user["id"], "Fault Test")

    # Row 1 is valid, Row 2 has empty term, Row 3 has empty definition, Row 4 is valid
    csv_content = (
        "term,definition\n"
        "valid_one,first valid\n"
        ",missing term\n"
        "missing_def,\n"
        "valid_two,second valid\n"
    ).encode("utf-8")

    with get_db(temp_db_path) as conn:
        res = import_vocabulary_file(
            conn=conn,
            user_id=test_user["id"],
            deck_id="deck-fault-1",
            file_bytes=csv_content,
            filename="faulty.csv",
        )

        assert res.total_rows == 4
        assert res.imported_count == 2
        assert res.error_count == 2
        assert len(res.errors) == 2


def test_import_deduplication_strategies(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-dedup-1", test_user["id"], "Dedup Test")

    csv_initial = "term,definition\napple,quả táo\n".encode("utf-8")
    with get_db(temp_db_path) as conn:
        import_vocabulary_file(conn, test_user["id"], "deck-dedup-1", csv_initial, "init.csv")

    # 1. Strategy = skip
    csv_update = "term,definition\napple,trái táo mới\nbanana,chuối\n".encode("utf-8")
    with get_db(temp_db_path) as conn:
        res_skip = import_vocabulary_file(
            conn, test_user["id"], "deck-dedup-1", csv_update, "skip.csv", dedup_strategy="skip"
        )
        assert res_skip.imported_count == 1  # banana imported
        assert res_skip.skipped_count == 1   # apple skipped

        item = repository.find_vocab_by_term(conn, "deck-dedup-1", "apple")
        assert item["definition"] == "quả táo"

    # 2. Strategy = overwrite
    with get_db(temp_db_path) as conn:
        res_overwrite = import_vocabulary_file(
            conn, test_user["id"], "deck-dedup-1", csv_update, "overwrite.csv", dedup_strategy="overwrite"
        )
        assert res_overwrite.imported_count == 2
        item = repository.find_vocab_by_term(conn, "deck-dedup-1", "apple")
        assert item["definition"] == "trái táo mới"
