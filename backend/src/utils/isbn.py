"""ISBN utility functions.

Provides cleaning and validation helpers for ISBN-10 and ISBN-13.

Rules:
 - Accepts ISBN-10 (10 chars, may include X/x as check digit) or ISBN-13 (13 digits)
 - Hyphens and spaces are ignored during validation
 - Returns the cleaned (hyphen/space removed) version on success
 - Raises ValueError on invalid format/checksum
"""
from __future__ import annotations

import re
from typing import Optional

ISBN10_RE = re.compile(r"^[0-9]{9}[0-9Xx]$")
ISBN13_RE = re.compile(r"^[0-9]{13}$")


def clean_isbn(raw: str) -> str:
    """Remove hyphens, spaces, and trim."""
    return re.sub(r"[-\s]", "", raw or "").strip()


def is_valid_isbn10(isbn10: str) -> bool:
    isbn10 = clean_isbn(isbn10)
    if not ISBN10_RE.match(isbn10):
        return False
    total = 0
    for i, ch in enumerate(isbn10[:9]):
        total += (i + 1) * int(ch)
    check_char = isbn10[9].upper()
    check_val = 10 if check_char == "X" else int(check_char)
    return total % 11 == check_val


def is_valid_isbn13(isbn13: str) -> bool:
    isbn13 = clean_isbn(isbn13)
    if not ISBN13_RE.match(isbn13):
        return False
    total = 0
    for i, ch in enumerate(isbn13[:12]):
        factor = 1 if i % 2 == 0 else 3
        total += factor * int(ch)
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(isbn13[12])


def normalize_isbn(isbn: str) -> str:
    """Return cleaned ISBN if valid else raise."""
    cleaned = clean_isbn(isbn)
    if len(cleaned) == 10 and is_valid_isbn10(cleaned):
        return cleaned
    if len(cleaned) == 13 and is_valid_isbn13(cleaned):
        return cleaned
    raise ValueError("Invalid ISBN checksum or format")


def validate_isbn(isbn: Optional[str]) -> Optional[str]:
    """Validate optional ISBN (None allowed). Returns normalized or None."""
    if isbn is None:
        return None
    return normalize_isbn(isbn)

__all__ = [
    "clean_isbn",
    "is_valid_isbn10",
    "is_valid_isbn13",
    "normalize_isbn",
    "validate_isbn",
]
