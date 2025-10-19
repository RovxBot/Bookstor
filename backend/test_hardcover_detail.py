"""
Test what Hardcover is actually returning for ISBN 0975126016
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from src.services.hardcover import hardcover_service

async def main():
    isbn = "0975126016"
    
    print(f"\n{'='*80}")
    print(f"Testing Hardcover API for ISBN: {isbn}")
    print(f"{'='*80}\n")
    
    try:
        result = await hardcover_service.search_by_isbn(isbn)
        if result:
            print(f"✓ Hardcover returned a result:")
            print(f"  ISBN: {result.isbn}")
            print(f"  Title: {result.title}")
            print(f"  Subtitle: {result.subtitle}")
            print(f"  Authors: {result.authors}")
            print(f"  Publisher: {result.publisher}")
            print(f"  Description: {result.description[:200] if result.description else None}...")
        else:
            print("✗ No result found")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
