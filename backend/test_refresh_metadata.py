"""
Test the refresh metadata endpoint
"""
import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.api_integration_manager import api_integration_manager
from src.database import SessionLocal
from src.models import Book


async def test_refresh_metadata():
    """Test refreshing metadata for existing books"""
    print("\n" + "="*60)
    print("TESTING METADATA REFRESH")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Get a book with ISBN
        book = db.query(Book).filter(Book.isbn.isnot(None)).first()
        
        if not book:
            print("   ⚠️  No books with ISBN found in database")
            return
        
        print(f"\nBook: {book.title}")
        print(f"ISBN: {book.isbn}")
        print(f"Current Authors: {book.authors}")
        print(f"Current Description: {book.description[:100] if book.description else 'None'}...")
        print(f"Current Thumbnail: {book.thumbnail}")
        
        # Fetch updated metadata
        print(f"\nFetching updated metadata from APIs...")
        book_info = await api_integration_manager.search_by_isbn(book.isbn, db)
        
        if book_info:
            print(f"   ✅ SUCCESS - Retrieved metadata:")
            print(f"   Title: {book_info.title}")
            print(f"   Authors: {', '.join(book_info.authors) if book_info.authors else 'None'}")
            print(f"   Publisher: {book_info.publisher}")
            print(f"   Published: {book_info.published_date}")
            print(f"   Pages: {book_info.page_count}")
            print(f"   Description: {book_info.description[:100] if book_info.description else 'None'}...")
            print(f"   Thumbnail: {book_info.thumbnail}")
            print(f"   Series: {book_info.series_name}")
            print(f"   Edition: {book_info.edition}")
            print(f"   Format: {book_info.book_format}")
            
            # Show what would be updated
            print(f"\n   Fields that would be updated:")
            if book_info.title and book_info.title != book.title:
                print(f"   - Title: '{book.title}' → '{book_info.title}'")
            if book_info.authors:
                new_authors = ", ".join(book_info.authors)
                if new_authors != book.authors:
                    print(f"   - Authors: '{book.authors}' → '{new_authors}'")
            if book_info.description and book_info.description != book.description:
                print(f"   - Description: Updated")
            if book_info.thumbnail and book_info.thumbnail != book.thumbnail:
                print(f"   - Thumbnail: Updated")
            if book_info.page_count and book_info.page_count != book.page_count:
                print(f"   - Page Count: {book.page_count} → {book_info.page_count}")
        else:
            print(f"   ❌ FAILED: No metadata found")
        
        # Test another book without ISBN
        book_no_isbn = db.query(Book).filter(Book.isbn.is_(None)).first()
        if book_no_isbn:
            print(f"\n" + "="*60)
            print(f"Testing book without ISBN: {book_no_isbn.title}")
            print(f"Current Authors: {book_no_isbn.authors}")
            
            # Try searching by title
            search_query = book_no_isbn.title
            if book_no_isbn.authors:
                search_query += f" {book_no_isbn.authors.split(',')[0]}"
            
            print(f"Searching for: '{search_query}'")
            results = await api_integration_manager.search_by_title(search_query, db, max_results=1)
            
            if results:
                print(f"   ✅ SUCCESS - Found match:")
                print(f"   Title: {results[0].title}")
                print(f"   Authors: {', '.join(results[0].authors) if results[0].authors else 'None'}")
                print(f"   ISBN: {results[0].isbn}")
            else:
                print(f"   ⚠️  No results found")
        
    finally:
        db.close()


async def main():
    await test_refresh_metadata()


if __name__ == "__main__":
    asyncio.run(main())

