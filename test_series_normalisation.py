"""
Test that series names are normalised when fetching book data
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from src.services.api_integration_manager import api_integration_manager
from src.database import SessionLocal

async def main():
    # Test normalisation function directly
    print("\n" + "="*80)
    print("Testing series name normalisation:")
    print("="*80)
    
    test_cases = [
        "The Rain Wild Chronicles",
        "Rain Wild Chronicles",
        "A Song of Ice and Fire",
        "The Lord of the Rings",
        "Liveship Traders, Book",
        "The Hobbit Series",
        "Harry Potter Saga",
        "The Chronicles of Narnia",
    ]
    
    for original in test_cases:
        normalised = api_integration_manager.normalise_series_name(original)
        print(f"  '{original}' -> '{normalised}'")
    
    # Test with actual ISBN lookup
    print("\n" + "="*80)
    print("Testing ISBN lookup with series normalisation:")
    print("="*80)
    
    db = SessionLocal()
    
    # Test with a book that has series info
    isbn = "9780007383467"  # Ship of Magic
    print(f"\nLooking up ISBN: {isbn}")
    
    result = await api_integration_manager.search_by_isbn(isbn, db)
    
    if result:
        print(f"  Title: {result.title}")
        print(f"  Series: {result.series_name}")
        print(f"  Position: {result.series_position}")
    else:
        print("  No result found")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
