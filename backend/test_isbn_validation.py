"""Parametrized async tests validating ISBN search returns expected title fragment."""
import pytest
from src.services.api_integration_manager import APIIntegrationManager
from src.database import SessionLocal

ISBN_TITLE_CASES = [
    ("9780744016307", "Fallout"),
    # Google Books returns Dragon Keeper for this ISBN (first book of Rain Wild Chronicles)
    ("9780061561658", "Dragon"),  # match broader fragment
    ("9780547928227", "Hobbit"),
]


@pytest.mark.external
@pytest.mark.asyncio
@pytest.mark.parametrize("isbn,expected", ISBN_TITLE_CASES)
async def test_isbn_lookup_matches_title(skip_if_offline, isbn: str, expected: str):
    db = SessionLocal()
    try:
        manager = APIIntegrationManager()
        result = await manager.search_by_isbn(isbn, db)
        assert result is not None, f"No result for ISBN {isbn}"
        # ISBN normalization
        norm_isbn = isbn.replace("-", "").replace(" ", "")
        norm_result = result.isbn.replace("-", "").replace(" ", "") if result.isbn else ""
        assert norm_isbn == norm_result, f"ISBN mismatch {norm_isbn} != {norm_result}"
        title_lower = result.title.lower()
        assert expected.lower() in title_lower, (
            f"Title '{result.title}' missing expected fragment '{expected}'"
        )
    finally:
        db.close()
