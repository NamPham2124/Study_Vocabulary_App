"""Robust CSV importer supporting various encodings and delimiters."""

import csv
import io
from typing import Any, Dict, List, Tuple


COMMON_DELIMITERS = [",", "\t", ";", "|"]


def detect_encoding_and_decode(data_bytes: bytes) -> str:
    """Decode bytes by trying utf-8-sig, utf-8, latin-1, and cp1252."""
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            return data_bytes.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return data_bytes.decode("utf-8", errors="replace")


def sniff_delimiter(text_sample: str) -> str:
    """Sniff CSV delimiter from sample text or default to comma."""
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(text_sample, delimiters=",\t;|")
        return dialect.delimiter
    except Exception:
        # Fallback heuristic: count occurrences in first non-empty line
        lines = [line for line in text_sample.splitlines() if line.strip()]
        if not lines:
            return ","
        first_line = lines[0]
        counts = {d: first_line.count(d) for d in COMMON_DELIMITERS}
        best_del = max(counts, key=counts.get)  # type: ignore
        return best_del if counts[best_del] > 0 else ","


def parse_csv_data(data_bytes: bytes) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Parse CSV bytes into header list and list of row dicts.
    """
    text = detect_encoding_and_decode(data_bytes)
    delimiter = sniff_delimiter(text[:4096])

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    headers = []
    rows = []

    for row_idx, row in enumerate(reader):
        if not row or all(not str(cell).strip() for cell in row):
            continue
        if not headers:
            headers = [c.replace("\ufeff", "").strip() for c in row]
            continue

        # Map row values to headers
        row_dict: Dict[str, str] = {}
        for col_idx, col_name in enumerate(headers):
            if col_idx < len(row):
                row_dict[col_name] = row[col_idx].strip()
            else:
                row_dict[col_name] = ""
        rows.append(row_dict)

    return headers, rows
