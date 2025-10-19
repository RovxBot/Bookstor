"""
Test what Google Books API returns for ISBN
"""
import asyncio
import httpx
import json

async def test_google_books_isbn(isbn: str):
    """Test Google Books API response"""
    print(f"\nTesting Google Books API for ISBN: {isbn}")
    print("="*80)
    
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10.0)
        data = response.json()
        
        if data.get("totalItems", 0) == 0:
            print("No results found")
            return
        
        item = data["items"][0]
        volume_info = item.get("volumeInfo", {})
        
        print(f"\nTitle: {volume_info.get('title')}")
        print(f"Authors: {volume_info.get('authors')}")
        print(f"Publisher: {volume_info.get('publisher')}")
        print(f"Published Date: {volume_info.get('publishedDate')}")
        
        # Check for ISBN in industryIdentifiers
        print(f"\nIndustry Identifiers:")
        identifiers = volume_info.get("industryIdentifiers", [])
        for identifier in identifiers:
            print(f"  {identifier.get('type')}: {identifier.get('identifier')}")
        
        print(f"\nFull volumeInfo keys: {list(volume_info.keys())}")

async def main():
    test_isbns = [
        "9780744016307",  # Fallout
        "9780061561658",  # Dragon Haven
        "9780547928227",  # Hobbit
    ]
    
    for isbn in test_isbns:
        await test_google_books_isbn(isbn)
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())
