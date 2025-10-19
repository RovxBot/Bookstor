"""
Test Open Library search for Robin Hobb
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from src.services.openlibrary import openlibrary_service

async def main():
    query = "Robin Hobb Ship of Magic"
    
    print(f"\n{'='*80}")
    print(f"Testing Open Library for: '{query}'")
    print(f"{'='*80}\n")
    
    try:
        results = await asyncio.wait_for(
            openlibrary_service.search_by_title(query, max_results=5),
            timeout=10.0
        )
        
        if results:
            print(f"✓ Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.title}")
                print(f"   Authors: {result.authors}")
                print(f"   ISBN: {result.isbn}")
                print()
        else:
            print("✗ No results found")
    except asyncio.TimeoutError:
        print("✗ TIMEOUT")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
