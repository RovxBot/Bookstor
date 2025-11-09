"""Unit tests for safe merge logic preventing cross‑book data contamination.

These tests operate purely in-memory and do not hit external APIs.
We import the manager and call the internal _merge_book_info_safe helper
with synthetic integration objects and GoogleBookInfo instances.
"""
from types import SimpleNamespace

from src.services.api_integration_manager import api_integration_manager, APIIntegrationManager
from src.schemas import GoogleBookInfo


def _integration(name: str, display: str, priority: int = 0):
    # Minimal attribute set used by merge logic (display_name)
    return SimpleNamespace(name=name, display_name=display, priority=priority)


def test_merge_preserves_canonical_and_adds_missing_fields():
    manager: APIIntegrationManager = api_integration_manager
    canonical = GoogleBookInfo(
        title="The Hobbit",
        authors=["J.R.R. Tolkien"],
        description=None,
        publisher="Allen & Unwin",
        published_date="1937",
        page_count=None,
        categories=["Fantasy"],
        thumbnail=None,
        isbn="9780547928227",
    )
    consistent = GoogleBookInfo(
        title="Hobbit",  # token overlap -> similarity should pass (hobbit)
        authors=["J.R.R. Tolkien"],
        description="A fantasy novel about Bilbo Baggins.",
        publisher="Allen & Unwin",  # same
        published_date="1937",  # same
        page_count=310,
        categories=["Adventure"],
        thumbnail="http://example/cover.jpg",
        isbn="9780547928227",
    )
    inconsistent = GoogleBookInfo(
        title="Advanced Quantum Mechanics",  # no token overlap
        authors=["Some Other Author"],
        description="Physics book should be discarded",
        publisher="Science Press",
        published_date="1999",
        page_count=999,
        categories=["Physics"],
        thumbnail="http://example/physics.jpg",
        isbn="9780547928227",  # Same ISBN but content should be rejected
    )

    merged = manager._merge_book_info_safe(
        [
            (_integration("google_books", "Google Books", 0), canonical),
            (_integration("open_library", "Open Library", 1), consistent),
            (_integration("hardcover", "Hardcover", 2), inconsistent),
        ],
        search_isbn="9780547928227",
    )

    assert merged is not None
    # Canonical title preserved
    assert merged.title == "The Hobbit"
    # Page count filled from consistent supplementary result
    assert merged.page_count == 310
    # Categories union: order may preserve canonical first
    assert set(merged.categories or []) == {"Fantasy", "Adventure"}
    # Thumbnail filled
    assert merged.thumbnail == "http://example/cover.jpg"
    # Inconsistent description NOT merged (canonical had None, but inconsistent should be discarded entirely)
    # We did merge description from consistent though, so ensure it's that one
    assert merged.description == "A fantasy novel about Bilbo Baggins."
    # Ensure physics category/author/publisher from inconsistent did not leak
    assert "Physics" not in (merged.categories or [])
    assert merged.publisher == "Allen & Unwin"
    assert merged.authors == ["J.R.R. Tolkien"]


def test_merge_rejects_author_mismatch_when_titles_match():
    manager: APIIntegrationManager = api_integration_manager
    canonical = GoogleBookInfo(
        title="Dragon Keeper",
        authors=["Robin Hobb"],
        isbn="9780553808124",
    )
    conflicting_author = GoogleBookInfo(
        title="Dragon Keeper",  # identical title
        authors=["Different Author"],
        description="Should not merge due to author mismatch",
        isbn="9780553808124",
    )
    merged = manager._merge_book_info_safe(
        [
            (_integration("google_books", "Google Books", 0), canonical),
            (_integration("open_library", "Open Library", 1), conflicting_author),
        ],
        search_isbn="9780553808124",
    )
    assert merged is not None
    # Description should remain None because supplementary was rejected
    assert merged.description is None
    # Authors unchanged
    assert merged.authors == ["Robin Hobb"]
