"""Importer package root."""

from vocabmaster.importer.processor import (
    import_vocabulary_file,
    preview_vocabulary_import,
    parse_tabular_text,
    extract_root_marker,
    ImportResult,
    DedupMode,
)
from vocabmaster.importer.column_mapper import build_column_mapping
from vocabmaster.importer.csv_importer import parse_csv_data
from vocabmaster.importer.xlsx_importer import parse_xlsx_data

__all__ = [
    "import_vocabulary_file",
    "preview_vocabulary_import",
    "parse_tabular_text",
    "extract_root_marker",
    "ImportResult",
    "DedupMode",
    "build_column_mapping",
    "parse_csv_data",
    "parse_xlsx_data",
]
