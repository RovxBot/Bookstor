"""
Test ISBN 0975126016 to see what data is being returned
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from src.services.google_books import google_books_service
from src.services.openlibrary import openlibrary_service
from src.services.hardcover import hardcover_service

async def main():
    isbn = "0975126016"
    
    print(f"\n{'='*80}")
    print(f"Testing ISBN: {isbn}")
    print(f"Expected: From the Ground Up: The Memoirs of Alan Hickinbotham")
    print(f"{'='*80}\n")
    
    # Test Google Books
    print("1. GOOGLE BOOKS:")
    print("-" * 80)
    try:
        result = await google_books_service.search_by_isbn(isbn)
        if result:
            print(f"✓ Found result")
            print(f"  ISBN: {result.isbn}")
            print(f"  Title: {result.title}")
            print(f"  Subtitle: {result.subtitle}")
            print(f"  Authors: {result.authors}")
            print(f"  Publisher: {result.publisher}")
        else:
            print("✗ No result found")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()
    
    # Test Open Library
    print("2. OPEN LIBRARY:")
    print("-" * 80)
    try:
        result = await openlibrary_service.search_by_isbn(isbn)
        if result:
            print(f"✓ Found result")
            print(f"  ISBN: {result.isbn}")
            print(f"  Title: {result.title}")
            print(f"  Subtitle: {result.subtitle}")
            print(f"  Authors: {result.authors}")
            print(f"  Publisher: {result.publisher}")
        else:
            print("✗ No result found")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()
    
    # Test Hardcover
    print("3. HARDCOVER:")
    print("-" * 80)
    try:
        result = await hardcover_service.search_by_isbn(isbn)
        if result:
            print(f"✓ Found result")
            print(f"  ISBN: {result.isbn}")
            print(f"  Title: {result.title}")
            print(f"  Subtitle: {result.subtitle}")
            print(f"  Authors: {result.authors}")
            print(f"  Publisher: {result.publisher}")
        else:
            print("✗ No result found")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()
    
    # Test API Integration Manager (merged result)
    print("4. API INTEGRATION MANAGER (MERGED):")
    print("-" * 80)
    try:
        from src.services.api_integration_manager import api_integration_manager
        from src.database import SessionLocal
        
        db = SessionLocal()
        result = await api_integration_manager.search_by_isbn(isbn, db)
        db.close()
        
        if result:
            print(f"✓ Found merged result")
            print(f"  ISBN: {result.isbn}")
            print(f"  Title: {result.title}")
            print(f"  Subtitle: {result.subtitle}")
            print(f"  Authors: {result.authors}")
            print(f"  Publisher: {result.publisher}")
        else:
            print("✗ No merged result")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
