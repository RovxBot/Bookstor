"""
Test ISBN lookup with API integration manager
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from src.database import SessionLocal
from src.services.api_integration_manager import api_integration_manager

async def test_isbn_lookup():
    """Test ISBN lookup"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("TESTING ISBN LOOKUP")
        print("="*60)
        
        # Test ISBN
        isbn = "9780316769174"
        print(f"\nLooking up ISBN: {isbn}")
        
        # Call the API integration manager
        result = await api_integration_manager.search_by_isbn(isbn, db)
        
        if result:
            print(f"\n✅ Book found!")
            print(f"Title: {result.title}")
            print(f"Authors: {result.authors}")
            print(f"Publisher: {result.publisher}")
            print(f"ISBN: {result.isbn}")
        else:
            print(f"\n❌ Book not found")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_isbn_lookup())

