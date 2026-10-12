"""Unit and integration tests for advanced vocabulary importer features:
- Root word hierarchy parsing (↳ Root word: ...)
- Preview before import
- Pasted tabular data support
- Deduplication strategies (skip, overwrite, merge, allow_duplicates)
- Automatic SRS card creation
"""

import pytest
from vocabmaster.db.connection import get_db
from vocabmaster.db import repository
from vocabmaster.importer.processor import (
    import_vocabulary_file,
    preview_vocabulary_import,
    parse_tabular_text,
    extract_root_marker,
)


def test_root_marker_extraction():
    assert extract_root_marker("↳ Root word: inspect") == "inspect"
    assert extract_root_marker("↳Từ gốc: act") == "act"
    assert extract_root_marker("↳ root: play") == "play"
    assert extract_root_marker("-> Root word: construct") == "construct"
    assert extract_root_marker("↳ build") == "build"
    assert extract_root_marker("regular_word") is None


def test_root_word_hierarchy_import_and_relationship_linking(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-root-test", test_user["id"], "Word Families", target_language="en")

        csv_content = (
            "term,definition\n"
            "inspection,the act of looking at something carefully\n"
            "↳ Root word: inspect,to look at something carefully to check its condition\n"
        ).encode("utf-8")

        res = import_vocabulary_file(conn, test_user["id"], "deck-root-test", csv_content, "words.csv")
        assert res.imported_count == 2

        items = repository.list_vocab_items(conn, deck_id="deck-root-test", user_id=test_user["id"])
        assert len(items) == 2

        item_map = {item["term"]: item for item in items}
        # Term must NEVER store the raw marker prefix
        assert "inspection" in item_map
        assert "inspect" in item_map
        assert "↳ Root word: inspect" not in item_map

        inspection_item = item_map["inspection"]
        inspect_item = item_map["inspect"]

        # The preceding word should have root_word pointing to 'inspect' and root_word_id
        assert inspection_item["root_word"] == "inspect"
        assert inspection_item["root_word_id"] == inspect_item["id"]

        # Structured relationship should be recorded
        rels = repository.list_relationships_for_vocab(conn, inspection_item["id"], test_user["id"])
        assert len(rels) >= 1
        assert rels[0]["relation_type"] == "root_word"
        assert rels[0]["target_vocab_id"] == inspect_item["id"]


def test_import_preview_functionality(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-prev-test", test_user["id"], "Preview Deck", target_language="en")

        csv_content = (
            "term,definition,ipa,part_of_speech\n"
            "ephemeral,lasting for a very short time,/ɪˈfem.ər.əl/,adj\n"
            "ubiquitous,present everywhere,/juːˈbɪk.wə.təs/,adj\n"
        ).encode("utf-8")

        preview = preview_vocabulary_import(conn, test_user["id"], "deck-prev-test", csv_content, "preview.csv")
        assert preview["total_rows"] == 2
        assert len(preview["preview_rows"]) == 2
        assert preview["preview_rows"][0]["term"] == "ephemeral"
        assert preview["preview_rows"][0]["is_valid"] is True
        assert preview["errors"] == []

        # Ensure no items were actually committed to database during preview
        items = repository.list_vocab_items(conn, deck_id="deck-prev-test", user_id=test_user["id"])
        assert len(items) == 0


def test_pasted_tabular_text_import(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-paste-test", test_user["id"], "Paste Deck", target_language="en")

        tsv_data = "term\tdefinition\tpart_of_speech\npersevere\tcontinue in a course of action\tverb\nresilient\table to withstand difficulties\tadj\n"
        headers, rows = parse_tabular_text(tsv_data)
        assert "term" in headers
        assert len(rows) == 2

        res = import_vocabulary_file(
            conn, test_user["id"], "deck-paste-test", tsv_data.encode("utf-8"), "pasted.tsv"
        )
        assert res.imported_count == 2

        items = repository.list_vocab_items(conn, deck_id="deck-paste-test", user_id=test_user["id"])
        assert len(items) == 2
        terms = [it["term"] for it in items]
        assert "persevere" in terms
        assert "resilient" in terms


def test_deduplication_merge_mode(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-dedup-test", test_user["id"], "Dedup Deck", target_language="en")

        # Initial import with 1 definition and no IPA
        csv1 = "term,definition\nserendipity,finding good things by chance\n".encode("utf-8")
        res1 = import_vocabulary_file(conn, test_user["id"], "deck-dedup-test", csv1, "v1.csv")
        assert res1.imported_count == 1

        # Second import with MERGE mode: adds IPA and an example
        csv2 = "term,definition,ipa,examples\nserendipity,may mắn bất ngờ,/ˌser.ənˈdɪp.ə.ti/,a fortunate stroke of serendipity\n".encode("utf-8")
        res2 = import_vocabulary_file(
            conn, test_user["id"], "deck-dedup-test", csv2, "v2.csv", dedup_strategy="merge"
        )
        assert res2.imported_count == 1

        items = repository.list_vocab_items(conn, deck_id="deck-dedup-test", user_id=test_user["id"])
        assert len(items) == 1
        item = items[0]
        assert item["ipa"] == "/ˌser.ənˈdɪp.ə.ti/"
        assert len(item["examples"]) >= 1
        assert "may mắn bất ngờ" in item["vietnamese_meanings"]


def test_srs_card_creation_on_import(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-srs-test", test_user["id"], "SRS Deck", target_language="en")

        csv_content = "term,definition\nword1,def1\nword2,def2\n".encode("utf-8")
        import_vocabulary_file(conn, test_user["id"], "deck-srs-test", csv_content, "srs.csv")

        # Check SRS cards
        cards = repository.get_new_cards(conn, test_user["id"], deck_id="deck-srs-test")
        assert len(cards) == 2
        for c in cards:
            assert c["state"] == "NEW"
            assert c["repetition_count"] == 0
            assert c["ease_factor"] == 2.5
