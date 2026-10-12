"""Unit and integration tests for Mandarin Chinese language support."""

import pytest
from pydantic import ValidationError
from vocabmaster.db.connection import get_db
from vocabmaster.db import repository
from vocabmaster.models.base import Language
from vocabmaster.models.factory import validate_language_fields
from vocabmaster.models.languages.chinese import (
    ChineseFields,
    normalize_pinyin,
    extract_tone_numbers_from_pinyin,
)
from vocabmaster.importer.processor import import_vocabulary_file


def test_chinese_fields_validation_success():
    data = {
        "simplified": "学习",
        "traditional": "學習",
        "pinyin": "xuéxí",
        "pinyin_numbered": "xue2xi2",
        "tone_sequence": "2-2",
        "hsk_level": "HSK 1",
        "character_components": ["学", "习"],
        "radical": "子",
        "stroke_count": 8,
    }
    validated = validate_language_fields(Language.ZH, data)
    assert validated["simplified"] == "学习"
    assert validated["traditional"] == "學習"
    assert validated["pinyin"] == "xuéxí"
    assert validated["tone_sequence"] == "2-2"
    assert validated["hsk_level"] == "HSK 1"
    assert validated["radical"] == "子"


def test_chinese_fields_validation_failure():
    # pinyin is required
    with pytest.raises(ValidationError):
        validate_language_fields(Language.ZH, {"simplified": "学习"})

    # Invalid HSK level
    with pytest.raises(ValidationError):
        validate_language_fields(
            Language.ZH,
            {"pinyin": "xuéxí", "hsk_level": "HSK 99"}
        )


def test_pinyin_normalization_and_tones():
    assert normalize_pinyin("  Nǐ Hǎo  ") == "nǐ hǎo"

    # Tone 3 and 3
    tones_nihao = extract_tone_numbers_from_pinyin("nǐ hǎo")
    assert tones_nihao == [3, 3]

    # Tone 3 and 1
    tones_beijing = extract_tone_numbers_from_pinyin("běijīng")
    assert tones_beijing == [3, 1]

    # Tone 4 and neutral (5)
    tones_xiexie = extract_tone_numbers_from_pinyin("xièxie")
    assert tones_xiexie == [4, 5]


def test_chinese_vocabulary_import_and_persistence(temp_db_path, test_user):
    with get_db(temp_db_path) as conn:
        deck = repository.create_deck(conn, "deck-zh-test", test_user["id"], "HSK 1 Vocab", target_language="zh")
        assert deck["target_language"] == "zh"

        csv_content = (
            "term,definition,pinyin,hsk_level\n"
            "你好,Xin chào / Hello,nǐ hǎo,HSK 1\n"
            "谢谢,Cảm ơn / Thank you,xièxie,HSK 1\n"
        ).encode("utf-8")

        res = import_vocabulary_file(conn, test_user["id"], "deck-zh-test", csv_content, "hsk1.csv")
        assert res.imported_count == 2
        assert res.error_count == 0

        items = repository.list_vocab_items_by_deck(conn, "deck-zh-test", test_user["id"])
        assert len(items) == 2

        term_map = {item["term"]: item for item in items}
        assert "你好" in term_map
        assert "谢谢" in term_map

        item_nihao = term_map["你好"]
        assert item_nihao["language"] == "zh"
        assert item_nihao["language_specific_fields"]["pinyin"] == "nǐ hǎo"
        assert item_nihao["language_specific_fields"]["hsk_level"] == "HSK 1"
