"""Async tests hitting Google Books API for a few ISBNs.

These are lightweight integration probes; they will be skipped if network
access fails quickly. They are not strict assertions beyond ensuring at
least one item is returned.
"""
import httpx
import pytest

ISBN_CASES = [
    "9780744016307",  # Fallout
    "9780061561658",  # Dragon Haven
    "9780547928227",  # Hobbit
]


@pytest.mark.external
@pytest.mark.asyncio
@pytest.mark.parametrize("isbn", ISBN_CASES)
async def test_google_books_basic_isbn_lookup(skip_if_offline, isbn: str):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("totalItems", 0) > 0, f"No items for ISBN {isbn}" 
