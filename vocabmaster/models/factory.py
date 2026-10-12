"""Factory for validating and serializing language-specific vocabulary items."""

from typing import Any, Dict
from pydantic import ValidationError
from vocabmaster.models.base import Language
from vocabmaster.models.languages.english import EnglishFields
from vocabmaster.models.languages.chinese import ChineseFields
from vocabmaster.models.languages.japanese import JapaneseFields
from vocabmaster.models.languages.german import GermanFields
from vocabmaster.models.languages.romance import RomanceFields
from vocabmaster.models.languages.vietnamese import VietnameseFields


LANGUAGE_FIELD_MAP = {
    Language.EN: EnglishFields,
    Language.ZH: ChineseFields,
    Language.JA: JapaneseFields,
    Language.DE: GermanFields,
    Language.ES: RomanceFields,
    Language.FR: RomanceFields,
    Language.VI: VietnameseFields,
}


def validate_language_fields(
    language: Language, fields_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate and normalize language-specific fields.
    Raises ValidationError if the fields violate language schema.
    Returns cleaned dictionary.
    """
    if not fields_data:
        return {}

    model_cls = LANGUAGE_FIELD_MAP.get(language)
    if not model_cls:
        # Fallback to returning raw dict for OTHER or unmapped languages
        return fields_data

    validated = model_cls(**fields_data)
    # Exclude None values to keep JSON compact
    return validated.model_dump(exclude_none=True)
