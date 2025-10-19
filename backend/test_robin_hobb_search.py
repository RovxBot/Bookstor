"""
Test search for Robin Hobb to see what data is returned
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from src.services.api_integration_manager import api_integration_manager
from src.database import SessionLocal

async def main():
    query = "Robin Hobb"
    
    print(f"\n{'='*80}")
    print(f"Searching for: '{query}'")
    print(f"{'='*80}\n")
    
    db = SessionLocal()
    
    try:
        results = await api_integration_manager.search_by_title(query, db, max_results=10)
        
        if results:
            print(f"✓ Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.title}")
                print(f"   Authors: {result.authors}")
                print(f"   ISBN: {result.isbn}")
                print(f"   Thumbnail: {result.thumbnail[:50] if result.thumbnail else None}...")
                print(f"   Publisher: {result.publisher}")
                print(f"   Page Count: {result.page_count}")
                print(f"   Description: {result.description[:100] if result.description else None}...")
                print()
        else:
            print("✗ No results found")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
