"""
Test script for API integrations
Tests Open Library and Google Books APIs
"""
import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.openlibrary import openlibrary_service
from src.services.google_books import google_books_service
from src.services.api_integration_manager import api_integration_manager
from src.database import SessionLocal


async def test_openlibrary():
    """Test Open Library API"""
    print("\n" + "="*60)
    print("TESTING OPEN LIBRARY API")
    print("="*60)
    
    # Test ISBN search
    test_isbn = "9780547928227"  # The Hobbit
    print(f"\n1. Testing ISBN search: {test_isbn}")
    try:
        result = await openlibrary_service.search_by_isbn(test_isbn)
        if result:
            print(f"   ✅ SUCCESS")
            print(f"   Title: {result.title}")
            print(f"   Authors: {result.authors}")
            print(f"   Publisher: {result.publisher}")
            print(f"   Published: {result.published_date}")
            print(f"   Pages: {result.page_count}")
            print(f"   Description: {result.description[:100] if result.description else 'None'}...")
            print(f"   Thumbnail: {result.thumbnail}")
            print(f"   Series: {result.series_name}")
            print(f"   Edition: {result.edition}")
            print(f"   Format: {result.book_format}")
        else:
            print(f"   ❌ FAILED: No results returned")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test cover image
    print(f"\n2. Testing cover image fetch")
    try:
        cover_url = await openlibrary_service.get_cover_by_isbn(test_isbn)
        if cover_url:
            print(f"   ✅ SUCCESS: {cover_url}")
        else:
            print(f"   ⚠️  No cover found")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")


async def test_google_books():
    """Test Google Books API"""
    print("\n" + "="*60)
    print("TESTING GOOGLE BOOKS API")
    print("="*60)
    
    # Test ISBN search
    test_isbn = "9780547928227"  # The Hobbit
    print(f"\n1. Testing ISBN search: {test_isbn}")
    try:
        result = await google_books_service.search_by_isbn(test_isbn)
        if result:
            print(f"   ✅ SUCCESS")
            print(f"   Title: {result.title}")
            print(f"   Authors: {result.authors}")
            print(f"   Publisher: {result.publisher}")
            print(f"   Published: {result.published_date}")
            print(f"   Pages: {result.page_count}")
            print(f"   Description: {result.description[:100] if result.description else 'None'}...")
            print(f"   Thumbnail: {result.thumbnail}")
            print(f"   Series: {result.series_name}")
            print(f"   Google Books ID: {result.google_books_id}")
        else:
            print(f"   ❌ FAILED: No results returned")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test title search
    print(f"\n2. Testing title search: 'The Hobbit'")
    try:
        results = await google_books_service.search_by_title("The Hobbit", max_results=3)
        if results:
            print(f"   ✅ SUCCESS: Found {len(results)} results")
            for i, book in enumerate(results[:3], 1):
                print(f"   {i}. {book.title} by {', '.join(book.authors) if book.authors else 'Unknown'}")
        else:
            print(f"   ❌ FAILED: No results returned")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")


async def test_api_integration_manager():
    """Test API Integration Manager"""
    print("\n" + "="*60)
    print("TESTING API INTEGRATION MANAGER")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Check enabled integrations
        print("\n1. Checking enabled integrations")
        integrations = api_integration_manager.get_enabled_integrations(db)
        if integrations:
            print(f"   ✅ Found {len(integrations)} enabled integration(s):")
            for integration in integrations:
                print(f"   - {integration.display_name} (Priority: {integration.priority})")
        else:
            print(f"   ⚠️  No enabled integrations found")
        
        # Test ISBN search with manager
        test_isbn = "9780547928227"  # The Hobbit
        print(f"\n2. Testing merged ISBN search: {test_isbn}")
        try:
            result = await api_integration_manager.search_by_isbn(test_isbn, db)
            if result:
                print(f"   ✅ SUCCESS - Merged result:")
                print(f"   Title: {result.title}")
                print(f"   Authors: {result.authors}")
                print(f"   Publisher: {result.publisher}")
                print(f"   Published: {result.published_date}")
                print(f"   Pages: {result.page_count}")
                print(f"   Description: {result.description[:100] if result.description else 'None'}...")
                print(f"   Thumbnail: {result.thumbnail}")
                print(f"   Series: {result.series_name}")
                print(f"   Edition: {result.edition}")
                print(f"   Format: {result.book_format}")
                print(f"   Google Books ID: {result.google_books_id}")
            else:
                print(f"   ❌ FAILED: No results returned")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        # Test title search with manager
        print(f"\n3. Testing merged title search: 'Harry Potter'")
        try:
            results = await api_integration_manager.search_by_title("Harry Potter", db, max_results=5)
            if results:
                print(f"   ✅ SUCCESS: Found {len(results)} merged results")
                for i, book in enumerate(results[:5], 1):
                    print(f"   {i}. {book.title} by {', '.join(book.authors) if book.authors else 'Unknown'}")
            else:
                print(f"   ❌ FAILED: No results returned")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        
    finally:
        db.close()


async def test_different_isbns():
    """Test with multiple different ISBNs"""
    print("\n" + "="*60)
    print("TESTING MULTIPLE ISBNs")
    print("="*60)
    
    test_books = [
        ("9780547928227", "The Hobbit"),
        ("9780439708180", "Harry Potter and the Sorcerer's Stone"),
        ("9780061120084", "To Kill a Mockingbird"),
        ("9780316769174", "The Catcher in the Rye"),
    ]
    
    db = SessionLocal()
    try:
        for isbn, expected_title in test_books:
            print(f"\nTesting: {expected_title} ({isbn})")
            try:
                result = await api_integration_manager.search_by_isbn(isbn, db)
                if result:
                    print(f"   ✅ Found: {result.title}")
                    print(f"      Authors: {', '.join(result.authors) if result.authors else 'None'}")
                    print(f"      Has thumbnail: {'Yes' if result.thumbnail else 'No'}")
                    print(f"      Has description: {'Yes' if result.description else 'No'}")
                else:
                    print(f"   ❌ Not found")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
    finally:
        db.close()


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("BOOKSTOR API INTEGRATION TEST SUITE")
    print("="*60)
    
    # Test individual APIs
    await test_openlibrary()
    await test_google_books()
    
    # Test integration manager
    await test_api_integration_manager()
    
    # Test multiple ISBNs
    await test_different_isbns()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

