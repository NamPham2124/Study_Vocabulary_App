"""Unit tests for language-specific linguistic models and validation."""

import pytest
from pydantic import ValidationError
from vocabmaster.models.base import Language
from vocabmaster.models.factory import validate_language_fields


def test_english_fields_validation():
    valid_data = {
        "cefr_level": "B2",
        "collocations": ["take into account", "bear in mind"],
        "phrasal_verbs": ["look up to"],
    }
    validated = validate_language_fields(Language.EN, valid_data)
    assert validated["cefr_level"] == "B2"
    assert len(validated["collocations"]) == 2

    # Invalid CEFR level
    with pytest.raises(ValidationError):
        validate_language_fields(Language.EN, {"cefr_level": "Z9"})


def test_japanese_fields_validation():
    valid_data = {
        "reading": "たべる",
        "romaji": "taberu",
        "jlpt_level": "N5",
        "verb_type": "ichidan",
        "transitivity": "transitive",
    }
    validated = validate_language_fields(Language.JA, valid_data)
    assert validated["reading"] == "たべる"
    assert validated["jlpt_level"] == "N5"

    # Missing required reading field
    with pytest.raises(ValidationError):
        validate_language_fields(Language.JA, {"romaji": "taberu"})

    # Invalid JLPT level
    with pytest.raises(ValidationError):
        validate_language_fields(Language.JA, {"reading": "たべる", "jlpt_level": "N10"})


def test_german_fields_validation():
    valid_data = {
        "article": "die",
        "gender": "feminine",
        "plural_form": "die Blumen",
        "case_governed": "Akkusativ",
    }
    validated = validate_language_fields(Language.DE, valid_data)
    assert validated["article"] == "die"
    assert validated["gender"] == "feminine"

    # Invalid article
    with pytest.raises(ValidationError):
        validate_language_fields(Language.DE, {"article": "invalid_article"})


def test_romance_and_vietnamese_validation():
    # Spanish/French
    romance_data = {"gender": "masculine", "plural_form": "livres"}
    assert validate_language_fields(Language.FR, romance_data)["gender"] == "masculine"

    # Vietnamese
    vi_data = {"tone": "hỏi", "sino_vietnamese": "Thủy (水)"}
    validated_vi = validate_language_fields(Language.VI, vi_data)
    assert validated_vi["tone"] == "hỏi"
    assert validated_vi["sino_vietnamese"] == "Thủy (水)"

    # Invalid Vietnamese tone
    with pytest.raises(ValidationError):
        validate_language_fields(Language.VI, {"tone": "invalid_tone"})
