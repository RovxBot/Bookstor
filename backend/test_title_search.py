"""
Test title search to see what's happening
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from src.services.api_integration_manager import api_integration_manager
from src.database import SessionLocal

async def main():
    test_queries = [
        "The Hobbit",
        "Harry Potter",
        "Fallout"
    ]
    
    db = SessionLocal()
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Searching for: '{query}'")
        print(f"{'='*80}\n")
        
        try:
            results = await api_integration_manager.search_by_title(query, db, max_results=3)
            
            if results:
                print(f"✓ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n  {i}. {result.title}")
                    print(f"     Authors: {result.authors}")
                    print(f"     ISBN: {result.isbn}")
            else:
                print("✗ No results found")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
