"""
Test each API individually for title search
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from src.services.google_books import google_books_service
from src.services.openlibrary import openlibrary_service
from src.services.hardcover import hardcover_service

async def main():
    query = "Harry Potter"
    
    print(f"\n{'='*80}")
    print(f"Testing individual APIs for: '{query}'")
    print(f"{'='*80}\n")
    
    # Test Google Books
    print("1. GOOGLE BOOKS:")
    print("-" * 80)
    try:
        results = await asyncio.wait_for(
            google_books_service.search_by_title(query, max_results=3),
            timeout=5.0
        )
        if results:
            print(f"✓ Found {len(results)} results")
            for r in results[:2]:
                print(f"  - {r.title} by {r.authors}")
        else:
            print("✗ No results")
    except asyncio.TimeoutError:
        print("✗ TIMEOUT after 5 seconds")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()
    
    # Test Open Library
    print("2. OPEN LIBRARY:")
    print("-" * 80)
    try:
        results = await asyncio.wait_for(
            openlibrary_service.search_by_title(query, max_results=3),
            timeout=5.0
        )
        if results:
            print(f"✓ Found {len(results)} results")
            for r in results[:2]:
                print(f"  - {r.title} by {r.authors}")
        else:
            print("✗ No results")
    except asyncio.TimeoutError:
        print("✗ TIMEOUT after 5 seconds")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()
    
    # Test Hardcover
    print("3. HARDCOVER:")
    print("-" * 80)
    try:
        results = await asyncio.wait_for(
            hardcover_service.search_by_title(query, max_results=3),
            timeout=5.0
        )
        if results:
            print(f"✓ Found {len(results)} results")
            for r in results[:2]:
                print(f"  - {r.title} by {r.authors}")
        else:
            print("✗ No results")
    except asyncio.TimeoutError:
        print("✗ TIMEOUT after 5 seconds")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
